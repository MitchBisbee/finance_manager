from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s
# this is just examle code and it will need to be modified to fit your monorepo's package structure and ETL logic.
default_args = {
    'owner': 'finance_team',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10)
}

# 2. Declare the scheduler pipeline
with DAG(
    dag_id='monorepo_weekly_plaid_sync',
    default_args=default_args,
    description='Triggers a transient k3s pod to run the monorepo Plaid ETL script weekly',
    schedule='@weekly',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['personal_app', 'k3s', 'monorepo'],
) as dag:

    # 3. Define the transient execution worker pod
    run_plaid_sync_worker = KubernetesPodOperator(
        task_id='execute_plaid_sync_script',
        namespace='airflow',               # The k3s namespace where the pod will execute

        # Point to your local k3s registry image built from your monorepo root
        image='localhost:5000/monorepo-app:latest',
        image_pull_policy='Always',
        name='plaid-etl-runner',

        # OVERRIDE the container command to invoke your isolated package runner
        cmds=["uv", "run", "python"],
        arguments=["src/airflow_etl/run_sync.py"],

        # 4. Inject your cluster secrets cleanly into the container's environment
        env_from=[
            k8s.V1EnvFromSource(
                secret_ref=k8s.V1SecretEnvSource(name='finance-app-secrets')
            )
        ],

        # 5. Restrict resource footprints to avoid memory leaks on your mini-PC
        container_resources=k8s.V1ResourceRequirements(
            requests={"cpu": "200m", "memory": "256Mi"},
            limits={"cpu": "500m", "memory": "512Mi"}
        ),

        # Automatically streams your script's print statements to the Airflow UI
        get_logs=True,
        # Automatically cleans up and destroys the Pod on completion to save RAM
        is_delete_operator_pod=True
    )
