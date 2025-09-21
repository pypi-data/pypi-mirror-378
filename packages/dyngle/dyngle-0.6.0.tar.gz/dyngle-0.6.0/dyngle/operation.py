from dataclasses import dataclass


@dataclass
class Operation:

    local_expressions: dict

    steps: list
