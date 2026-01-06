import time
import requests
from typing import Dict, Any, Optional, List
from config import Config


class LuccaClient:
    def __init__(self):
        self.base_url = Config.LUCCA_API_URL.rstrip("/")
        self.headers = {
            "Authorization": f"lucca application={Config.LUCCA_API_TOKEN}",
            "Accept": "application/json",
        }
        self.timeout = Config.REQUEST_TIMEOUT

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        allow_404: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"

        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )

        if response.status_code == 404 and allow_404:
            return {"data": {"items": []}}

        if not response.ok:
            raise RuntimeError(
                f"Lucca API error {response.status_code} on {url}: {response.text}"
            )

        return response.json()

    def get_employees(self) -> Dict[str, Any]:
        """
        Récupère les utilisateurs avec les champs utiles (liste).
        """
        params = {
            "fields": ",".join([
                "id",
                "displayName",
                "firstName",
                "lastName",
                "mail",
                "employeeNumber",
                "dtContractStart",
                "dtContractEnd",
                "departmentId",
            ])
        }
        return self._request("GET", "/api/v3/users", params=params)

    def get_departments(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v3/departments")

    # =========================
    # NOUVEAU : stratégie "ids puis détails"
    # =========================

    def get_all_user_ids(self) -> List[int]:
        """
        Récupère tous les IDs depuis /users.
        (Note: si l'API est paginée, il faudra itérer sur les pages.)
        """
        resp = self._request("GET", "/api/v3/users")
        items = resp.get("data", {}).get("items", [])
        return [u["id"] for u in items if "id" in u]

    def get_user_details(self, user_id: int, max_retries: int = 5):
        endpoint = f"/api/v3/users/{user_id}"
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries):
            try:
                r = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                )

                if r.status_code == 429:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue

                if r.status_code >= 500:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue

                if not r.ok:
                    raise RuntimeError(
                        f"Lucca API error {r.status_code} on {url}: {r.text}"
                    )

                payload = r.json()
                return payload.get("data", payload)

            except requests.exceptions.ReadTimeout:
                wait = 2 ** attempt
                time.sleep(wait)
                continue

        # Après retries → on SKIP l'utilisateur
        print(f"[WARN] User {user_id} ignoré après {max_retries} tentatives")
        return None

