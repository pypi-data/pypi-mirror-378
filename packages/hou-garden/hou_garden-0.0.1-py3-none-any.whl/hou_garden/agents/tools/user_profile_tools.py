"""
User profiling tools for HouGarden with PostgreSQL first, DuckDB fallback.

Tools:
- user_profile_query: fetch the latest profile JSON for a user_id.
- user_profile_upsert_async: enqueue an async upsert of a profile JSON.
- user_profile_generate_and_upsert: run embedded profiling Agent then upsert.
- Queue helpers for producer/consumer pipelines (Ray ready).

Design notes
- Primary storage: PostgreSQL (set USER_PROFILE_PG_DSN). If not set, fallback to DuckDB.
- Store the entire profile as JSON/JSONB with versioning and timestamps.
- Async upsert uses a background thread to avoid blocking the LLM/tool call.
"""

from __future__ import annotations

from agno.tools import tool
import os
import json
import threading
import time
import datetime as dt
from typing import Any, Dict, Optional, List, Tuple
import uuid
from dotenv import load_dotenv
import traceback


def _log_error(context: str, err: Exception) -> None:
    try:
        path = os.getenv("HOU_AGENT_LOG", "hou_agent_errors.log")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{_now_iso()}] {context}: {err}\n")
            f.write(traceback.format_exc())
            f.write("\n")
    except Exception:
        pass


def _now_iso() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load_env_once() -> None:
    try:
        load_dotenv(".env.secret", override=False)
        load_dotenv(".env", override=False)
    except Exception:
        pass


def _get_db_path() -> str:
    # Allow overriding via env; default to app-local path under tmp/mem
    db_path = os.getenv(
        "USER_PROFILE_DB",
        os.path.join("tmp", "mem", "ask-hougarden", "user_profiles.duckdb"),
    )
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return db_path

def _ensure_schema_duckdb(con) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT,
            version BIGINT,
            profile_json JSON,
            updated_at TIMESTAMP
        );
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profile_events (
            user_id TEXT,
            event_type TEXT,
            payload JSON,
            created_at TIMESTAMP
        );
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profile_jobs (
            job_id TEXT PRIMARY KEY,
            user_id TEXT,
            text TEXT,
            merge BOOLEAN,
            status TEXT,
            tries INTEGER,
            error TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        );
        """
    )


def _ensure_schema_postgres(con) -> None:
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT NOT NULL,
            version BIGINT NOT NULL,
            profile_json JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (user_id, version)
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profile_events (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profile_jobs (
            job_id UUID PRIMARY KEY,
            user_id TEXT NOT NULL,
            text TEXT NOT NULL,
            merge BOOLEAN NOT NULL DEFAULT TRUE,
            status TEXT NOT NULL DEFAULT 'pending',
            tries INTEGER NOT NULL DEFAULT 0,
            error TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
    )
    con.commit()


def _connect_duckdb():
    import duckdb  # lazy import to avoid hard dependency at import-time

    db_path = _get_db_path()
    con = duckdb.connect(db_path)
    _ensure_schema_duckdb(con)
    return con


def _pg_dsn() -> Optional[str]:
    _load_env_once()
    return os.getenv("USER_PROFILE_PG_DSN") or os.getenv("DATABASE_URL")


def _connect_postgres():
    dsn = _pg_dsn()
    if not dsn:
        raise RuntimeError("missing_postgres_dsn")
    try:
        # Prefer psycopg (v3), fallback to psycopg2
        try:
            import psycopg as psy
            con = psy.connect(dsn)
            _ensure_schema_postgres(con)
            return con, "psycopg3"
        except Exception:
            import psycopg2 as psy2  # type: ignore
            con = psy2.connect(dsn)
            _ensure_schema_postgres(con)
            return con, "psycopg2"
    except Exception as e:
        _log_error("postgres_connect_failed", e)
        raise RuntimeError(f"postgres_connect_failed: {e}")


def _connect_db():
    dsn = _pg_dsn()
    if dsn:
        con, impl = _connect_postgres()
        return ("pg", con, impl)
    return ("duck", _connect_duckdb(), None)


def _load_latest_profile(con, user_id: str) -> tuple[Optional[dict], Optional[int]]:
    # DuckDB path
    try:
        cur = con.execute(
            """
            SELECT profile_json, version
            FROM user_profiles
            WHERE user_id = ?
            ORDER BY version DESC
            LIMIT 1
            """,
            [user_id],
        )
        row = cur.fetchone()
        if not row:
            return None, None
        raw, ver = row
        try:
            prof = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            prof = None
        return prof, int(ver) if ver is not None else None
    except Exception:
        # Postgres path
        cur = con.cursor()
        cur.execute(
            """
            SELECT profile_json::text, version
            FROM user_profiles
            WHERE user_id = %s
            ORDER BY version DESC
            LIMIT 1
            """,
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None, None
        raw, ver = row
        try:
            prof = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            prof = None
        return prof, int(ver) if ver is not None else None


def _merge_profiles(existing: Optional[dict], incoming: dict) -> dict:
    # Shallow merge: only overwrite with non-empty values
    if not existing:
        return dict(incoming)
    merged = dict(existing)
    for k, v in incoming.items():
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        merged[k] = v
    return merged


def _upsert_worker(user_id: str, profile_json: str, merge: bool) -> None:
    try:
        db_kind, con, *_ = ("duck", None, None)
        kind, con, _ = _connect_db()
        incoming: dict = json.loads(profile_json)
        existing, last_ver = _load_latest_profile(con, user_id)
        new_profile = _merge_profiles(existing, incoming) if merge else incoming
        new_version = (last_ver or 0) + 1
        now = _now_iso()

        try:
            # Try DuckDB first
            con.execute(
                """
                INSERT INTO user_profiles(user_id, version, profile_json, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                [user_id, new_version, json.dumps(new_profile, ensure_ascii=False), now],
            )
            con.execute(
                """
                INSERT INTO user_profile_events(user_id, event_type, payload, created_at)
                VALUES (?, 'upsert', ?, ?)
                """,
                [user_id, json.dumps(incoming, ensure_ascii=False), now],
            )
        except Exception:
            # Postgres
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO user_profiles(user_id, version, profile_json, updated_at)
                VALUES (%s, %s, %s::jsonb, NOW())
                """,
                (user_id, new_version, json.dumps(new_profile, ensure_ascii=False)),
            )
            cur.execute(
                """
                INSERT INTO user_profile_events(user_id, event_type, payload)
                VALUES (%s, 'upsert', %s::jsonb)
                """,
                (user_id, json.dumps(incoming, ensure_ascii=False)),
            )
            con.commit()
        finally:
            try:
                con.close()
            except Exception:
                pass
    except Exception:
        # Silent fail in worker; production code should log this.
        pass


def _upsert_profile_sync(user_id: str, profile: Dict[str, Any], merge: bool) -> Dict[str, Any]:
    """Synchronous upsert used by the generate-and-upsert tool when sync=True."""
    kind, con, _ = _connect_db()
    try:
        existing, last_ver = _load_latest_profile(con, user_id)
        new_profile = _merge_profiles(existing, profile) if merge else profile
        new_version = (last_ver or 0) + 1
        now = _now_iso()
        try:
            # DuckDB path
            con.execute(
                """
                INSERT INTO user_profiles(user_id, version, profile_json, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                [user_id, new_version, json.dumps(new_profile, ensure_ascii=False), now],
            )
            con.execute(
                """
                INSERT INTO user_profile_events(user_id, event_type, payload, created_at)
                VALUES (?, 'upsert', ?, ?)
                """,
                [user_id, json.dumps(profile, ensure_ascii=False), now],
            )
        except Exception:
            # Postgres path
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO user_profiles(user_id, version, profile_json, updated_at)
                VALUES (%s, %s, %s::jsonb, NOW())
                """,
                (user_id, new_version, json.dumps(new_profile, ensure_ascii=False)),
            )
            cur.execute(
                """
                INSERT INTO user_profile_events(user_id, event_type, payload)
                VALUES (%s, 'upsert', %s::jsonb)
                """,
                (user_id, json.dumps(profile, ensure_ascii=False)),
            )
            con.commit()
        return {"version": new_version, "updated_at": now, "profile": new_profile}
    finally:
        try:
            con.close()
        except Exception:
            pass


@tool(
    name="user_profile_upsert_async",
    description=(
        "接收 LLM 生成的用户画像 JSON（字符串），异步入库（Postgres 优先，DuckDB 兜底）；"
        "返回立即确认，不阻塞当前对话。参数：user_id, profile_json(str), merge(bool)."
    ),
)
def user_profile_upsert_async(user_id: str, profile_json: str, merge: bool = True) -> Dict[str, Any]:
    """
    Enqueue an async upsert of user profile.

    - user_id: 用户唯一标识
    - profile_json: LLM 生成的画像 JSON 字符串（与 UserProfileResponse 字段对齐即可）
    - merge: True 则与已有画像做浅合并（非空覆盖），False 则直接替换
    """
    if not user_id or not isinstance(user_id, str):
        return {"ok": False, "error": "invalid_user_id"}
    try:
        # Validate JSON early (non-blocking if large)
        json.loads(profile_json)
    except Exception as e:
        return {"ok": False, "error": f"invalid_json: {e}"}

    job_id = f"upsert-{user_id}-{int(time.time()*1000)}"
    th = threading.Thread(target=_upsert_worker, args=(user_id, profile_json, merge), daemon=True)
    th.start()
    # Try to set permissive permissions for the DB file directory (best-effort)
    try:
        db_path = _get_db_path()
        os.chmod(os.path.dirname(db_path), 0o777)
        if os.path.exists(db_path):
            os.chmod(db_path, 0o666)
    except Exception:
        pass

    return {
        "ok": True,
        "status": "queued",
        "job_id": job_id,
        "user_id": user_id,
        "db": _get_db_path(),
        "queued_at": _now_iso(),
    }


# =========================
# Queue-based Producer/Consumer API (for Ray workers)
# =========================

def _jobs_enqueue(user_id: str, text: str, merge: bool = True) -> str:
    kind, con, _ = _connect_db()
    try:
        now = _now_iso()
        job_id = str(uuid.uuid4())
        try:
            con.execute(
                """
                INSERT INTO user_profile_jobs(job_id, user_id, text, merge, status, tries, error, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'pending', 0, NULL, ?, ?)
                """,
                [job_id, user_id, text, merge, now, now],
            )
        except Exception:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO user_profile_jobs(job_id, user_id, text, merge, status, tries, error, created_at, updated_at)
                VALUES (%s, %s, %s, %s, 'pending', 0, NULL, NOW(), NOW())
                """,
                (job_id, user_id, text, merge),
            )
            con.commit()
        return job_id
    finally:
        try:
            con.close()
        except Exception:
            pass


def _jobs_next_pending(limit: int = 1) -> List[Dict[str, Any]]:
    kind, con, _ = _connect_db()
    try:
        try:
            cur = con.execute(
                """
                SELECT job_id, user_id, text, merge, status, tries
                FROM user_profile_jobs
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT ?
                """,
                [limit],
            )
            rows = cur.fetchall() or []
        except Exception:
            cur = con.cursor()
            cur.execute(
                """
                SELECT job_id, user_id, text, merge, status, tries
                FROM user_profile_jobs
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall() or []
        jobs: List[Dict[str, Any]] = []
        for r in rows:
            jobs.append(
                {
                    "job_id": r[0],
                    "user_id": r[1],
                    "text": r[2],
                    "merge": bool(r[3]),
                    "status": r[4],
                    "tries": int(r[5] or 0),
                }
            )
        return jobs
    finally:
        try:
            con.close()
        except Exception:
            pass


def _jobs_mark(job_id: str, status: str, error: Optional[str] = None, inc_try: bool = False) -> None:
    kind, con, _ = _connect_db()
    try:
        now = _now_iso()
        try:
            if inc_try:
                con.execute(
                    """
                    UPDATE user_profile_jobs
                    SET status = ?, error = ?, tries = COALESCE(tries,0)+1, updated_at = ?
                    WHERE job_id = ?
                    """,
                    [status, error, now, job_id],
                )
            else:
                con.execute(
                    """
                    UPDATE user_profile_jobs
                    SET status = ?, error = ?, updated_at = ?
                    WHERE job_id = ?
                    """,
                    [status, error, now, job_id],
                )
        except Exception:
            cur = con.cursor()
            if inc_try:
                cur.execute(
                    """
                    UPDATE user_profile_jobs
                    SET status = %s, error = %s, tries = COALESCE(tries,0)+1, updated_at = NOW()
                    WHERE job_id = %s
                    """,
                    (status, error, job_id),
                )
            else:
                cur.execute(
                    """
                    UPDATE user_profile_jobs
                    SET status = %s, error = %s, updated_at = NOW()
                    WHERE job_id = %s
                    """,
                    (status, error, job_id),
                )
            con.commit()
    finally:
        try:
            con.close()
        except Exception:
            pass


def _jobs_get(job_id: str) -> Optional[Dict[str, Any]]:
    kind, con, _ = _connect_db()
    try:
        try:
            cur = con.execute(
                """
                SELECT job_id, user_id, text, merge, status, tries, error, created_at, updated_at
                FROM user_profile_jobs
                WHERE job_id = ?
                LIMIT 1
                """,
                [job_id],
            )
            r = cur.fetchone()
        except Exception:
            cur = con.cursor()
            cur.execute(
                """
                SELECT job_id, user_id, text, merge, status, tries, error, created_at, updated_at
                FROM user_profile_jobs
                WHERE job_id = %s
                LIMIT 1
                """,
                (job_id,),
            )
            r = cur.fetchone()
        if not r:
            return None
        return {
            "job_id": r[0],
            "user_id": r[1],
            "text": r[2],
            "merge": bool(r[3]),
            "status": r[4],
            "tries": int(r[5] or 0),
            "error": r[6],
            "created_at": str(r[7]) if r[7] is not None else None,
            "updated_at": str(r[8]) if r[8] is not None else None,
        }
    finally:
        try:
            con.close()
        except Exception:
            pass


@tool(
    name="user_profile_enqueue_generate",
    description=(
        "将画像生成任务写入队列（Postgres 优先，DuckDB 兜底），立即返回 job_id；"
        "由独立 Worker（例如 Ray）消费并写入画像。参数：user_id, text, merge(True)。"
    ),
)
def user_profile_enqueue_generate(user_id: str, text: str, merge: bool = True) -> Dict[str, Any]:
    if not user_id or not isinstance(user_id, str):
        return {"ok": False, "error": "invalid_user_id"}
    if not isinstance(text, str) or not text.strip():
        return {"ok": False, "error": "empty_text"}
    job_id = _jobs_enqueue(user_id=user_id, text=text, merge=merge)
    return {"ok": True, "job_id": job_id}


@tool(
    name="user_profile_job_status",
    description="查询队列任务状态（pending/running/done/failed），返回 {ok, found, job}.",
)
def user_profile_job_status(job_id: str) -> Dict[str, Any]:
    if not job_id:
        return {"ok": False, "error": "invalid_job_id"}
    job = _jobs_get(job_id)
    if job is None:
        return {"ok": True, "found": False}
    return {"ok": True, "found": True, "job": job}


def user_profile_generate_and_upsert_core(
    user_id: str,
    text: str,
    merge: bool = True,
    sync: bool = True,
) -> Dict[str, Any]:
    """
    Generate a user profile from free text using the configured profiling Agent,
    then upsert it to the DB (Postgres preferred, DuckDB fallback). When sync=False,
    the upsert runs in a background thread.
    """
    if not user_id or not isinstance(user_id, str):
        return {"ok": False, "error": "invalid_user_id"}
    if not isinstance(text, str) or not text.strip():
        return {"ok": False, "error": "empty_text"}

    try:
        # Lazy import to avoid circular deps and speed up module import
        from hou_garden.agents.user_profiling.agent import user_profiling_agent  # type: ignore
    except Exception as e:
        _log_error("load_agent_failed@import_user_profiling_agent", e)
        return {"ok": False, "error": f"load_agent_failed: {e}"}

    try:
        resp = user_profiling_agent.run(text, user_id=user_id)
        content = getattr(resp, "content", resp)
        # Normalize to dict
        profile: Dict[str, Any]
        try:
            # pydantic BaseModel
            model_dump = getattr(content, "model_dump", None)
            if callable(model_dump):
                profile = model_dump()
            elif isinstance(content, dict):
                profile = content
            elif isinstance(content, str):
                profile = json.loads(content)
            else:
                # best-effort fallback
                profile = {"raw": str(content)}
        except Exception:
            # as text JSON parse fallback
            try:
                profile = json.loads(str(content))
            except Exception:
                profile = {"raw": str(content)}
    except Exception as e:
        _log_error("agent_run_failed@user_profiling_agent.run", e)
        return {"ok": False, "error": f"agent_run_failed: {e}"}

    if sync:
        try:
            res = _upsert_profile_sync(user_id=user_id, profile=profile, merge=merge)
            # Best-effort permissions
            try:
                db_path = _get_db_path()
                os.chmod(os.path.dirname(db_path), 0o777)
                if os.path.exists(db_path):
                    os.chmod(db_path, 0o666)
            except Exception:
                pass
            return {"ok": True, "mode": "sync", "user_id": user_id, **res}
        except Exception as e:
            _log_error("upsert_failed@sync_profile_upsert", e)
            return {"ok": False, "error": f"upsert_failed: {e}"}
    else:
        try:
            th = threading.Thread(
                target=lambda: _upsert_profile_sync(user_id=user_id, profile=profile, merge=merge),
                daemon=True,
            )
            th.start()
            return {
                "ok": True,
                "mode": "async",
                "user_id": user_id,
                "queued_at": _now_iso(),
            }
        except Exception as e:
            _log_error("enqueue_failed@async_profile_upsert", e)


@tool(
    name="user_profile_generate_and_upsert",
    description=(
        "使用内置用户画像Agent对输入文本进行画像提取，并写入数据库（Postgres 优先，DuckDB 兜底）。"
        "参数：user_id, text, merge(True=浅合并), sync(True=同步写入)。"
    ),
)
def user_profile_generate_and_upsert(
    user_id: str,
    text: str,
    merge: bool = True,
    sync: bool = True,
) -> Dict[str, Any]:
    # Agno Tool wrapper; for direct Python use, prefer calling the _core variant
    return user_profile_generate_and_upsert_core(user_id=user_id, text=text, merge=merge, sync=sync)


def user_profile_query_core(user_id: str, keys: Optional[List[str]] = None) -> Dict[str, Any]:
    if not user_id:
        return {"ok": False, "error": "invalid_user_id"}
    try:
        kind, con, _ = _connect_db()
    except Exception as e:
        _log_error("db_open_failed@user_profile_query", e)
        return {"ok": False, "error": f"db_open_failed: {e}", "dsn": _pg_dsn(), "db": _get_db_path()}

    try:
        prof, ver = _load_latest_profile(con, user_id)
        if prof is None:
            return {"ok": True, "found": False, "user_id": user_id}
        # obtain updated_at for that version
        try:
            cur = con.execute(
                """
                SELECT updated_at FROM user_profiles
                WHERE user_id = ? AND version = ?
                LIMIT 1
                """,
                [user_id, ver],
            )
            row = cur.fetchone()
        except Exception:
            cur = con.cursor()
            cur.execute(
                """
                SELECT updated_at FROM user_profiles
                WHERE user_id = %s AND version = %s
                LIMIT 1
                """,
                (user_id, ver),
            )
            row = cur.fetchone()
        updated_at = row[0] if row else None
        if keys:
            filtered = {k: prof.get(k) for k in keys}
        else:
            filtered = prof
        return {
            "ok": True,
            "found": True,
            "user_id": user_id,
            "version": ver,
            "updated_at": str(updated_at) if updated_at is not None else None,
            "profile": filtered,
        }
    finally:
        try:
            con.close()
        except Exception:
            pass


@tool(
    name="user_profile_query",
    description=("按 user_id 查询最新用户画像（Postgres 优先，DuckDB 兜底）；返回 {ok, found, version, updated_at, profile}。"),
)
def user_profile_query(user_id: str, keys: Optional[List[str]] = None) -> Dict[str, Any]:
    # Agno Tool wrapper; for direct Python use, prefer calling the _core variant
    return user_profile_query_core(user_id=user_id, keys=keys)
