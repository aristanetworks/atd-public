import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from ruamel.yaml import YAML

from models import CvpStatus
from state import app_state

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cvp_proxy")

ATD_ACCESS_PATH = "/etc/atd/ACCESS_INFO.yaml"
PROBE_INTERVAL = 30
RETRY_INTERVAL = 15


def load_access_info() -> dict:
    with open(ATD_ACCESS_PATH, "r") as f:
        return YAML().load(f)


async def cvp_connection_loop():
    client = app_state.cvp_client

    while True:
        try:
            access_info = load_access_info()
        except FileNotFoundError:
            logger.info("ACCESS_INFO not available yet, retrying in %ds", RETRY_INTERVAL)
            await asyncio.sleep(RETRY_INTERVAL)
            continue

        cvp_host = access_info["nodes"]["cvp"][0]["ip"]
        username = access_info["login_info"]["jump_host"]["user"]
        password = access_info["login_info"]["jump_host"]["pw"]

        try:
            await client.connect(cvp_host, username, password)
            logger.info("CVP connection established, entering monitoring loop")

            while True:
                await asyncio.sleep(PROBE_INTERVAL)
                if not await client.health_probe():
                    logger.warning("CVP health probe failed, will reconnect")
                    break
        except Exception as e:
            logger.info("CVP not ready (%s), retrying in %ds", e, RETRY_INTERVAL)
            client.status = CvpStatus.WAITING
            await asyncio.sleep(RETRY_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(cvp_connection_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="ATD CVP Proxy", version="0.1.0", lifespan=lifespan)

from routers import health, inventory, configlets, assignments, enrollment, cvp_status

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(inventory.router, prefix="/api/v1", tags=["inventory"])
app.include_router(configlets.router, prefix="/api/v1", tags=["configlets"])
app.include_router(assignments.router, prefix="/api/v1", tags=["assignments"])
app.include_router(enrollment.router, prefix="/api/v1", tags=["enrollment"])
app.include_router(cvp_status.router, prefix="/api/v1", tags=["cvp"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8880)
