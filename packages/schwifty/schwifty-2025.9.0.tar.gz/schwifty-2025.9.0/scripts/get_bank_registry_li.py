import json
from typing import Any

import requests


URL = "https://api.six-group.com/api/epcd/bankmaster/v3/bankmaster.json"


def fetch() -> list[dict[str, Any]]:
    return requests.get(URL).json()["entries"]


def process(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    registry: list[dict[str, Any]] = []

    for record in records:
        if record["entryType"] != "BankMaster" or record["country"] != "LI":
            continue
        name = short_name = record["bankOrInstitutionName"]
        registry.append(
            {
                "name": name,
                "short_name": short_name,
                "bank_code": f"{record['iid']:0>5}",
                "bic": record.get("bic"),
                "country_code": "LI",
                "primary": record["iidType"] == "HEADQUARTERS",
            }
        )
    return registry


if __name__ == "__main__":
    with open("schwifty/bank_registry/generated_li.json", "w") as fp:
        json.dump(process(fetch()), fp, indent=2)
