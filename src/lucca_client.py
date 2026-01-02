import requests
from typing import Dict, Any, Optional
from config import Config


class LuccaClient:
    """
    Client HTTP pour l'API Lucca.
    Responsable uniquement des appels réseau.
    """

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

    # =====================
    # Endpoints Lucca
    # =====================

    def get_employees(self):
        """
        Récupère les utilisateurs avec les champs RH nécessaires.
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
                "rolePrincipal",
                "userWorkCycles",
            ])
        }

        return self._request(
            method="GET",
            endpoint="/api/v3/users",
            params=params,
        )

    def get_departments(self) -> Dict[str, Any]:
        """
        Récupère l'ensemble des départements.
        """
        return self._request(
            method="GET",
            endpoint="/api/v3/departments",
        )
