from extract import derive_contracts_from_users


def test_derive_contracts_from_users():
    """
    Vérifie qu'un contrat est correctement dérivé
    à partir d'un user avec dtContractStart.
    """

    users = [
        {
            "id": 1,
            "dtContractStart": "2020-01-01T00:00:00",
            "dtContractEnd": None,
            "departmentId": 10,
            "rolePrincipal": {"name": "Engineer"},
            "userWorkCycles": []
        },
        {
            # User sans contrat → ne doit rien produire
            "id": 2,
            "dtContractStart": None,
        }
    ]

    contracts = derive_contracts_from_users(users)

    # ---- Assertions ----
    assert len(contracts) == 1

    contract = contracts[0]
    assert contract["user_id"] == 1
    assert contract["start_date"] == "2020-01-01T00:00:00"
    assert contract["end_date"] is None
    assert contract["department_id"] == 10
    assert contract["role"] == "Engineer"

