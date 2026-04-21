from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

metadata = MetaData()


events = Table(
    "events",
    metadata,
    Column("event_id", UUID(as_uuid=True), primary_key=True),
    Column("application_id", UUID(as_uuid=True), nullable=False, index=True),
    Column("event_type", Text, nullable=False),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("recorded_at", DateTime(timezone=True), nullable=False),
    Column("payload", JSONB, nullable=False),
    Column("version", Integer, nullable=False),
)
