import requests
from datetime import datetime
from typing import Optional

DEFAULT_BASE_URL = "https://api.cronpulse.com"  # TODO: confirm actual production URL

class CronPulse:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')

    def create_monitor(self, name: str, interval: int, email: str, expires_at: datetime):
        response = requests.post(
            f"{self.base_url}/monitors",
            json={
                "name": name,
                "interval": interval,
                "email": email,
                "expires_at": expires_at.isoformat(),
            },
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10,
        )
        response.raise_for_status()
        monitor_id = response.json()["id"]
        return Monitor(monitor_id, client=self)

class Monitor:
    def __init__(self, monitor_id: str, client: CronPulse):
        self.monitor_id = monitor_id
        self._client = client

    @property
    def api_key(self) -> str:
        return self._client.api_key

    @property
    def base_url(self) -> str:
        return self._client.base_url

    def ping(self):
        response = requests.post(
            f"{self.base_url}/monitors/{self.monitor_id}/ping",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10,
        )
        response.raise_for_status()

    def delete(self):
        response = requests.delete(
            f"{self.base_url}/monitors/{self.monitor_id}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10,
        )
        response.raise_for_status()
