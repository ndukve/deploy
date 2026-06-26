"""Config"""

from __future__ import annotations
from typing import ClassVar, Optional, Union
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RESTConfig(BaseSettings):
    """Config for for the wrapper REST api"""

    port: int = Field(description="bind port", default=8887)
    addr: str = Field(description="bind address", default="0.0.0.0")  # nosec
    cfssl: str = Field(
        description="cfssl executable Union[Path, str]", default="/usr/bin/cfssl"
    )
    data_path: Union[Path, str] = Field(
        description="Where is CFSSL persistent data",
        alias="CFSSL_PERSISTENT_FOLDER",
        default="/data/persistent",
    )
    cacrt: Union[Path, str] = Field(
        alias="RUN_INTER_CA",
        description="CA cert to use in commands",
        default="/data/persistent/inter-ca.pem",
    )
    cakey: Union[Path, str] = Field(
        alias="RUN_INTER_CA_KEY",
        description="CA key to use in commands",
        default="/data/persistent/inter-ca_key.pem",
    )
    rootcacrt: Union[Path, str] = Field(
        alias="RUN_CA",
        description="Root CA cert to use in commands",
        default="/data/persistent/ca.pem",
    )
    rootcakey: Union[Path, str] = Field(
        alias="RUN_CA_KEY",
        description="root CA key to use in commands",
        default="/data/persistent/init_ca-key.pem",
    )
    conf: Union[Path, str] = Field(
        alias="RUN_CA_CFSSL_CONF",
        description="Path to the db config file",
        default="/data/persistent/root_ca_cfssl.json",
    )
    dbconf: Union[Path, str] = Field(
        alias="RUN_DB_CONFIG",
        description="Path to the db config file",
        default="/data/persistent/db.json",
    )
    respcrt: Union[Path, str] = Field(
        alias="RUN_OCSP_CERT",
        description="Responder cert to use",
        default="/data/persistent/ocsp.pem",
    )
    respkey: Union[Path, str] = Field(
        alias="RUN_OCSP_KEY",
        description="Responder key to use",
        default="/data/persistent/ocsp_key.pem",
    )
    crl: Union[Path, str] = Field(
        description="Location to dump the DER CRL to, .PEM version will also be created",
        default="/ca_public/crl.der",
    )
    crl_lifetime: str = Field(description="Lifetime to pass to CFSSL", default="1800s")
    # OCSP responder rounds the response nextupdate in funky ways so less than 1h will lead to weird results
    ocsp_lifetime: str = Field(description="Lifetime to pass to CFSSL", default="1h")
    crl_refresh: int = Field(
        description="Interval to dump CRL via out background task", default=900
    )

    ci: bool = Field(default=False, alias="CI", description="Are we running in CI")
    model_config = SettingsConfigDict(
        env_prefix="or_", env_file=".env", extra="ignore", env_nested_delimiter="__"
    )
    _singleton: ClassVar[Optional[RESTConfig]] = None

    @classmethod
    def singleton(cls) -> RESTConfig:
        """Return singleton"""
        if not RESTConfig._singleton:
            RESTConfig._singleton = RESTConfig()
        RESTConfig._singleton.data_path = Path(RESTConfig._singleton.data_path)
        RESTConfig._singleton.cacrt = Path(RESTConfig._singleton.cacrt)
        RESTConfig._singleton.cakey = Path(RESTConfig._singleton.cakey)
        RESTConfig._singleton.rootcacrt = Path(RESTConfig._singleton.rootcacrt)
        RESTConfig._singleton.rootcakey = Path(RESTConfig._singleton.rootcakey)
        RESTConfig._singleton.conf = Path(RESTConfig._singleton.conf)
        RESTConfig._singleton.dbconf = Path(RESTConfig._singleton.dbconf)
        RESTConfig._singleton.respcrt = Path(RESTConfig._singleton.respcrt)
        RESTConfig._singleton.respkey = Path(RESTConfig._singleton.respkey)
        RESTConfig._singleton.crl = Path(RESTConfig._singleton.crl)
        return RESTConfig._singleton
