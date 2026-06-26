"""CLI entrypoints for miniwerk"""

import asyncio
import logging
from typing import Any

import click
from libadvian.logging import init_logging

from miniwerk import __version__
from miniwerk.config import MWConfig
from miniwerk.lewrap import get_le_certs
from miniwerk.manifests import create_all_product_manifests, create_rasenmaeher_manifest
from miniwerk.mkcwrap import get_mk_certs

LOGGER = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option("-l", "--loglevel", help="Python log level, 10=DEBUG, 20=INFO, 30=WARNING, 40=CRITICAL", default=30)
@click.option("-v", "--verbose", count=True, help="Shorthand for info/debug loglevel (-v/-vv)")
def cligrp(loglevel: int, verbose: int) -> None:
    """Minimal KRAFTWERK amulation to be able to run a RASENMAEHER+products deployment on any VM"""
    if verbose == 1:
        loglevel = 20
    if verbose >= 2:
        loglevel = 10
    init_logging(loglevel)
    LOGGER.setLevel(loglevel)


@cligrp.command(name="config")
def dump_config() -> None:
    """Show the resolved config as JSON"""
    click.echo(MWConfig.singleton().model_dump_json())


@cligrp.command(name="certs")
@click.pass_context
def do_certs(ctx: Any) -> None:
    """Get and/or renew certs based on configuration"""

    async def call() -> int:
        """Do the call"""
        config = MWConfig.singleton()
        if config.extcert:
            LOGGER.info("EXTernal certificate handling specified")
        elif config.mkcert:
            await get_mk_certs()
        else:
            await get_le_certs()
        return 0

    ctx.exit(asyncio.run(call()))


@cligrp.command(name="manifests")
@click.pass_context
def create_manifests(ctx: Any) -> None:
    """Create manifests"""

    async def call() -> int:
        """Do the call"""
        await create_rasenmaeher_manifest()
        await create_all_product_manifests()
        return 0

    ctx.exit(asyncio.run(call()))


@cligrp.command(name="init")
@click.pass_context
def do_full_init(ctx: Any) -> None:
    """Create manifests, get certs, everything that is needed"""

    async def call() -> int:
        """Do the call"""
        config = MWConfig.singleton()
        await create_rasenmaeher_manifest()
        await create_all_product_manifests()
        if config.extcert:
            LOGGER.info("EXTernal certificate handling specified")
        elif config.mkcert:
            await get_mk_certs()
        else:
            await get_le_certs()
        return 0

    ctx.exit(asyncio.run(call()))


def miniwerk_cli() -> None:
    """cli entrypoint"""
    init_logging(logging.WARNING)
    cligrp()
