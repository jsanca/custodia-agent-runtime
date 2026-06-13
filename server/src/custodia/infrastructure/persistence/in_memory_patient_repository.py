from custodia.domain.intake import IntakeStatus
from custodia.domain.patients import IntakeDocument, PatientAdministrativeProfile

_FAKE_PATIENTS: dict[str, PatientAdministrativeProfile] = {
    "PAT-001": PatientAdministrativeProfile(
        patient_id="PAT-001",
        display_name="Alex Rivera",
        preferred_language="en",
        requested_service="outpatient_therapy",
        documents=(
            IntakeDocument(name="consent_form", status=IntakeStatus.COMPLETE),
            IntakeDocument(name="insurance_verification", status=IntakeStatus.MISSING),
        ),
    ),
    "PAT-002": PatientAdministrativeProfile(
        patient_id="PAT-002",
        display_name="Jordan Lee",
        preferred_language="es",
        requested_service="intake_assessment",
        documents=(
            IntakeDocument(name="consent_form", status=IntakeStatus.PENDING_REVIEW),
            IntakeDocument(name="insurance_verification", status=IntakeStatus.COMPLETE),
        ),
    ),
}


class InMemoryPatientRepository:
    def load(self, patient_id: str) -> PatientAdministrativeProfile | None:
        return _FAKE_PATIENTS.get(patient_id)
