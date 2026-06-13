from custodia.domain.intake import IntakeStatus
from custodia.domain.patients import (
    AdministrativeDocument,
    AdministrativeDocumentType,
    PatientAdministrativeProfile,
)

_FAKE_PATIENTS: dict[str, PatientAdministrativeProfile] = {
    "PAT-001": PatientAdministrativeProfile(
        patient_id="PAT-001",
        display_name="Alex Rivera",
        preferred_language="en",
        requested_service="outpatient_therapy",
        documents=(
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.CONSENT_FORM,
                status=IntakeStatus.COMPLETE,
            ),
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.INSURANCE_VERIFICATION,
                status=IntakeStatus.MISSING,
            ),
        ),
    ),
    "PAT-002": PatientAdministrativeProfile(
        patient_id="PAT-002",
        display_name="Jordan Lee",
        preferred_language="es",
        requested_service="intake_assessment",
        documents=(
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.CONSENT_FORM,
                status=IntakeStatus.PENDING_REVIEW,
            ),
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.INSURANCE_VERIFICATION,
                status=IntakeStatus.COMPLETE,
            ),
        ),
    ),
}


class InMemoryPatientRepository:
    def load(self, patient_id: str) -> PatientAdministrativeProfile | None:
        return _FAKE_PATIENTS.get(patient_id)
