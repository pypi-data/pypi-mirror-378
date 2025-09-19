"""CLI utilities for HouGarden Finder deployment and testing."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

import click
import requests

from hou_garden.apps.hougarden_finder import run as run_server, load_env_files


def _parse_context(pairs: tuple[str, ...]) -> Dict[str, object]:
    context: Dict[str, object] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Invalid context format '{pair}', expected key=value")
        key, value = pair.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise click.BadParameter("Context key cannot be empty")
        # Try to coerce into int/float/bool
        lowered = value.lower()
        if lowered in {"true", "false"}:
            context[key] = lowered == "true"
            continue
        try:
            context[key] = int(value)
            continue
        except ValueError:
            pass
        try:
            context[key] = float(value)
            continue
        except ValueError:
            pass
        context[key] = value
    return context


@click.group()
def cli() -> None:
    """HouGarden Finder command line tools."""


@cli.command()
@click.option("--env-file", "env_files", multiple=True, type=click.Path(dir_okay=False, exists=True), help="Additional .env files to load before starting.")
@click.option("--config", default="apps/hougarden-finder.yaml", show_default=True, help="Hydra config name to load.")
@click.option("--host", default=None, help="Override HTTP host.")
@click.option("--port", type=int, default=None, help="Override HTTP port.")
@click.option("--address", default=None, help="Ray cluster address, e.g. 'auto' or 'ray://host:10001'.")
@click.option("--num-replicas", type=int, default=None, help="Set HGFINDER_NUM_REPLICAS before start.")
@click.option("--num-cpus", type=float, default=None, help="Set HGFINDER_NUM_CPUS before start.")
def serve(env_files, config, host, port, address, num_replicas, num_cpus) -> None:
    """Start the HouGarden Finder server."""
    if num_replicas is not None:
        os.environ["HGFINDER_NUM_REPLICAS"] = str(num_replicas)
    if num_cpus is not None:
        os.environ["HGFINDER_NUM_CPUS"] = str(num_cpus)
    extra_env = [str(Path(f).resolve()) for f in env_files]
    run_server(
        config_name=config,
        env_files=extra_env if extra_env else None,
        host=host,
        port=port,
        address=address,
    )

# alias for convenience (`hougarden-finder server`)
cli.add_command(serve, name="server")


@cli.command()
@click.option("--url", default="http://127.0.0.1:8701/finder/generate", show_default=True, help="Target endpoint URL.")
@click.option("--query", prompt=True, help="Natural language query for property search.")
@click.option("--context", "context_pairs", multiple=True, help="Context key=value pairs. Repeat to add multiple entries.")
@click.option("--env-file", "env_files", multiple=True, type=click.Path(dir_okay=False, exists=True), help="Optional env files to load before sending request.")
@click.option("--timeout", type=float, default=30.0, show_default=True, help="Request timeout in seconds.")
def query(url, query, context_pairs, env_files, timeout) -> None:
    """Send a test request to HouGarden Finder."""
    extra_env = [str(Path(f).resolve()) for f in env_files]
    load_env_files(extra_env if extra_env else None)
    context = _parse_context(context_pairs)
    payload = {"query": query}
    if context:
        payload["context"] = context
    session = requests.Session()
    session.trust_env = False
    try:
        resp = session.post(url, json=payload, timeout=timeout, proxies={})
        resp.raise_for_status()
    except requests.HTTPError as err:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise click.ClickException(f"Request failed ({resp.status_code}): {detail}") from err
    except requests.RequestException as err:
        raise click.ClickException(str(err)) from err

    try:
        data = resp.json()
    except Exception:
        click.echo(resp.text)
        return
    click.echo(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli()
