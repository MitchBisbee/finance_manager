import os
from src.shared.database import SessionLocal
from src.shared.models.transaction import TransactionModel
from src.finance_manager.services.plaid import PlaidService
# TODO: this just example code and the pipeline will be different.


def main():
    print("Launching weekly cron-pod...")
    db = SessionLocal()
    try:
        # 1. Instantiate your service logic
        plaid_service = PlaidService(
            client_id=os.getenv("PLAID_CLIENT_ID"),
            secret=os.getenv("PLAID_SECRET")
        )

        # 2. Extract
        raw_txs = plaid_service.fetch_weekly(os.getenv("MY_ACCESS_TOKEN"))

        # 3. Transform & Load using your shared models
        for tx in raw_txs:
            record = TransactionModel(id=tx["id"], amount=tx["amount"])
            db.merge(record)  # Upsert

        db.commit()
        print("Weekly sync complete!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
