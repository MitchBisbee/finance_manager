"""Run the weekly Plaid ETL as a standalone pod entry point."""
from db.connections import get_postgres_client
from db.repositories import get_transaction_repository
from airflow_etl.services import get_plaid_sandbox_session_factory, get_plaid_service


def plaid_etl():
    """Extract, transform, and load Plaid transactions in one transaction."""
    print("Launching weekly cron-pod...")
    plaid_session_factory = get_plaid_sandbox_session_factory()
    db_client = get_postgres_client(connection_string="placeholder")
    transaction_repository = get_transaction_repository(
        db_client=db_client)
    plaid_service = get_plaid_service(
        session_factory=plaid_session_factory,
        transaction_repository=transaction_repository
    )

    raw_transactions = plaid_service.extract()
    records = plaid_service.transform(raw_transactions)

    with transaction_repository.transaction():
        plaid_service.load(records)

    print("Weekly sync complete!")
