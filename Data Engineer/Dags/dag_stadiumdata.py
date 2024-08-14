from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago
from google.cloud import storage
import pandas as pd
from io import StringIO

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def download_from_gcs(bucket_name, source_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    content = blob.download_as_text()
    return content

def process_data(**kwargs):
    bucket_name = 'bucket_horizont'
    source_blob_name = 'stadium_data.csv'
    
    content = download_from_gcs(bucket_name, source_blob_name)
    
    df_estadios = pd.read_csv(StringIO(content))
    
    df_estadios['Equipo'] = df_estadios['Equipo'].str.strip().str.lower()
    df_estadios = df_estadios.reset_index(drop=True)
    df_estadios = df_estadios.drop_duplicates(subset='Equipo', keep='first')
    df_estadios.dropna(subset=['city'], inplace=True)
    
    df_stadiums = pd.DataFrame({
        'stadium_id': range(1, len(df_estadios) + 1),
        'team': df_estadios['Equipo'],
        'name': df_estadios['Nombre Estadio'],
        'address': df_estadios['address'],
        'city': df_estadios['city'],
        'latitude': df_estadios['lat'],
        'longitude': df_estadios['lng'],
        'capacity': df_estadios['Capacidad']})
    
    df_stadiums['team'] = df_stadiums['team'].str.title()
    
    output_file = '/tmp/processed_stadiums.csv'
    df_stadiums.to_csv(output_file, index=False)
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob('processed_data/processed_stadiums.csv')
    blob.upload_from_filename(output_file)

with DAG(
    dag_id='stadium_data_etl_to_bq',
    default_args=default_args,
    description='ETL pipeline for stadium data and load to BigQuery',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
) as dag:

    start = DummyOperator(task_id='start')
    
    wait_for_file = GCSObjectExistenceSensor(
        task_id='wait_for_file',
        bucket='bucket_horizont',
        object='stadium_data.csv',
        mode='poke',
        timeout=600,
        poke_interval=60,
    )
    
    process_stadiums = PythonOperator(
        task_id='process_stadiums',
        python_callable=process_data,
    )
    
    load_to_bigquery = GCSToBigQueryOperator(
        task_id='load_to_bigquery',
        bucket='bucket_horizont',
        source_objects=['processed_data/processed_stadiums.csv'],
        destination_project_dataset_table='divine-builder-431018-g4.horizon.stadiums',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        source_format='CSV',
        autodetect=True,
        skip_leading_rows=1,
    )

    end = DummyOperator(task_id='end')

    start >> wait_for_file >> process_stadiums >> load_to_bigquery >> end