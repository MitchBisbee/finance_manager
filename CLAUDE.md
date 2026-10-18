# CLAUDE.md

A PySide6 + Plotly desktop app that analyzes bank and credit-card CSV exports, plus an importer (in progress) that loads Plaid transactions into PostgreSQL.

## Commands

- Install: `uv sync --extra dev` (Python >= 3.14; the package is in `src/finance_manager/`)
- Run: `uv run app [CSV_DIR_OR_FILE]`. The data path comes from the argument, then `FINANCE_DATA_DIR`, then a folder picker.
- Test: `uv run --extra dev pytest -m unit` (or `integration` / `system`)
- Lint: `uv run --extra dev ruff check src tests`
- Migrate: `uv run alembic upgrade head`

## Environment variables

| Var | Purpose |
| --- | --- |
| `FINANCE_DATA_DIR` | Default CSV location |
| `PLAID_CLIENT_ID`, `PLAID_SECRET` | Plaid Sandbox credentials |
| `POSTGRES_SUPERUSER_NAME`, `POSTGRES_SUPERUSER_PSWRD`, `DB_HOST`, `DB_PORT` | Alembic connection |

## Database safety

`alembic/env.py` hardcodes the **real** database, `personal-finances`, and connects as a superuser. Never run migrations or database tests unless you're sure of the target. Tests must use a separate PostgreSQL test database (never SQLite), and that database's name must end in `_test`.

## Pipelines

- CSV app: `CSVDataCleaner` → `FinanceService` → `MainWindow`
- Plaid import: `PlaidSandboxSessionFactory` → `PlaidService` → `TransactionRepository` → `PostgresClient`

## Non-obvious rules

- Cleaned frames have the columns `date, description, category, amount`. **Negative amounts are expenses and positive amounts are income.** A CSV with a `Transaction Date` column is treated as credit; any other CSV is checking.
- Repositories `add` and `flush` but never commit. The caller owns the transaction (`with repo.transaction():`). `PlaidService` doesn't commit either.
- `PostgresClient` is one shared instance per process, and constructing it with a different URL raises `ValueError`. Tests must reset `PostgresClient._instance`.
- The repository's `transaction_id` parameters are internal UUIDs. Plaid's ID is stored as `bank_transaction_id`.
- Each layer has an ABC in a sibling `interfaces/` package. Code depends on those ABCs and gets implementations from the `get_*` factory functions exported by each package.

## Testing conventions

- Tests go in `tests/unit/`, `tests/integration/` or `tests/system/`. The root `conftest.py` marks each test by its folder, and `--strict-markers` is on.
- Build test data with pytest fixtures and factory fixtures only. Never use module-level helper functions.
- Use `unittest.mock`, and spec every double (`create_autospec`). Never use a bare `MagicMock()`.
- Each test module has the classes `TestHappyPaths` and `TestUnhappyPaths`. Follow Arrange, Act, Assert, separating the sections with blank lines and no comments. Use `pytest.mark.parametrize` with `ids=`.
