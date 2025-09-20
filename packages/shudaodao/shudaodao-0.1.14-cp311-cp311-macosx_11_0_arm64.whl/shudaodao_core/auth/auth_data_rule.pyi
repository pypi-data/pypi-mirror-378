from dataclasses import dataclass
from requests import Request as Request
from typing import Pattern

@dataclass
class AuthDataRule:
    method: str
    pattern: Pattern
    data_role: str
    data_act: str
    data_obj: str
    @staticmethod
    def convert_path_to_regex(path: str) -> Pattern: ...

def get_data_rule_from_request(*, request: Request, data_rules: list[AuthDataRule]) -> AuthDataRule | None: ...
