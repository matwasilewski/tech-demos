#!/usr/bin/env python3
"""
MongoDB Beanie Test CLI (Click version)

This command-line interface orchestrates the full demonstration flow:
1. Connect to MongoDB.
2. Drop the chosen database (clean slate).
3. Insert the sample documents defined in :pyfile:`mongo_connection.py`.
4. Dump everything back to stdout so the user can verify the contents.

All heavy lifting lives in :pyfile:`MongoDBManager` – this script is only
a thin, user-friendly wrapper implemented with *click*.
"""

from __future__ import annotations

import asyncio
import sys
from typing import NoReturn

import click

from mongo_connection import MongoDBManager


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--host",
    default="localhost",
    show_default=True,
    help="MongoDB hostname.",
)
@click.option(
    "--port",
    default=27019,
    show_default=True,
    type=int,
    help="MongoDB port.",
)
@click.option(
    "--database",
    "--db",
    default="evidence-db-test",
    show_default=True,
    help="Database name to wipe and populate.",
)
def cli(host: str, port: int, database: str) -> NoReturn:  # noqa: D401 (Click style)
    """Run the demo with the given *HOST*, *PORT* and *DATABASE*."""

    async def _run() -> None:
        manager = MongoDBManager(host=host, port=port, database=database)
        try:
            await manager.run_demo()
        except Exception as exc:  # pragma: no cover – top-level exception barrier
            click.echo(f"❌ Demo failed: {exc}", err=True)
            sys.exit(1)

    asyncio.run(_run())


if __name__ == "__main__":
    cli()