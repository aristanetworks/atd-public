import requests
import time
import logging

logger = logging.getLogger("proxy_client")


class ProxyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/api/v1{path}"

    def get_health(self) -> dict:
        resp = self.session.get(self._url("/health"), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def is_cvp_ready(self) -> bool:
        try:
            resp = self.session.get(self._url("/ready"), timeout=10)
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    def wait_for_cvp(self, poll_interval: int = 15):
        logger.info("Waiting for CloudVision to become operational...")
        while True:
            try:
                health = self.get_health()
                cvp_status = health.get("cvp_status", "UNKNOWN")
                if cvp_status == "READY":
                    logger.info(
                        "CloudVision is operational (v%s)",
                        health.get("cvp_version", "?"),
                    )
                    return
                elapsed = health.get("uptime_seconds", 0)
                logger.info(
                    "CVP status: %s — %s (%ds elapsed)",
                    cvp_status,
                    health.get("message", ""),
                    elapsed,
                )
            except requests.ConnectionError:
                logger.info("CVP proxy not yet reachable...")
            time.sleep(poll_interval)

    def get_inventory(self) -> dict:
        resp = self.session.get(self._url("/inventory"), timeout=30)
        resp.raise_for_status()
        return resp.json()["devices"]

    def wait_for_devices(self, count: int, timeout: int = 300) -> dict:
        resp = self.session.post(
            self._url("/inventory/wait"),
            json={"count": count, "timeout": timeout},
            timeout=timeout + 30,
        )
        resp.raise_for_status()
        return resp.json()["devices"]

    def sync_configlets(self, configlets: list[dict]) -> dict:
        resp = self.session.post(
            self._url("/configlets/sync"),
            json={"configlets": configlets},
            timeout=600,
        )
        resp.raise_for_status()
        return resp.json()

    def apply_assignments(
        self, device_assignments: dict, global_configlets: list[str]
    ) -> dict:
        resp = self.session.post(
            self._url("/assignments/apply"),
            json={
                "device_assignments": device_assignments,
                "global_configlets": global_configlets,
            },
            timeout=600,
        )
        resp.raise_for_status()
        return resp.json()

    def init_tags(self) -> dict:
        resp = self.session.post(self._url("/tags/init"), timeout=120)
        resp.raise_for_status()
        return resp.json()

    def create_enrollment_token(self, duration: str = "86400s") -> dict:
        resp = self.session.post(
            self._url("/enrollment/token"),
            json={"duration": duration},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def get_enrollment_status(self) -> dict:
        resp = self.session.get(self._url("/enrollment/status"), timeout=30)
        resp.raise_for_status()
        return resp.json()
