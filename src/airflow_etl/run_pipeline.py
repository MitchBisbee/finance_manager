"""Provide a command-line interface for executing ETL pipelines."""

import argparse

from airflow_etl.pipelines import plaid_etl


def cli():
    """Parse the selected pipeline name and execute its registered function."""
    pipelines = {
        "plaid_etl": plaid_etl,
    }

    parser = argparse.ArgumentParser(description="Run an ETL pipeline.")
    parser.add_argument(
        "--pipeline",
        required=True,
        choices=pipelines.keys(),
        help="The ETL pipeline to execute.",
    )
    args = parser.parse_args()

    pipelines[args.pipeline]()


if __name__ == "__main__":
    cli()
