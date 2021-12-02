"""
This file assumes the format of messaged-people.yaml is

.. code-block:: yaml

    people:
    - name: xxx
    - name: yyy
    - name: zzz
"""

from typing import List

import yaml
from dataclasses import dataclass

from constants import MESSAGED_PEOPLE_STORE_FPATH

@dataclass(frozen=True)
class MessagedPerson:
    name: str

    def to_dict(self) -> dict:
        return {
            "name": self.name
        }

def load_messaged_people() -> List[MessagedPerson]:
    if not MESSAGED_PEOPLE_STORE_FPATH.exists():
        return []

    messaged_people_txt: str = MESSAGED_PEOPLE_STORE_FPATH.read_text()
    data: dict = yaml.safe_load(messaged_people_txt)
    return [MessagedPerson(**person) for person in data["people"]]

def save_messaged_people(people: List[MessagedPerson]):
    data = {
        "people": [person.to_dict() for person in people]
    }
    with open(MESSAGED_PEOPLE_STORE_FPATH, "w") as file:
        yaml.safe_dump(data, file)

def save_messaged_person(person: MessagedPerson):
    messaged_people: List[MessagedPerson] = load_messaged_people()
    if person.name not in [p.name for p in messaged_people]:
        messaged_people += [person]
    save_messaged_people(messaged_people)

