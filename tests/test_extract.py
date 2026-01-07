from datetime import date, timedelta

from extract import extract_contracts_from_user


def test_extract_contract_from_user_with_start_date():
    """
    Un user avec dtContractStart doit produire exactement 1 contrat.
    """
    user = {
        "id": 1,
        "dtContractStart": "2023-01-01T00:00:00",
        "dtContractEnd": None,
        "departmentId": 10,
        "department": {"name": "Engineering"},
        "managerId": 5,
        "manager": {"name": "Alice Manager"},
        "calendarId": 1,
        "calendar": {"name": "France"},
        "jobTitle": "Data Engineer",
    }

    contracts = extract_contracts_from_user(user)

    assert len(contracts) == 1

    contract = contracts[0]
    assert contract["employee_id"] == 1
    assert contract["contract_start_date"] == "2023-01-01"
    assert contract["contract_end_date"] is None
    assert contract["status"] == "ACTIVE"


def test_extract_contract_from_user_without_start_date():
    """
    Un user sans dtContractStart ne doit produire aucun contrat.
    """
    user = {
        "id": 2,
        "dtContractStart": None,
        "dtContractEnd": None,
    }

    contracts = extract_contracts_from_user(user)

    assert contracts == []


def test_contract_status_future():
    """
    Si la date de début de contrat est dans le futur, le statut doit être FUTURE.
    """
    future_date = (date.today() + timedelta(days=30)).isoformat()

    user = {
        "id": 3,
        "dtContractStart": f"{future_date}T00:00:00",
        "dtContractEnd": None,
    }

    contracts = extract_contracts_from_user(user)

    assert len(contracts) == 1
    assert contracts[0]["status"] == "FUTURE"


def test_contract_status_ended():
    """
    Si dtContractEnd est dans le passé, le statut doit être ENDED
    """
    user = {
        "id": 4,
        "dtContractStart": "2020-01-01T00:00:00",
        "dtContractEnd": "2021-01-01T00:00:00",
    }

    contracts = extract_contracts_from_user(user)

    assert len(contracts) == 1
    assert contracts[0]["status"] == "ENDED"
