import streamlit as st
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from google.cloud import bigquery

# Establece la variable de entorno con la ruta a tu archivo de credenciales JSON
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credenciales.json'

# Configura la conexión a BigQuery
client = bigquery.Client(location="us-central1")

# Verificar si el archivo existe antes de cargarlo
def load_data():
    query = """
    SELECT 
        stadium,
        name,
        avg_rating,
        num_of_reviews,
        gmap_id,
        url,
        category
    FROM 
        divine-builder-431018-g4.horizon.Google_metadata
    """
    estados = client.query(query).to_dataframe()
    return estados

# Cargar los datos y asignarlos a la variable 'estados'
estados = load_data()

# Imprimir la primera fila de los datos para verificar la carga
print(estados.head(1))

# Definir las funciones
def filter_by_city(estados, stadium):
    return estados[estados['stadium'] == stadium]

def find_similar_restaurants(name, stadium, num_recommendations=5):
    city_restaurants = filter_by_city(estados, stadium)
    
    if name not in city_restaurants['name'].values:
        raise ValueError(f"El restaurante '{name}' no existe cerca del estadio '{stadium}'.")
    
    city_restaurants = city_restaurants.drop_duplicates(subset=['name'])
    
    # Asegurarse de que no haya duplicados en el índice
    restaurant_matrix = city_restaurants.pivot_table(index='name', values=['avg_rating', 'num_of_reviews'])
    
    mlb = MultiLabelBinarizer()
    categories = mlb.fit_transform(city_restaurants['category'].apply(lambda x: x.split(',')))
    categories_df = pd.DataFrame(categories, index=city_restaurants['name'], columns=mlb.classes_)
    
    combined_matrix = pd.concat([restaurant_matrix, categories_df], axis=1)
    
    # Asegurar que el índice sea único después de la concatenación
    combined_matrix = combined_matrix[~combined_matrix.index.duplicated(keep='first')]
    
    combined_matrix_filled = combined_matrix.fillna(0)
    
    # Calcular la similitud coseno
    similarity_matrix = cosine_similarity(combined_matrix_filled)
    similarity_df = pd.DataFrame(similarity_matrix, index=combined_matrix.index, columns=combined_matrix.index)
    
    # Obtener restaurantes similares
    similar_restaurants = similarity_df[name].sort_values(ascending=False).head(num_recommendations + 1).index.tolist()
    similar_restaurants.remove(name)
    
    recommendations = estados[estados['name'].isin(similar_restaurants) & (estados['stadium'] == stadium)].drop_duplicates(subset=['name']).head(num_recommendations)
    
    return recommendations[['name', 'avg_rating', 'url', 'stadium']]

# Interfaz de usuario con Streamlit
st.title("Recomendación de Restaurantes")

# Campo de selección para estadios
stadium = st.selectbox("Selecciona el estadio", estados['stadium'].unique())

# Input field para el nombre del restaurante
name = st.text_input("Nombre del restaurante")

# Botón para obtener recomendaciones
if st.button("Obtener recomendaciones"):
    if name and stadium:
        try:
            recommendations = find_similar_restaurants(name, stadium)
            st.write(f"Recomendaciones para {name} cerca de {stadium}:")
            for _, row in recommendations.iterrows():
                st.markdown(f"- [{row['name']}]({row['url']}) - Calificación: {row['avg_rating']}")
        except ValueError as e:
            st.error(str(e))
    else:
        st.warning("Por favor, ingresa el nombre del restaurante y selecciona un estadio.")
