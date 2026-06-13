from dataclasses import dataclass
from enum import StrEnum

from custodia.domain.intake import IntakeStatus


class AdministrativeDocumentType(StrEnum):
    CONSENT_FORM = "consent_form"
    INSURANCE_VERIFICATION = "insurance_verification"

    @property
    def label(self) -> str:
        match self:
            case AdministrativeDocumentType.CONSENT_FORM:
                return "Consent form"
            case AdministrativeDocumentType.INSURANCE_VERIFICATION:
                return "Insurance verification"


@dataclass(frozen=True)
class AdministrativeDocument:
    document_type: AdministrativeDocumentType
    status: IntakeStatus


@dataclass(frozen=True)
class PatientAdministrativeProfile:
    patient_id: str
    display_name: str
    preferred_language: str
    requested_service: str
    documents: tuple[AdministrativeDocument, ...]

    def missing_document_labels(self) -> tuple[str, ...]:
        return tuple(
            administrative_document.document_type.label
            for administrative_document in self.documents
            if administrative_document.status == IntakeStatus.MISSING
        )

    def pending_review_document_labels(self) -> tuple[str, ...]:
        return tuple(
            administrative_document.document_type.label
            for administrative_document in self.documents
            if administrative_document.status == IntakeStatus.PENDING_REVIEW
        )

    def is_ready_for_scheduling(self) -> bool:
        return (
            len(self.missing_document_labels()) == 0
            and len(self.pending_review_document_labels()) == 0
        )
