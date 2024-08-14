from airflow import DAG
from airflow.operators.python import PythonOperator
from google.cloud import bigquery
from datetime import datetime
import os

# Configuración por defecto del DAG
default_args = {
    'owner': 'airflow',  # Puedes cambiar esto si lo deseas, pero "airflow" es el valor estándar
    'start_date': datetime(2023, 1, 1),  # Cambia la fecha de inicio si es necesario
    'retries': 1,  # Número de reintentos en caso de fallo
}

# Definir la función que carga JSON a BigQuery
def load_json_to_bigquery(ds, **kwargs):


    client = bigquery.Client()

    # Define los parámetros específicos
    dataset_id = "horizon"  # Reemplaza con tu ID de dataset en BigQuery
    table_id = "Google_reviews"  # Reemplaza con tu ID de tabla en BigQuery
    gcs_uri = "gs://bucket_horizont/data/restaurants_near_stadiums.json"  # Reemplaza con la URI correcta de tu archivo JSON en GCS

    # Define la configuración del trabajo de carga
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,  # Detecta automáticamente el esquema; considera definir manualmente el esquema si es complejo
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Agrega datos a la tabla si ya existe
    )

    # Crea una referencia a la tabla
    table_ref = client.dataset(dataset_id).table(table_id)

    # Realiza la carga desde Cloud Storage a BigQuery
    load_job = client.load_table_from_uri(
        gcs_uri,
        table_ref,
        job_config=job_config
    )

    # Espera a que el trabajo de carga se complete
    load_job.result()
    print(f"Carga completa de {gcs_uri} a {dataset_id}.{table_id}.")

# Definición del DAG
with DAG(
    dag_id='Bucket_to_bigquery_manual_respaldo',  # Puedes cambiar el ID del DAG si lo deseas
    default_args=default_args,
    schedule_interval=None,  # Cambia esto si deseas programar el DAG para que se ejecute automáticamente
    catchup=False  # Evita la ejecución retroactiva si usas una fecha anterior
) as dag:

    # Tarea para cargar JSON a BigQuery
    load_json_to_bq_task = PythonOperator(
        task_id='load_json_to_bq',  # Puedes cambiar el ID de la tarea si lo deseas
        python_callable=load_json_to_bigquery,  # Llama a la función de carga
        provide_context=True  # Proporciona el contexto del DAG a la función
    )


load_json_to_bq_task
