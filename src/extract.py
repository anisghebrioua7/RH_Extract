import json
import csv
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, date

from lucca_client import LuccaClient
from config import Config


# =====================================================
# Utils fichiers
# =====================================================

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_csv(path: Path, data: List[Dict[str, Any]]) -> None:
    if not data:
        return

    fieldnames = sorted({k for row in data for k in row.keys()})

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in data:
            flat_row = {
                k: json.dumps(v, ensure_ascii=False)
                if isinstance(v, (dict, list))
                else v
                for k, v in row.items()
            }
            writer.writerow(flat_row)


def write_output(base_path_no_ext: Path, data: List[Dict[str, Any]]) -> None:
    fmt = getattr(Config, "OUTPUT_FORMAT", "json").lower()
    if fmt == "csv":
        write_csv(base_path_no_ext.with_suffix(".csv"), data)
    else:
        write_json(base_path_no_ext.with_suffix(".json"), data)


# =====================================================
# Utils dates
# =====================================================

def _parse_iso_date(d: Optional[str]) -> Optional[date]:
    if not d:
        return None
    return datetime.fromisoformat(d).date()


# =====================================================
# Extraction USERS (essential)
# =====================================================

def extract_essential_user(user: Dict[str, Any]) -> Dict[str, Any]:
    today = date.today()

    dt_start = user.get("dtContractStart")
    dt_end = user.get("dtContractEnd")

    start_date = _parse_iso_date(dt_start)
    end_date = _parse_iso_date(dt_end)

    if start_date and start_date > today:
        status = "FUTURE"
    elif end_date is None or end_date >= today:
        status = "ACTIVE"
    else:
        status = "ENDED"

    department_id = user.get("departmentId", user.get("departmentID"))
    manager_id = user.get("managerId", user.get("managerID"))
    legal_entity_id = user.get("legalEntityId", user.get("legalEntityID"))

    return {
        "employee_id": user.get("id"),
        "first_name": user.get("firstName"),
        "last_name": user.get("lastName"),
        "display_name": user.get("displayName"),
        "civil_title": user.get("civilTitle"),
        "gender": user.get("gender"),
        "birth_date": user.get("birthDate"),
        "professional_email": user.get("mail"),
        "personal_email": user.get("personalEmail"),
        "login": user.get("login"),
        "employee_number": user.get("employeeNumber"),

        "department_id": department_id,
        "department_name": (user.get("department") or {}).get("name"),

        "manager_id": manager_id,
        "manager_name": (user.get("manager") or {}).get("name"),

        "legal_entity_id": legal_entity_id,
        "legal_entity_name": (user.get("legalEntity") or {}).get("name"),

        "contract_start_date": dt_start,
        "contract_end_date": dt_end,
        "job_title": user.get("jobTitle"),

        "calendar_id": user.get("calendarId"),
        "calendar_name": (user.get("calendar") or {}).get("name"),

        "status": status,
    }


# =====================================================
# Extraction CONTRACTS
# RÈGLE MÉTIER :
# Un contrat = un salarié avec dtContractStart
# =====================================================

def extract_contracts_from_user(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Génère exactement UN contrat par salarié
    basé uniquement sur dtContractStart / dtContractEnd.
    """
    today = date.today()
    contracts = []

    start_date = _parse_iso_date(user.get("dtContractStart"))
    end_date = _parse_iso_date(user.get("dtContractEnd"))

    # Pas de date de début => pas de contrat
    if not start_date:
        return contracts

    if start_date > today:
        status = "FUTURE"
    elif end_date is None or end_date >= today:
        status = "ACTIVE"
    else:
        status = "ENDED"

    department_id = user.get("departmentId", user.get("departmentID"))
    manager_id = user.get("managerId", user.get("managerID"))

    contract = {
        "contract_id": f"{user.get('id')}_1",
        "employee_id": user.get("id"),
        "contract_start_date": start_date.isoformat(),
        "contract_end_date": end_date.isoformat() if end_date else None,
        "job_title": user.get("jobTitle"),

        "department_id": department_id,
        "department_name": (user.get("department") or {}).get("name"),

        "manager_id": manager_id,
        "manager_name": (user.get("manager") or {}).get("name"),

        "calendar_id": user.get("calendarId"),
        "calendar_name": (user.get("calendar") or {}).get("name"),

        "status": status,
    }

    contracts.append(contract)
    return contracts


# =====================================================
# MAIN EXTRACTION
# =====================================================

def run_extraction() -> None:
    client = LuccaClient()

    raw_dir = Path(Config.DATA_DIR) / "raw"
    ensure_dir(raw_dir)

    # 1) IDs utilisateurs
    user_ids = client.get_all_user_ids()
    print(f"{len(user_ids)} utilisateurs trouvés.")

    users_essential: List[Dict[str, Any]] = []
    all_contracts: List[Dict[str, Any]] = []

    # 2) Récupération users détaillés + extraction
    for uid in user_ids:
        user_detail = client.get_user_details(uid)

        users_essential.append(
            extract_essential_user(user_detail)
        )

        all_contracts.extend(
            extract_contracts_from_user(user_detail)
        )

        time.sleep(0.2)  # respect API (~5 req/sec)

    # 3) Departments
    departments_resp = client.get_departments()
    departments = departments_resp.get("data", {}).get("items", [])

    # 4) Écriture fichiers
    write_output(raw_dir / "users", users_essential)
    write_output(raw_dir / "contracts", all_contracts)
    write_output(raw_dir / "departments", departments)

    # 5) Logs finaux
    print("Extraction terminée")
    print(f"- Users       : {len(users_essential)}")
    print(f"- Contracts   : {len(all_contracts)}")
    print(f"- Departments : {len(departments)}")
    print(f"- Format      : {getattr(Config, 'OUTPUT_FORMAT', 'json').upper()}")


if __name__ == "__main__":
    run_extraction()
