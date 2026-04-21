# jobtrack

An event-sourced job application tracker. CLI-first, postgres-backed, built to model a job hunt the way a bank models a ledger: append-only events are the source of truth.
> **Status:** under active construction. Week 1 (core engine + CLI) is the current focus. Gmail ingestion, the LLM extractor, and the dashboard land in weeks 2-3. See [Roadmap](#roadmap).

## Design

- **Event-sourced core.** `events` table is append-only and authoritative. `applications_view` is a read model, disposable, rebuilt by folding the log.
- **Pure state machine.** `apply(current_state, event) -> new_state` is a pure function with heavy test coverage. Invalid transitions raise.
- **Domain as a library, not a service.** No HTTP API in v1. The CLI imports the domain directly. A FastAPI layer can be added later without redesign.
- **Postgres only.** No redis, no Kafka, no object storage. CVs and JDs live on disk, referenced by path.
- **Single-tenant, no auth.** Runs on a laptop or a 5$ VPS behind tailscale.

## Data model

Four tables. Two hold facts, two hold derived views.

```
events				-- append-only, source of truth
  event_id			uuid pk
  application_id    uuid fk
  event_type		text
  occurred_at		timestamptz  -- when it happened in the world
  recorded_at		timestamptz  -- when it hit the log
  payload			jsonb
  version			int

applications		-- one row per application, written once
  application_id	uuid pk
  company_id		uuid fk -> companies
  role_title		text
  source 			text 		 -- linkedin, hackajob, referral, direct
  cv_variant		text		 -- funding_circle, general_python, etc.
  created_at		timestamptz

companies			-- one row per company
  company_id		uuid pk
  name				text unique
  domain			text		 -- for matching inbound emails
  notes				text			

applications_view	-- projection, rebuilt by folding the event log
  application_id	uuid pk
  current_state		text
  last_event_at		timestamptz
  days_since_apply  int
  days_in_state		int

```

`events` is the source of truth. `applications_view` is never written by hand - a projection function folds over the log and upserts into it. `applications` and `companies` hold identity  and creation-time facts so the event log has something to reference.

## State machine

```
Applied
  -> RecruiterScreenScheduled	-> RecruiterScreenDone
  -> TechnicalScreenScheduled	-> TechnicalScreenDone
  -> OnsiteScheduled			-> OnsiteDone
  -> OfferReceived				-> OffAccepted | OfferDeclined
```

Terminal states reachable from most non-terminal states. `Rejected`, `Withdrawn`, `Ghosted`.

`Ghosted` is time-based: the scheduler appends one after 21 days of silence. It's not user-driven.

## Requirements

- Python 3.12+
- Poetry 1.8+
- Docker + Docker Compose (for Postgres)
- Make

## Setup

```bash
git clone https://github.com/arunraghunath/jobtrack.git
cd jobtrack
make install 			# poetry install + pre-commit hooks
make db-up 				# starts Postgres in docker
make migrate 			# applies schema
make test 				# runs the test suite
```

After that:

```bash
poetry run jobtrack --help
```

## Usage

> Week 1 commands. More to come as ingestion and review land.

```bash
jobtrack add 					# interactive: add new application
jobtrack event <app-id><type>	# append an event to the application
jobtrack pipeline				# show current pipeline by stage
jobtrack show <app-id>			# full event history for one application
```

## Development

All workflows run through `make`:

| Command         | What it does                                           |
| --------------- | ------------------------------------------------------ |
| `make install`  | `poetry install` + install pre-commit hooks            |
| `make fmt`      | Format with ruff                                       |
| `make lint`     | Lint with ruff (no fixes)                              |
| `make typecheck`| Run mypy in strict mode                                |
| `make test`     | Run pytest with coverage                               |
| `make check`    | `lint` + `typecheck` + `test` (what CI runs)           |
| `make db-up`    | Start Postgres via docker compose                      |
| `make db-down`  | Stop Postgres                                          |
| `make db-reset` | Drop + recreate the database                           |
| `make migrate`  | Apply schema migrations                                |
| `make clean`    | Remove caches and build artefacts                      |

### Tooling
 
- **Poetry** — dependency management, packaging, virtualenv.
- **ruff** — formatting and linting. Replaces black, isort, flake8.
- **mypy** — static type checking, strict mode.
- **pytest** — tests. Integration tests use [testcontainers](https://testcontainers.com/) to spin up real Postgres.
- **pre-commit** — runs ruff + mypy on staged files before every commit.
## Project structure
 
```
jobtrack/
├── src/jobtrack/
│   ├── domain/          # events, state machine, apply()
│   ├── storage/         # SQLAlchemy Core repositories
│   ├── projections/     # read model builders
│   ├── ingestion/       # gmail + llm extractor (week 2)
│   ├── scheduler/       # ghost detection, digests (week 2)
│   ├── cli/             # typer entrypoints
│   └── dashboard/       # streamlit app (week 3)
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── README.md
```
 
## Roadmap
 
- **Week 1 — core + CLI.** Event schema, state machine, storage, CLI. Tracking real applications by end of week. *(in progress)*
- **Week 2 — ingestion.** Gmail label worker reads routed recruiter emails; Anthropic API extracts structured events with confidence scores; low-confidence results go to a CLI review queue.
- **Week 3 — dashboard.** Small Streamlit app: pipeline health, CV variant performance, follow-ups due.
Things deliberately not on the roadmap: HTTP API, auth, multi-tenancy, calendar integration, mobile client, SaaS version. See `FUTURE.md` for ideas that came up mid-build and were parked.
 
## Article
 
A write-up — *Modelling my job hunt as an event-sourced ledger* — will ship alongside the v1 release. Link will go here.
 
## License
 
MIT.
