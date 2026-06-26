"""Handle manifests"""

import json
import logging
import uuid
from pathlib import Path
from typing import cast

from libadvian.binpackers import uuid_to_b64

from .config import MWConfig, ProductSettings
from .hosts_helper import generate_hosts_bash_script, write_product_hosts_script
from .jwt import PUBDIR_MODE, check_create_keypair, get_issuer

LOGGER = logging.getLogger(__name__)


async def copy_jwt_pub(manifest_dir: Path) -> None:
    """Copy miniwerks JWT public key to the manifest dir"""
    _, mw_jwt_pub = await check_create_keypair()
    LOGGER.debug(f"manifest_dir={manifest_dir}")
    pubkeypath = manifest_dir / "publickeys" / "kraftwerk.pub"
    pubdir = pubkeypath.parent
    pubdir.mkdir(parents=True, exist_ok=True)
    pubdir.chmod(PUBDIR_MODE)
    LOGGER.debug(f"pubkeypath={pubkeypath}, exists: {pubkeypath.exists()}")
    if pubkeypath.exists():
        return
    pubkeypath.write_bytes(mw_jwt_pub.read_bytes())
    LOGGER.info(f"Wrote {pubkeypath}")


def get_product_config(productname: str) -> ProductSettings | None:
    """Get normalized product config"""
    config = MWConfig.singleton()
    product_config = getattr(config, productname, None)
    if not product_config:
        LOGGER.error(f"No config for {productname}")
        return None
    product_config = cast(ProductSettings, product_config)
    if not product_config.api_host:
        product_config.api_host = productname
    if not product_config.user_host:
        product_config.user_host = productname
    return product_config


async def create_rasenmaeher_manifest() -> Path:
    """create manifest for RASENMAEHER"""
    config = MWConfig.singleton()
    manifest_path = config.manifests_base / "rasenmaeher" / "kraftwerk-rasenmaeher-init.json"
    manifest_dir = manifest_path.parent
    manifest_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.debug(f"manifest_dir={manifest_dir}")
    await copy_jwt_pub(manifest_dir)
    # Write the hosts helper script
    script_path = config.manifests_base / "rasenmaeher" / "hosts_script.sh"
    script_path.write_text(generate_hosts_bash_script(), encoding="utf-8")
    script_path.chmod(0o754)  # -rwxr-xr--
    LOGGER.info(f"Wrote {script_path}")

    if manifest_path.exists():
        LOGGER.info(f"{manifest_path} already exists, not overwriting")
        return manifest_path

    manifest = {
        "dns": config.domain,
        "deployment": config.domain.split(".")[0],
        "products": cast(dict[str, dict[str, str]], {}),
    }
    for productname in config.product_manifest_paths:
        product_config = get_product_config(productname)
        if not product_config:
            LOGGER.error(f"No config for {productname}")
            continue
        apihost = product_config.api_host
        userhost = product_config.user_host
        manifest["products"][productname] = {  # type: ignore[index]   # false positive
            "api": f"https://{apihost}.{config.domain}:{product_config.api_port}{product_config.api_base}",
            "uri": f"https://{userhost}.{config.domain}:{product_config.user_port}{product_config.user_base}",
            "certcn": f"{productname}.{config.domain}",
        }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    LOGGER.info(f"Wrote {manifest_path}")
    return manifest_path


async def create_product_manifest(productname: str) -> Path:
    """create manisfest for given product"""
    config = MWConfig.singleton()
    manifest_path = config.manifests_base / productname / "kraftwerk-init.json"
    manifest_dir = manifest_path.parent
    manifest_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.debug(f"manifest_dir={manifest_dir}")
    await copy_jwt_pub(manifest_dir)

    if manifest_path.exists():
        LOGGER.info(f"{manifest_path} already exists, not overwriting")
        return manifest_path

    issuer = await get_issuer()
    issuer.config.lifetime = 3600 * 24  # 24h
    token = issuer.issue(
        {
            "sub": f"{productname}.{config.domain}",
            "csr": True,
            "nonce": uuid_to_b64(uuid.uuid4()),
        }
    )
    rm_port = config.rasenmaeher.api_port
    rm_uri = f"https://{config.domain}:{rm_port}/" if rm_port != 443 else f"https://{config.domain}/"
    mtls_uri = rm_uri.replace("https://", "https://mtls.")
    product_config = get_product_config(productname)
    if not product_config:
        LOGGER.error(f"No config for {productname}")
        return manifest_path
    apihost = product_config.api_host
    userhost = product_config.user_host
    manifest = {
        "deployment": config.domain.split(".")[0],
        "rasenmaeher": {
            "init": {"base_uri": rm_uri, "csr_jwt": token},
            "mtls": {"base_uri": mtls_uri},
            "certcn": "rasenmaeher",
        },
        "product": {
            "dns": f"{productname}.{config.domain}",
            "api": f"https://{apihost}.{config.domain}:{product_config.api_port}{product_config.api_base}",
            "uri": f"https://{userhost}.{config.domain}:{product_config.user_port}{product_config.user_base}",
        },
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    LOGGER.info(f"Wrote {manifest_path}")
    return manifest_path


async def create_all_product_manifests() -> list[Path]:
    """Handle all products"""
    config = MWConfig.singleton()
    ret = []
    for productname in config.product_manifest_paths:
        product_config = getattr(config, productname, None)
        if not product_config:
            LOGGER.error(f"No config for {productname}")
            continue
        ret.append(await create_product_manifest(productname))
        write_product_hosts_script(productname)
    return ret
