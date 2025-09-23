"""Ray Serve + FastAPI entrypoint for the HouGarden Finder search service."""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from hydra import compose, initialize_config_dir
from omegaconf import DictConfig, OmegaConf
from pydantic import BaseModel
from ray import serve
import ray
from ray.serve.schema import LoggingConfig
from dotenv import load_dotenv

from hou_garden.agents.tools.query_hougarden_info import (
    _query_hougarden_info_core,
    resolve_location_ids,
)

CONFIG_NAME = "apps/hougarden-finder.yaml"
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = PACKAGE_ROOT.parent
_CONFIG_CANDIDATES = [PACKAGE_ROOT / "configs", _REPO_ROOT / "configs"]
for _candidate in _CONFIG_CANDIDATES:
    if _candidate.exists():
        CONFIG_DIR = _candidate
        break
else:
    raise FileNotFoundError("Could not locate configs directory for HouGarden Finder")

APP_LOGGER = logging.getLogger("hougarden_finder")
SERVE_LOGGER = logging.getLogger("ray.serve")

for logger in (APP_LOGGER, SERVE_LOGGER):
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)

fastapi_app = FastAPI(title="HouGarden Finder API")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_env_files(extra_files: Optional[List[str]] = None) -> None:
    root = CONFIG_DIR.parent
    files = [root / ".env", root / ".env.secret"]
    if extra_files:
        files.extend(Path(f) for f in extra_files)
    for file in files:
        try:
            load_dotenv(file, override=False)
        except Exception:
            continue


class GenerateRequest(BaseModel):
    """Incoming payload for property search."""

    query: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class GenerateResponse(BaseModel):
    """Response returned to the caller."""

    result: Dict[str, Any]
    latency_ms: int


class LocationResponse(BaseModel):
    """Response payload for location resolution."""

    keyword: str
    param: Optional[str]
    location_id: Optional[str]


def _load_app_config(config_name: str = CONFIG_NAME) -> DictConfig:
    """Load Hydra config for the server deployment."""

    with initialize_config_dir(version_base="1.3", config_dir=str(CONFIG_DIR)):
        return compose(config_name=config_name)


@serve.deployment
@serve.ingress(fastapi_app)
class HouGardenFinderService:
    """Ray Serve deployment that wraps the HouGarden search tool."""

    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        search_cfg = cfg.app.search
        self.default_page = int(search_cfg.get("default_page", 1))
        self.default_page_size = int(search_cfg.get("default_page_size", 10))
        self.default_sort = int(search_cfg.get("default_sort", 0))
        self.logger = APP_LOGGER

    async def _run_search(
        self,
        query: str,
        page: Optional[int],
        page_size: Optional[int],
        sort: Optional[int],
        surrounding: Optional[int],
    ) -> Dict[str, Any]:
        def _blocking_call() -> Dict[str, Any]:
            kwargs: Dict[str, Any] = {}
            if page is not None:
                kwargs["page"] = page
            if page_size is not None:
                kwargs["page_size"] = page_size
            if sort is not None:
                kwargs["sort"] = sort
            if surrounding is not None:
                kwargs["surrounding"] = surrounding
            return _query_hougarden_info_core(query=query, **kwargs)

        return await asyncio.to_thread(_blocking_call)

    @fastapi_app.get("/health")
    async def health(self) -> Dict[str, str]:
        return {"status": "ok"}

    @fastapi_app.post("/generate", response_model=GenerateResponse)
    async def generate(self, payload: GenerateRequest) -> GenerateResponse:
        context = dict(payload.context or {})

        def _maybe_int(value: Any) -> Optional[int]:
            try:
                if value is None or value == "":
                    return None
                return int(value)
            except (TypeError, ValueError):
                return None

        raw_page = context.pop("page", None)
        page = _maybe_int(raw_page)
        if page is not None:
            page = max(1, page)

        raw_page_size = context.pop("page_size", None)
        page_size = _maybe_int(raw_page_size)
        if page_size is not None:
            page_size = max(1, page_size)

        raw_sort = context.pop("sort", None)
        sort = _maybe_int(raw_sort)

        raw_surrounding = context.pop("surrounding", None)
        surrounding = _maybe_int(raw_surrounding)
        if surrounding not in (0, 1):
            surrounding = None

        user_msg = payload.query.strip()
        if context:
            ctx_lines = [f"{k}: {v}" for k, v in context.items()]
            user_msg = f"{user_msg}\n\n补充条件:\n" + "\n".join(ctx_lines)

        start = time.perf_counter()
        log_msg = (
            "Incoming request user_id=%s page=%s size=%s sort=%s surrounding=%s"
            % (
                payload.user_id,
                page if page is not None else "auto",
                page_size if page_size is not None else "auto",
                sort if sort is not None else "auto",
                surrounding if surrounding is not None else "auto",
            )
        )
        self.logger.info(log_msg)
        SERVE_LOGGER.info(log_msg)
        try:
            data = await self._run_search(
                user_msg,
                page=page,
                page_size=page_size,
                sort=sort,
                surrounding=surrounding,
            )
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - start) * 1000)
            err_msg = f"Search failed user_id={payload.user_id} latency={latency_ms}ms error={exc}"
            self.logger.exception(err_msg)
            SERVE_LOGGER.error(err_msg)
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        latency_ms = int((time.perf_counter() - start) * 1000)
        if isinstance(data, dict) and not data.get("ok", True):
            warn_msg = (
                f"Search returned ok=false user_id={payload.user_id} latency={latency_ms}ms "
                f"error={data.get('error')}"
            )
            self.logger.warning(warn_msg)
            SERVE_LOGGER.warning(warn_msg)
            raise HTTPException(status_code=503, detail=data.get("error", "search_failed"))

        success_msg = (
            f"Search success user_id={payload.user_id} latency={latency_ms}ms "
            f"items={len(data.get('items', [])) if isinstance(data, dict) else 'n/a'}"
        )
        self.logger.info(success_msg)
        SERVE_LOGGER.info(success_msg)
        return GenerateResponse(result=data, latency_ms=latency_ms)

    @fastapi_app.get("/location", response_model=LocationResponse)
    async def resolve_location(self, keyword: str) -> LocationResponse:
        keyword = (keyword or "").strip()
        if not keyword:
            raise HTTPException(status_code=400, detail="keyword_required")

        start = time.perf_counter()
        try:
            param, loc_id = await asyncio.to_thread(resolve_location_ids, keyword)
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - start) * 1000)
            self.logger.exception("Location resolve failed after %sms", latency_ms)
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        latency_ms = int((time.perf_counter() - start) * 1000)
        loc_msg = (
            f"Resolved location keyword={keyword} param={param} "
            f"id={loc_id} latency={latency_ms}ms"
        )
        self.logger.info(loc_msg)
        SERVE_LOGGER.info(loc_msg)
        if not (param and loc_id):
            raise HTTPException(status_code=404, detail="location_not_found")

        return LocationResponse(keyword=keyword, param=param, location_id=loc_id)


def run(
    config_name: str = CONFIG_NAME,
    env_files: Optional[List[str]] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    address: Optional[str] = None,
) -> None:
    """Convenience helper to start the Ray Serve deployment."""

    load_env_files(env_files)
    required_keys = ["OPENAI_API_KEY", "HG_AUTH_TOKEN"]
    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Use --env-file 或设置系统环境变量。"
        )
    cfg = _load_app_config(config_name)
    server_cfg = cfg.app.server

    resolved_host = host if host is not None else server_cfg.host
    resolved_port = int(port) if port is not None else int(server_cfg.port)

    ray_actor_opts = OmegaConf.to_object(server_cfg.get("ray_actor_options", {})) or {}
    if "num_cpus" in ray_actor_opts:
        try:
            ray_actor_opts["num_cpus"] = float(ray_actor_opts["num_cpus"])
        except (TypeError, ValueError):
            raise RuntimeError("HGFINDER_NUM_CPUS 必须是数字，例如 1 或 2.5")

    try:
        num_replicas = int(server_cfg.num_replicas)
    except (TypeError, ValueError):
        raise RuntimeError("HGFINDER_NUM_REPLICAS 必须是整数")

    deployment = HouGardenFinderService.options(
        name=server_cfg.deployment_name,
        num_replicas=num_replicas,
        ray_actor_options=ray_actor_opts,
    ).bind(cfg)

    try:
        serve.shutdown()
    except Exception:
        pass

    if address:
        ray.init(address=address, namespace="serve", ignore_reinit_error=True)
    else:
        ray.init(namespace="serve", ignore_reinit_error=True)

    serve.start(
        detached=False,
        http_options={
            "host": resolved_host,
            "port": resolved_port,
        },
        logging_config={
            "encoding": "JSON",
            "log_level": "INFO",
        },
    )
    serve.run(
        deployment,
        route_prefix=server_cfg.route_prefix,
        logging_config=LoggingConfig(encoding="JSON", log_level="INFO"),
    )

    print("HouGarden Finder is running at http://%s:%s%s" % (resolved_host, resolved_port, server_cfg.route_prefix))
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Shutting down HouGarden Finder...")
        serve.shutdown()


if __name__ == "__main__":
    run()
