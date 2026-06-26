"""TAK specific schemas"""

from pydantic import Field, Extra
from pydantic.main import BaseModel  # pylint: disable=E0611 # false positive


class UserTAKPackageZipRequest(BaseModel):  # pylint: disable=too-few-public-methods
    """Request to get user mission zip"""

    uuid: str = Field(description="RASENMAEHER UUID for this user")
    callsign: str = Field(description="Callsign of the user")
    x509cert: str = Field(description="Certificate encoded with CFSSL conventions (newlines escaped)")
    private_key: str = Field(description="Users private key that will be added to .p12 (newlines escaped)")
    missionpkg: str = Field(default="example", description="Mission package name, default 'example'")

    class Config:  # pylint: disable=too-few-public-methods
        """Example values for schema"""

        extra = Extra.forbid
        schema_extra = {
            "examples": [
                {
                    "uuid": "3ede23ae-eff2-4aa8-b7ef-7fac68c39988",
                    "callsign": "ROTTA01a",
                    "x509cert": "-----BEGIN CERTIFICATE-----\\nMIIEwjCC...\\n-----END CERTIFICATE-----\\n",
                    "private_key": "-----BEGIN PRIVATE KEY-----\\n(...)",  # pragma: allowlist secret
                    "missionpkg": "example",
                },
            ]
        }
