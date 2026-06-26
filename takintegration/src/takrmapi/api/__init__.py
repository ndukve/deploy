"""Api endpoints"""

from fastapi.routing import APIRouter

from .usercrud import router as usercrud_router
from .usercrud import test_router as testing_router  # REMOVE ME
from .clientinfo import router as clientinfo_router
from .admininfo import router as admininfo_router
from .healthcheck import router as healthcheck_router
from .description import router as description_router
from .instructions import router as instructions_router
from .tak_datapackage import router as takdatapackage_router
from .tak_missionpackage import router as takmissionpackage_router

from .description import router_v2 as description_router_v2
from .description import router_v2_admin as description_admin_router
from .userinfo import router as userinfo_router

from .tak_missionpackage import ephemeral_router as ephemeral_takmissionpackage_router

all_routers = APIRouter()
all_routers.include_router(testing_router, prefix="/users", tags=["users"])  # REMOVE ME
all_routers.include_router(usercrud_router, prefix="/users", tags=["users"])
all_routers.include_router(clientinfo_router, prefix="/clients", tags=["clients"])
all_routers.include_router(admininfo_router, prefix="/admins", tags=["admins"])
all_routers.include_router(healthcheck_router, prefix="/healthcheck", tags=["healthcheck"])
all_routers.include_router(description_router, prefix="/description", tags=["description"])
all_routers.include_router(instructions_router, prefix="/instructions", tags=["instructions"])
all_routers.include_router(takdatapackage_router, prefix="/tak-datapackages", tags=["tak-datapackages"])
all_routers.include_router(takmissionpackage_router, prefix="/tak-missionpackages", tags=["tak-missionpackages"])


all_routers_v2 = APIRouter()
all_routers_v2.include_router(description_router_v2, prefix="/description", tags=["description"])
all_routers_v2.include_router(description_admin_router, prefix="/admin/description", tags=["description"])
all_routers_v2.include_router(userinfo_router, prefix="/clients", tags=["clients"])


all_routers_ephemeral_v1 = APIRouter()
all_routers_ephemeral_v1.include_router(
    ephemeral_takmissionpackage_router, prefix="/tak-missionpackages", tags=["ephemeral-tak-missionpackages"]
)
