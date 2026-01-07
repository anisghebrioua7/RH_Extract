import time
import requests
from typing import Dict, Any, Optional, List
from config import Config


class LuccaClient:
    def __init__(self):
        self.base_url = Config.LUCCA_API_URL.rstrip("/")
        # Headers
        self.headers = {
            "Authorization": f"lucca application={Config.LUCCA_API_TOKEN}",
            "Accept": "application/json",
        }
        # Timeout global pour les requêtes HTTP
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
        # Certains endpoints peuvent retourner 404
        if response.status_code == 404 and allow_404:
            return {"data": {"items": []}}
        # Toute autre réponse non OK est considérée comme une erreur
        if not response.ok:
            raise RuntimeError(
                f"Lucca API error {response.status_code} on {url}: {response.text}"
            )

        return response.json()

    # Récupère la liste des utilisateurs avec un sous-ensemble de champs
    def get_employees(self) -> Dict[str, Any]:
        
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
    
    # Récupère l'ensemble des départements
    def get_departments(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v3/departments")

    #___Stratégie d'extraction : récupération des IDs puis détails_______

    # Récupère la liste de tous les identifiants utilisateurs
    def get_all_user_ids(self) -> List[int]:
 
        resp = self._request("GET", "/api/v3/users")
        items = resp.get("data", {}).get("items", [])
        return [u["id"] for u in items if "id" in u]

    # Récupère les informations détaillées d'un utilisateur à partir de son ID.
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

                # retry sur 429 (rate limit)
                if r.status_code == 429:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue

                # retry sur erreurs serveur (>=500)
                if r.status_code >= 500:
                    wait = 2 ** attempt
                    time.sleep(wait)
                    continue

                # Autres erreurs HTTP
                if not r.ok:
                    raise RuntimeError(
                        f"Lucca API error {r.status_code} on {url}: {r.text}"
                    )

                payload = r.json()
                return payload.get("data", payload)

            except requests.exceptions.ReadTimeout:
                # Timeout réseau : retry avec backoff
                wait = 2 ** attempt
                time.sleep(wait)
                continue

        # Après plusieurs échecs, on ignore l'utilisateur pour garantir la continuité du job
        print(f"[WARN] User {user_id} ignoré après {max_retries} tentatives")
        return None

