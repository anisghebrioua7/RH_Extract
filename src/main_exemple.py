from config import validate_config
from lucca_client import LuccaClient


def main():
    validate_config()
    client = LuccaClient()

    # =====================
    # USERS
    # =====================
    users_response = client.get_employees()
    users = users_response.get("data", {}).get("items", [])

    print("===== USERS =====")
    print(f"Nombre total de salariés : {len(users)}")

    if not users:
        print("❌ Aucun user récupéré")
        return

    print("Exemple user (brut) :")
    print({
        "id": users[0].get("id"),
        "displayName": users[0].get("displayName"),
        "departmentId": users[0].get("departmentId"),
        "dtContractStart": users[0].get("dtContractStart"),
        "dtContractEnd": users[0].get("dtContractEnd"),
    })

    # =====================
    # TEST : USER AVEC CONTRAT
    # =====================
    user_with_contract = next(
        (u for u in users if u.get("dtContractStart")), None
    )

    if user_with_contract:
        print("\nUser avec contrat trouvé :")
        print({
            "id": user_with_contract.get("id"),
            "displayName": user_with_contract.get("displayName"),
            "dtContractStart": user_with_contract.get("dtContractStart"),
            "dtContractEnd": user_with_contract.get("dtContractEnd"),
            "departmentId": user_with_contract.get("departmentId"),
        })
    else:
        print("\nAucun user avec contrat dans cette sandbox")

    # =====================
    # DEPARTMENTS
    # =====================
    departments_response = client.get_departments()
    departments = departments_response.get("data", {}).get("items", [])

    print("\n===== DEPARTMENTS =====")
    print(f"Nombre total de départements : {len(departments)}")

    if departments:
        print("Exemple département :")
        print({
            "id": departments[0].get("id"),
            "name": departments[0].get("name"),
            "parentId": departments[0].get("parentId"),
            "path": departments[0].get("path"),
            "isActive": departments[0].get("isActive"),
        })


if __name__ == "__main__":
    main()
