from custodia.domain.intake import IntakeStatus
from custodia.domain.patients import (
    AdministrativeDocument,
    AdministrativeDocumentType,
    PatientAdministrativeProfile,
)


def _make_profile(documents: tuple[AdministrativeDocument, ...]) -> PatientAdministrativeProfile:
    return PatientAdministrativeProfile(
        patient_id="PAT-TEST",
        display_name="Test Patient",
        preferred_language="en",
        requested_service="outpatient_therapy",
        documents=documents,
    )


def test_document_type_label_returns_human_readable_string() -> None:
    assert AdministrativeDocumentType.CONSENT_FORM.label == "Consent form"
    assert AdministrativeDocumentType.INSURANCE_VERIFICATION.label == "Insurance verification"


def test_missing_document_labels_returns_human_readable_labels() -> None:
    patient_profile = _make_profile(
        documents=(
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.CONSENT_FORM,
                status=IntakeStatus.MISSING,
            ),
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.INSURANCE_VERIFICATION,
                status=IntakeStatus.COMPLETE,
            ),
        )
    )

    assert patient_profile.missing_document_labels() == ("Consent form",)


def test_pending_review_document_labels_returns_human_readable_labels() -> None:
    patient_profile = _make_profile(
        documents=(
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.CONSENT_FORM,
                status=IntakeStatus.PENDING_REVIEW,
            ),
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.INSURANCE_VERIFICATION,
                status=IntakeStatus.COMPLETE,
            ),
        )
    )

    assert patient_profile.pending_review_document_labels() == ("Consent form",)


def test_is_ready_for_scheduling_when_all_documents_complete() -> None:
    patient_profile = _make_profile(
        documents=(
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.CONSENT_FORM,
                status=IntakeStatus.COMPLETE,
            ),
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.INSURANCE_VERIFICATION,
                status=IntakeStatus.COMPLETE,
            ),
        )
    )

    assert patient_profile.is_ready_for_scheduling() is True


def test_is_not_ready_for_scheduling_when_document_is_missing() -> None:
    patient_profile = _make_profile(
        documents=(
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.CONSENT_FORM,
                status=IntakeStatus.MISSING,
            ),
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.INSURANCE_VERIFICATION,
                status=IntakeStatus.COMPLETE,
            ),
        )
    )

    assert patient_profile.is_ready_for_scheduling() is False


def test_is_not_ready_for_scheduling_when_document_is_pending_review() -> None:
    patient_profile = _make_profile(
        documents=(
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.CONSENT_FORM,
                status=IntakeStatus.PENDING_REVIEW,
            ),
            AdministrativeDocument(
                document_type=AdministrativeDocumentType.INSURANCE_VERIFICATION,
                status=IntakeStatus.COMPLETE,
            ),
        )
    )

    assert patient_profile.is_ready_for_scheduling() is False


def test_empty_document_list_is_ready_for_scheduling() -> None:
    patient_profile = _make_profile(documents=())

    assert patient_profile.missing_document_labels() == ()
    assert patient_profile.pending_review_document_labels() == ()
    assert patient_profile.is_ready_for_scheduling() is True
