"""Schedule the weekly Plaid ETL pipeline in a transient Kubernetes pod."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s


default_args = {
    "owner": "finance_team",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}


with DAG(
    dag_id="monorepo_weekly_plaid_sync",
    default_args=default_args,
    description="Run the Plaid ETL pipeline weekly in a transient k3s pod.",
    schedule="@weekly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["personal_app", "k3s", "monorepo"],
) as plaid_etl_dag:
    run_plaid_pipeline = KubernetesPodOperator(
        task_id="execute_plaid_etl",
        namespace="airflow",
        image="localhost:5000/monorepo-app:latest",
        image_pull_policy="Always",
        name="plaid-etl-runner",
        cmds=["uv", "run", "python"],
        arguments=[
            "src/airflow_etl/run_pipeline.py",
            "--pipeline",
            "plaid_etl",
        ],
        env_from=[
            k8s.V1EnvFromSource(
                secret_ref=k8s.V1SecretEnvSource(name="finance-app-secrets"),
            ),
        ],
        container_resources=k8s.V1ResourceRequirements(
            requests={"cpu": "200m", "memory": "256Mi"},
            limits={"cpu": "500m", "memory": "512Mi"},
        ),
        get_logs=True,
        is_delete_operator_pod=True,
    )
