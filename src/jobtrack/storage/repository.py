from uuid import UUID

from sqlalchemy import select
from sqlalchemy.engine import Connection

from jobtrack.domain.events import Event
from jobtrack.storage.schema import events


class EventRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def append(self, event: Event) -> None:
        self._conn.execute(
            events.insert().values(
                event_id=event.event_id,
                application_id=event.application_id,
                event_type=event.event_type,
                occurred_at=event.occurred_at,
                recorded_at=event.recorded_at,
                payload=event.model_dump(
                    exclude={
                        "event_id",
                        "application_id",
                        "event_type",
                        "occurred_at",
                        "recorded_at",
                        "version",
                    }
                ),
                version=event.version,
            )
        )

    def list_for_application(self, application_id: UUID) -> list[dict[str, object]]:
        result = self._conn.execute(
            select(events)
            .where(events.c.application_id == application_id)
            .order_by(events.c.occurred_at)
        )
        return [dict(row._mapping) for row in result]
