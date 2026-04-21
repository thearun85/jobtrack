from datetime import UTC, datetime
from typing import Any, TypeVar
from uuid import uuid4

import pytest

from jobtrack.domain.events import Applied, BaseEvent, Ghosted, Rejected
from jobtrack.domain.state_machine import InvalidTransition, State, apply

E = TypeVar("E", bound=BaseEvent)


def _event(cls: type[E], **kwargs: Any) -> E:
    return cls(application_id=uuid4(), occurred_at=datetime.now(tz=UTC), **kwargs)


def test_applied_from_nothing_gives_applied() -> None:
    assert apply(None, _event(Applied)) == State.APPLIED


def test_rejected_from_applied_gives_rejected() -> None:
    assert apply(State.APPLIED, _event(Rejected)) == State.REJECTED


def test_ghosted_from_applied_gives_ghosted() -> None:
    assert apply(State.APPLIED, _event(Ghosted)) == State.GHOSTED


def test_cannot_apply_twice() -> None:
    with pytest.raises(InvalidTransition):
        apply(State.APPLIED, _event(Applied))


def test_cannot_reject_from_terminal_state() -> None:
    with pytest.raises(InvalidTransition):
        apply(State.REJECTED, _event(Rejected))


def test_cannot_apply_without_initial_event() -> None:
    with pytest.raises(InvalidTransition):
        apply(None, _event(Rejected))
