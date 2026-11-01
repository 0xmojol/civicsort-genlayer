import json

import pytest


PROFILE_ID = "test-frankfurt"
REGION_LABEL = "Frankfurt am Main, Germany (test)"
SOURCE_URL = "https://example.org/sorting-guide"
POLICY_TEXT = (
    "Sorting guide for household packaging in Frankfurt. "
    "Beverage cartons belong in the Gelbe Tonne. "
    "This guide is a test snapshot and does not replace official local advice."
)


def test_register_profile_and_read_back(direct_deploy):
    contract = direct_deploy("contracts/civic_sort.py")

    result = contract.register_profile(
        PROFILE_ID,
        REGION_LABEL,
        SOURCE_URL,
        POLICY_TEXT,
    )

    assert result == PROFILE_ID

    profile = json.loads(contract.get_profile(PROFILE_ID))
    assert profile["profile_id"] == PROFILE_ID
    assert profile["region_label"] == REGION_LABEL
    assert profile["source_url"] == SOURCE_URL
    assert profile["policy_text"] == POLICY_TEXT
    assert profile["policy_hash"]
    assert profile["source_note"]


def test_profile_id_cannot_be_registered_twice(direct_deploy):
    contract = direct_deploy("contracts/civic_sort.py")

    contract.register_profile(
        PROFILE_ID,
        REGION_LABEL,
        SOURCE_URL,
        POLICY_TEXT,
    )

    with pytest.raises(Exception, match="profile_id already exists"):
        contract.register_profile(
            PROFILE_ID,
            REGION_LABEL,
            SOURCE_URL,
            POLICY_TEXT,
        )


def test_evaluation_uses_policy_supported_result(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/civic_sort.py")

    contract.register_profile(
        PROFILE_ID,
        REGION_LABEL,
        SOURCE_URL,
        POLICY_TEXT,
    )

    # The mocked response is used for the leader and validator classification.
    direct_vm.mock_llm(
        r".*",
        json.dumps(
            {
                "decisions": [
                    {
                        "index": 0,
                        "category": "RECYCLING",
                        "local_stream": "Gelbe Tonne",
                        "quote": "Beverage cartons belong in the Gelbe Tonne.",
                    }
                ]
            }
        ),
    )

    result = contract.evaluate_item(
        PROFILE_ID,
        "Beverage carton",
        json.dumps(["beverage carton"]),
    )
    record = json.loads(result)

    assert record["profile_id"] == PROFILE_ID
    assert record["policy_hash"]
    assert record["components"] == ["beverage carton"]
    assert record["decisions"] == [
        {
            "index": 0,
            "category": "RECYCLING",
            "local_stream": "Gelbe Tonne",
            "quote": "Beverage cartons belong in the Gelbe Tonne.",
        }
    ]


def test_evaluation_rejects_unknown_profile(direct_deploy):
    contract = direct_deploy("contracts/civic_sort.py")

    with pytest.raises(Exception, match="profile not found"):
        contract.evaluate_item(
            "missing-profile",
            "Beverage carton",
            json.dumps(["beverage carton"]),
        )
