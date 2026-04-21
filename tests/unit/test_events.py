from datetime import UTC, datetime
from uuid import uuid4

from jobtrack.domain.events import Applied, Ghosted, Rejected


def test_applied_event_has_correct_type() -> None:
    event = Applied(
        application_id=uuid4(),
        occurred_at=datetime.now(tz=UTC),
    )
    assert event.event_type == "applied"


def test_event_auto_generates_eventid_and_recordedat() -> None:
    event = Applied(
        application_id=uuid4(),
        occurred_at=datetime.now(tz=UTC),
    )
    assert event.recorded_at is not None
    assert event.event_id is not None


def test_rejected_event_has_correct_type() -> None:
    event = Rejected(
        application_id=uuid4(),
        occurred_at=datetime.now(tz=UTC),
    )
    assert event.event_type == "rejected"


def test_rejected_event_has_optional_reason() -> None:
    with_reason = Rejected(
        application_id=uuid4(),
        occurred_at=datetime.now(tz=UTC),
        reason="no visa sponsorship",
    )

    without_reason = Rejected(
        application_id=uuid4(),
        occurred_at=datetime.now(tz=UTC),
    )

    assert without_reason.reason is None
    assert with_reason.reason == "no visa sponsorship"


def test_ghosted_event_has_correct_type() -> None:
    event = Ghosted(
        application_id=uuid4(),
        occurred_at=datetime.now(tz=UTC),
    )

    assert event.event_type == "ghosted"
