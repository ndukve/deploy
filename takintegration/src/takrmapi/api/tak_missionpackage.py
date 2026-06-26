"""Endpoint to deliver user missionpackages from templates/tak_missionpackage"""

from pathlib import Path
import logging
import base64
import binascii
import urllib.parse
import time
import os
import json
import secrets
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from libpvarki.middleware.mtlsheader import MTLSHeader
from libpvarki.schemas.product import UserCRUDRequest

from takrmapi import config
from takrmapi.takutils import tak_helpers
from takrmapi.takutils.tak_pkg_helpers import TAKDataPackage, TAKPackageZip

LOGGER = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])

ephemeral_router = APIRouter()


def hash_from_str(hash_from: str, hmac_key: bytes) -> str:
    """Return checksum string from given string"""
    # ct_digest = hashes.Hash(hashes.SHA256())
    ct_digest = hmac.HMAC(hmac_key, hashes.SHA256())
    ct_digest.update(hash_from.encode("ascii"))
    ct_dig = ct_digest.finalize()
    ct_dig_str = binascii.hexlify(ct_dig).decode()

    return ct_dig_str


@router.post("/client-zip/{variant}.zip")
async def return_tak_zip(user: UserCRUDRequest, variant: str, background_tasks: BackgroundTasks) -> FileResponse:
    """Return TAK client zip file proxied from rm api"""

    localuser = tak_helpers.UserCRUD(user)
    if not localuser:
        raise HTTPException(status_code=404, detail="User data not found")

    target_pkg = await create_mission_package(localuser, variant, background_tasks)

    return FileResponse(
        path=target_pkg.zip_path,
        media_type="application/zip",
        filename=f"{localuser.callsign}_{variant}.zip",
    )


async def create_mission_package(
    localuser: tak_helpers.UserCRUD, variant: str, background_tasks: BackgroundTasks
) -> TAKDataPackage:
    """Create mission package from template"""
    walk_dir = Path(config.TAK_MISSIONPKG_TEMPLATES_FOLDER) / "default" / variant

    if not walk_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Variant '{variant}' not found")

    tak_missionpkg = TAKPackageZip(localuser)
    target_pkg = TAKDataPackage(template_path=walk_dir, template_type="mission")
    await tak_missionpkg.create_zip_bundles(datapackages=[target_pkg])

    if not target_pkg.zip_path or not target_pkg.zip_path.is_file():
        raise HTTPException(status_code=500, detail="Failed to generate ZIP")

    background_tasks.add_task(tak_missionpkg.helpers.remove_tmp_dir, target_pkg.zip_tmp_folder)

    return target_pkg


@router.post("/ephemeral/{variant}.zip")
async def return_ephemeral_dl_link(user: UserCRUDRequest, variant: str) -> dict[str, str]:
    """Return an ephemeral download link to get the TAK client zip file"""
    localuser = tak_helpers.UserCRUD(user)
    if not localuser:
        raise HTTPException(status_code=404, detail="User data not found")
    request_time = int(time.time())

    encrypted_url = generate_encrypted_ephemeral_url_fragment(user.callsign, user.uuid, variant, request_time)

    # ATAK seems to take offense if the package file name is the same between
    # requests, so we add a random token to the filename.
    nonce = secrets.token_hex(8)

    ephemeral_url = (
        f"https://{config.read_tak_fqdn()}:{config.PRODUCT_HTTPS_EPHEMERAL_PORT}/"
        f"ephemeral/api/v1/tak-missionpackages/ephemeral/"
        f"{urllib.parse.quote_plus(encrypted_url)}/{config.read_deployment_name()}_{nonce}_{variant}.zip"
    )

    LOGGER.info("Returning ephemeral url: %s", ephemeral_url)

    return {"ephemeral_url": ephemeral_url}


@ephemeral_router.get("/ephemeral/{ephemeral_str}/{zipfile_name}.zip")
async def return_ephemeral_tak_zip(ephemeral_str: str, background_tasks: BackgroundTasks) -> FileResponse:
    """Return the TAK client zip file using an ephemeral link"""
    LOGGER.info("Got ephemeral url fragment: %s", ephemeral_str)

    callsign, user_uuid, variant = parse_encrypted_ephemeral_url_fragment(ephemeral_str)

    localuser: tak_helpers.UserCRUD = tak_helpers.UserCRUD(
        UserCRUDRequest(uuid=user_uuid, callsign=callsign, x509cert="")
    )
    if not localuser:
        raise HTTPException(status_code=404, detail="User data not found")

    target_pkg = await create_mission_package(localuser, variant, background_tasks)

    return FileResponse(
        path=target_pkg.zip_path,
        media_type="application/zip",
        filename=f"{localuser.callsign}_{config.read_deployment_name()}_{variant}.zip",
    )


def generate_encrypted_ephemeral_url_fragment(
    user_callsign: str, user_uuid: str, variant: str, request_time: float
) -> str:
    """Return encrypted ephemeral url"""
    plaintext_str: str = json.dumps(
        {"callsign": user_callsign, "uuid": user_uuid, "variant": variant, "request_time": request_time}
    )
    iv = os.urandom(12)
    encryptor = Cipher(algorithms.AES(TAKDataPackage.get_ephemeral_aes_key()), modes.GCM(iv)).encryptor()
    user_payload: bytes = encryptor.update(plaintext_str.encode("ascii")) + encryptor.finalize()
    user_payload_b64: str = base64.b64encode(user_payload).decode("ascii")
    iv_b64: str = base64.b64encode(iv).decode("ascii")
    payload_digest: str = hash_from_str(user_payload_b64 + iv_b64, TAKDataPackage.get_ephemeral_hmac_key())
    encode: str = base64.b64encode(
        json.dumps(
            {
                "payload_b64": user_payload_b64,
                "iv_b64": iv_b64,
                "digest": payload_digest,
            }
        ).encode("ascii")
    ).decode("ascii")

    return encode


def parse_encrypted_ephemeral_url_fragment(ephemeral_str: str) -> tuple[str, str, str]:
    """Parse and decrypt ephemeral url and return callsign, user uuid and variant.

    Verify that the ephemeral link is not expired and that the checksum matches.
    """
    try:
        e_decoded = base64.b64decode(ephemeral_str.encode("ascii")).decode("ascii")
    except binascii.Error as exc:
        LOGGER.info("Unable to decode base64 to string. Possible malformed query.")
        LOGGER.debug(exc)
        raise HTTPException(status_code=404, detail="User data not found") from exc

    ephemeral_json = json.loads(e_decoded)

    payload_digest: str = hash_from_str(
        ephemeral_json["payload_b64"] + ephemeral_json["iv_b64"], TAKDataPackage.get_ephemeral_hmac_key()
    )
    if payload_digest != ephemeral_json["digest"]:
        LOGGER.info(
            "Checksum mismatch. Calculated: {}, but got from response: {}".format(
                payload_digest, ephemeral_json["digest"]
            )
        )
        raise HTTPException(status_code=404, detail="User data not found")

    iv: bytes = base64.b64decode(ephemeral_json["iv_b64"].encode("ascii"))
    user_payload: bytes = base64.b64decode(ephemeral_json["payload_b64"].encode("ascii"))

    decryptor = Cipher(algorithms.AES(TAKDataPackage.get_ephemeral_aes_key()), modes.GCM(iv)).encryptor()
    decrypted_payload = decryptor.update(user_payload) + decryptor.finalize()

    try:
        decrypted_json = json.loads(decrypted_payload.decode("ascii"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        LOGGER.exception("Decryption failure. It could be someone is trying something nasty.")
        raise HTTPException(status_code=404, detail="User data not found") from exc

    variant = decrypted_json["variant"]
    callsign = decrypted_json["callsign"]
    user_uuid = decrypted_json["uuid"]
    link_generation_time = decrypted_json["request_time"]
    if link_generation_time + 300 < int(time.time()):
        LOGGER.audit("Ephemeral link has expired.")  # type: ignore[attr-defined]
        raise HTTPException(status_code=404, detail="User data not found")

    LOGGER.debug("Got the following data in ephemeral user payload: {}".format(decrypted_json))

    return callsign, user_uuid, variant
