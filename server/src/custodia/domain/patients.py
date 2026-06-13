from dataclasses import dataclass

from custodia.domain.intake import IntakeStatus


@dataclass(frozen=True)
class IntakeDocument:
    name: str
    status: IntakeStatus


@dataclass(frozen=True)
class PatientAdministrativeProfile:
    patient_id: str
    display_name: str
    preferred_language: str
    requested_service: str
    documents: tuple[IntakeDocument, ...]
