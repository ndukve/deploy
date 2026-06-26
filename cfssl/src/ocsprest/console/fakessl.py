"""fake cfssl for unit testing"""

import logging

import click
from libadvian.logging import init_logging

from ocsprest import __version__

LOGGER = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option(
    "-l",
    "--loglevel",
    help="Python log level, 10=DEBUG, 20=INFO, 30=WARNING, 40=CRITICAL",
    default=30,
)
@click.option(
    "-v", "--verbose", count=True, help="Shorthand for info/debug loglevel (-v/-vv)"
)
def cligrp(loglevel: int, verbose: int) -> None:
    """Fake CFSSL command for unit testing"""
    if verbose == 1:
        loglevel = 20
    if verbose >= 2:
        loglevel = 10
    init_logging(loglevel)
    LOGGER.setLevel(loglevel)


@cligrp.command(name="crl")
def crl() -> None:
    """generate a new Certificate Revocation List from Database"""
    raise NotImplementedError()


@cligrp.command(name="serve")
def serve() -> None:
    """set up a HTTP server handles CF SSL requests"""
    raise NotImplementedError()


@cligrp.command(name="gencert")
def gencert() -> None:
    """generate a new key and signed certificate"""
    raise NotImplementedError()


@cligrp.command(name="gencsr")
def gencsr() -> None:
    """generate a csr from a private key with existing CSR json specification or certificate"""
    raise NotImplementedError()


@cligrp.command(name="ocspsign")
def ocspsign() -> None:
    """signs an OCSP response for a given CA, cert, and status."""
    raise NotImplementedError()


@cligrp.command(name="certinfo")
def certinfo() -> None:
    """output certinfo about the given cert"""
    raise NotImplementedError()


@cligrp.command(name="sign")
def sign() -> None:
    """signs a client cert with a host name by a given CA and CA key"""
    raise NotImplementedError()


@cligrp.command(name="version")
def version() -> None:
    """print out the version of CF SSL"""
    click.echo(__version__)


@cligrp.command(name="gencrl")
def gencrl() -> None:
    """generate a new Certificate Revocation List"""
    raise NotImplementedError()


@cligrp.command(name="ocsprefresh")
def ocsprefresh() -> None:
    """refreshes the ocsp_responses table"""
    raise NotImplementedError()


@cligrp.command(name="print-defaults")
def print_defaults() -> None:
    """print default configurations that can be used as a template"""
    raise NotImplementedError()


@cligrp.command(name="revoke")
def revoke() -> None:
    """revoke a certificate in the certificate store"""
    raise NotImplementedError()


@cligrp.command(name="bundle")
def bundle() -> None:
    """create a certificate bundle that contains the client cert"""
    raise NotImplementedError()


@cligrp.command(name="ocspserve")
def ocspserve() -> None:
    """set up an HTTP server that handles OCSP requests from either a file or directly from a database (see RFC 5019)"""
    raise NotImplementedError()


@cligrp.command(name="scan")
def scan() -> None:
    """scan a host for issues"""
    raise NotImplementedError()


@cligrp.command(name="genkey")
def genkey() -> None:
    """generate a new key and CSR"""
    raise NotImplementedError()


@cligrp.command(name="selfsign")
def selfsign() -> None:
    """generate a new self-signed key and signed certificate"""
    raise NotImplementedError()


@cligrp.command(name="info")
def info() -> None:
    """get info about a remote signer"""
    raise NotImplementedError()


@cligrp.command(name="ocspdump")
def ocspdump() -> None:
    """generates a series of concatenated OCSP responses"""
    raise NotImplementedError()


def fakessl_cli() -> None:
    """cli entrypoint"""
    init_logging(logging.WARNING)
    cligrp()
