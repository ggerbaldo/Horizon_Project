from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import requests
import pandas as pd
import time
from datetime import datetime
import os

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
                            'stadium': stadium['name'],
                            'name': details['result'].get('name'),
                            'address': details['result'].get('formatted_address'),
                            'gmap_id': details['result'].get('place_id'),
                            'latitude': details['result']['geometry']['location'].get('lat'),
                            'longitude': details['result']['geometry']['location'].get('lng'),
                            'avg_rating': details['result'].get('rating'),
                            'num_of_reviews': details['result'].get('user_ratings_total'),
                            'url': details['result'].get('url'),
                            'reviews': details['result'].get('reviews')
                        }
                        results.append(result)
            
            next_page_token = places.get('next_page_token')
            if not next_page_token:
                break
            time.sleep(2)

    # Procesar resultados para incluir reseñas
    processed_results = []
    for result in results:
        reviews = result.pop('reviews', [])
        if reviews:
            for review in reviews:
                review_data = {
                    'review_author': review.get('author_name'),
                    'review_rating': review.get('rating'),
                    'review_text': review.get('text'),
                    'review_date': datetime.utcfromtimestamp(review.get('time')).strftime('%Y-%m-%d')
                }
                full_result = {**result, **review_data}
                processed_results.append(full_result)
        else:
            processed_results.append(result)

    if processed_results:
        df = pd.DataFrame(processed_results)
        df.to_json('/tmp/restaurants_near_stadiums_new.json', orient='records', lines=True)
        print("Datos guardados en '/tmp/restaurants_near_stadiums_new.json'")
    else:
        print("No se encontraron resultados.")

def process_and_remove_duplicates(**kwargs):
    bucket_name = 'bucket_horizont'
    file_path_old = 'data/restaurants_near_stadiums.json'
    file_path_new = '/tmp/restaurants_near_stadiums_new.json'
    file_path_processed = '/tmp/restaurants_near_stadiums_processed.json'

    # Descargar el archivo antiguo desde GCS
    if os.path.exists('/tmp/restaurants_near_stadiums.json'):
        df_old = pd.read_json('/tmp/restaurants_near_stadiums.json', orient='records', lines=True)
    else:
        df_old = pd.DataFrame()  # Crear un DataFrame vacío si no existe el archivo

    df_new = pd.read_json(file_path_new, orient='records', lines=True)
    
    # Combinar y eliminar duplicados
    df_combined = pd.concat([df_old, df_new]).drop_duplicates()
    
    # Guardar el archivo procesado
    df_combined.to_json(file_path_processed, orient='records', lines=True)
    print("Datos procesados y guardados en '/tmp/restaurants_near_stadiums_processed.json'")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'Reviews_api_incremental_historico',
    default_args=default_args,
    description='Archivo historico contiene todas las reviews sin duplicados extraidas desde API',
    schedule_interval='@weekly',  # Configura el DAG para que se ejecute una vez a la semana
    start_date=days_ago(1),
    tags=['example'],
)

download_from_gcs = GCSToLocalFilesystemOperator(
    task_id='download_from_gcs',
    bucket='bucket_horizont',
    object_name='data/restaurants_near_stadiums.json',
    filename='/tmp/restaurants_near_stadiums.json',
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract_and_save_data',
    python_callable=extract_and_save_data,
    op_kwargs={
        'api_key': 'AIzaSyC2PrjEiT-XZVT10BIhNAGRSWsvImhjQws',
        'stadiums': [
            {"name": "Audi Field", "lat": 38.8737, "lng": -77.0020},
            # Añadir otros estadios aquí...
        ]
    },
    dag=dag,
)

process_and_remove_duplicates_task = PythonOperator(
    task_id='process_and_remove_duplicates',
    python_callable=process_and_remove_duplicates,
    dag=dag,
)

upload_to_gcs = LocalFilesystemToGCSOperator(
    task_id='upload_to_gcs',
    src='/tmp/restaurants_near_stadiums_processed.json',
    dst='dataincremental/restaurants_near_stadiums.json',
    bucket='bucket_horizont',
    dag=dag,
)

download_from_gcs >> extract_task >> process_and_remove_duplicates_task >> upload_to_gcs
