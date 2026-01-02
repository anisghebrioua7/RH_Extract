import json
import csv
from pathlib import Path
from typing import List, Dict, Any

from lucca_client import LuccaClient
from config import Config


# =====================
# Utils
# =====================

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_csv(path: Path, data: List[Dict[str, Any]]) -> None:
    if not data:
        return

    # Colonnes = union des clés
    fieldnames = set()
    for row in data:
        fieldnames.update(row.keys())

    fieldnames = sorted(fieldnames)

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


def write_output(path: Path, data: List[Dict[str, Any]]) -> None:
    if Config.OUTPUT_FORMAT == "csv":
        write_csv(path.with_suffix(".csv"), data)
    else:
        write_json(path.with_suffix(".json"), data)


# =====================
# Extraction logic
# =====================

def extract_users(client: LuccaClient) -> List[Dict[str, Any]]:
    response = client.get_employees()
    return response.get("data", {}).get("items", [])


def extract_departments(client: LuccaClient) -> List[Dict[str, Any]]:
    response = client.get_departments()
    return response.get("data", {}).get("items", [])


def derive_contracts_from_users(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    contracts = []

    for user in users:
        start_date = user.get("dtContractStart")

        if not start_date:
            continue

        contracts.append({
            "user_id": user.get("id"),
            "start_date": start_date,
            "end_date": user.get("dtContractEnd"),
            "department_id": user.get("departmentId"),
            "role": user.get("rolePrincipal", {}).get("name"),
            "work_cycles": user.get("userWorkCycles", []),
        })

    return contracts


# =====================
# Main extraction
# =====================

def run_extraction() -> None:
    client = LuccaClient()

    raw_dir = Path(Config.DATA_DIR) / "raw"
    ensure_dir(raw_dir)

    users = extract_users(client)
    contracts = derive_contracts_from_users(users)
    departments = extract_departments(client)

    write_output(raw_dir / "users", users)
    write_output(raw_dir / "contracts", contracts)
    write_output(raw_dir / "departments", departments)

    print("Extraction terminée")
    print(f"- Users       : {len(users)}")
    print(f"- Contracts   : {len(contracts)}")
    print(f"- Departments : {len(departments)}")
    print(f"- Format      : {Config.OUTPUT_FORMAT.upper()}")


if __name__ == "__main__":
    run_extraction()
