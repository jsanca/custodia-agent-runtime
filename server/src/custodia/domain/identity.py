from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    CLINICIAN = "clinician"
    STAFF = "staff"
    SYSTEM = "system"


@dataclass(frozen=True)
class Principal:
    subject: str
    email: str
    roles: frozenset[Role]

    def has_role(self, role: Role) -> bool:
        return role in self.roles
