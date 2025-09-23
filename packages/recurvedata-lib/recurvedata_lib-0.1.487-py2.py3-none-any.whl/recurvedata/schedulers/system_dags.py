import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

from recurvedata.schedulers.consts import SYSTEM_SYNC_STATUS_DAG_ID


def create_system_dags():
    return [
        create_sync_status_dag(),
    ]


def _prepare_bash_env():
    dct = {}
    for key, val in os.environ.items():
        if key.startswith("RECURVE__"):
            dct[key] = val
        elif key.startswith("AIRFLOW"):
            dct[key] = val
        elif key in (
            "PATH",
            "PYENV_ROOT",
        ):
            dct[key] = os.environ[key]
    return dct


def create_sync_status_dag():
    start_date = datetime(2024, 8, 5)
    default_args = {
        "depends_on_past": False,
        "retries": 150,
        "retry_delay": timedelta(seconds=10),
        "priority_weight": 100,
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(seconds=30),
    }
    dag = DAG(
        SYSTEM_SYNC_STATUS_DAG_ID,
        default_args=default_args,
        description="A DAG to sync db status",
        schedule_interval="0 */6 * * *",  # Run every 6 hours
        start_date=start_date,
        catchup=False,
        dagrun_timeout=timedelta(minutes=60 * 6),
        max_active_runs=1,  # todo: retry may delay the future dag_run
        is_paused_upon_creation=False,
    )

    BashOperator(
        task_id="sync_status",
        bash_command="recurve_scheduler sync-task-status --interval=5",
        dag=dag,
        env=_prepare_bash_env(),
    )
    return dag
