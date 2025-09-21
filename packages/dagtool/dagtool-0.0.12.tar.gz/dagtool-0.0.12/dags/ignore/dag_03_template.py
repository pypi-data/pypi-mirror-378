from pathlib import Path

from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

from dagtool.models.dag import Variable
from dagtool.tasks import DebugOperator
from ignore.utils import sequence_pool

dag = DAG(
    dag_id="origin_template",
    start_date=days_ago(2),
    catchup=False,
    tags=["origin"],
    doc_md="doc.md",
    user_defined_macros={
        "custom_macros": "foo",
        "vars": Variable.from_path_with_key(
            Path(__file__).parent, key="template"
        ).get,
    },
)
test = EmptyOperator(task_id="test", dag=dag)
debug = DebugOperator(
    task_id="debug",
    dag=dag,
    debug={
        "test": "Hello World",
        "common": "{{ custom_macros }}",
        "variable_1": "{{ vars('schedule_interval') }}",
        "variable_2": "{{ vars('project_id') }}",
    },
    pool=sequence_pool.pool,
)
debug.set_upstream(test)
