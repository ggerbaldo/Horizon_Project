from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from google.cloud import bigquery
from datetime import datetime, timedelta
import requests
import pandas as pd
import time
import os

# Configuración por defecto del DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def get_places(api_key, location, radius, place_type, next_page_token=None):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': location,
        'radius': radius,
        'type': place_type,
        'key': api_key
    }
    if next_page_token:
        params['pagetoken'] = next_page_token
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener lugares: {e}")
        return None

def get_place_details(api_key, place_id, reviews_sort='newest'):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,place_id,geometry/location,'
                  'rating,user_ratings_total,url,reviews',
        'reviews_sort': reviews_sort,
        'key': api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener detalles del lugar: {e}")
        return None

def extract_and_save_data(**kwargs):
    api_key = kwargs['api_key']
    stadiums = kwargs['stadiums']
    radius = 10000  # 10 km
    place_type = "restaurant"

    results = []

    for stadium in stadiums:
        location = f"{stadium['lat']},{stadium['lng']}"
        next_page_token = None
        while True:
            places = get_places(api_key, location, radius, place_type, next_page_token)
            if not places:
                break
            for place in places.get('results', []):
                place_id = place.get('place_id')
                if place_id:
                    details = get_place_details(api_key, place_id, reviews_sort='newest')
                    if details and 'result' in details:
                        result = {
                            'stadium': stadium.get('name', 'SinDato'),
                            'name': details['result'].get('name', 'SinDato'),
                            'address': details['result'].get('formatted_address', 'SinDato'),
                            'gmap_id': details['result'].get('place_id', 'SinDato'),
                            'latitude': details['result']['geometry']['location'].get('lat', 0.0),
                            'longitude': details['result']['geometry']['location'].get('lng', 0.0),
                            'avg_rating': details['result'].get('rating', 0.0),
                            'num_of_reviews': float(details['result'].get('user_ratings_total', 0)),
                            'url': details['result'].get('url', 'SinDato'),
                            'reviews': details['result'].get('reviews', [])
                        }
                        results.append(result)
            
            next_page_token = places.get('next_page_token')
            if not next_page_token:
                break
            time.sleep(2)

    processed_results = []
    for result in results:
        reviews = result.pop('reviews', [])
        if reviews:
            for review in reviews:
                review_data = {
                    'review_author': review.get('author_name', 'SinDato'),
                    'review_rating': float(review.get('rating', 0)),
                    'review_text': review.get('text', 'SinDato'),
                    'review_date': datetime.utcfromtimestamp(review.get('time', 0)).strftime('%Y-%m-%d')
                }
                full_result = {**result, **review_data}
                processed_results.append(full_result)
        else:
            processed_results.append({
                **result,
                'review_author': 'SinDato',
                'review_rating': 0.0,
                'review_text': 'SinDato',
                'review_date': '1970-01-01'
            })

    if processed_results:
        df = pd.DataFrame(processed_results)
        df.to_json('/tmp/restaurants_near_stadiums.json', orient='records', lines=True)
        print("Datos guardados en '/tmp/restaurants_near_stadiums.json'")
    else:
        print("No se encontraron resultados.")

def load_json_to_bigquery(ds, **kwargs):
    client = bigquery.Client()

    dataset_id = "horizon"
    table_id = "Google_reviews"
    gcs_uri = "gs://bucket_horizont/data/restaurants_near_stadiums.json"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    table_ref = client.get_table(f"{dataset_id}.{table_id}")

    load_job = client.load_table_from_uri(
        gcs_uri,
        table_ref,
        job_config=job_config
    )

    load_job.result()
    print(f"Carga completa de {gcs_uri} a {dataset_id}.{table_id}.")

# Definición del DAG
dag = DAG(
    'Automatizacion_api_to_bigquery',
    default_args=default_args,
    description='Un DAG combinado para extraer datos, cargarlos a GCS y luego a BigQuery',
    schedule_interval='@weekly',
    catchup=False
)

# Tareas del DAG
extract_task = PythonOperator(
    task_id='extract_and_save_data',
    python_callable=extract_and_save_data,
    op_kwargs={
        'api_key': 'AIzaSyC2PrjEiT-XZVT10BIhNAGRSWsvImhjQws',
        'stadiums': [
            {"name": "Gillette Stadium", "lat": 42.0909, "lng": -71.2600},
            # Añadir otros estadios aquí...
        ]
    },
    dag=dag,
)

upload_to_gcs = LocalFilesystemToGCSOperator(
    task_id='upload_to_gcs',
    src='/tmp/restaurants_near_stadiums.json',
    dst='data/restaurants_near_stadiums.json',
    bucket='bucket_horizont',
    dag=dag,
)

load_json_to_bq_task = PythonOperator(
    task_id='load_json_to_bq',
    python_callable=load_json_to_bigquery,
    provide_context=True,
    dag=dag
)

# Configuración de dependencias
extract_task >> upload_to_gcs >> load_json_to_bq_task
