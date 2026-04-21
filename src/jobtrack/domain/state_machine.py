from enum import StrEnum

from jobtrack.domain.events import Applied, Event, Ghosted, Rejected


class State(StrEnum):
    APPLIED = "applied"
    REJECTED = "rejected"
    GHOSTED = "ghosted"


TRANSITIONS: dict[tuple[State | None, type[Event]], State] = {
    (None, Applied): State.APPLIED,
    (State.APPLIED, Rejected): State.REJECTED,
    (State.APPLIED, Ghosted): State.GHOSTED,
}


class InvalidTransition(Exception):
    pass


def apply(current: State | None, event: Event) -> State:
    key = (current, type(event))
    if key not in TRANSITIONS:
        raise InvalidTransition(
            f"Cannot apply {type(event).__name__} from state {current}"
        )
    return TRANSITIONS[key]
