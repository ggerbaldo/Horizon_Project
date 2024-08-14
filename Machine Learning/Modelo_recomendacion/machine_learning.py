import streamlit as st
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from google.cloud import bigquery 
from google.oauth2 import service_account

# Leer las credenciales desde los secretos de Streamlit
credentials_json = st.secrets["GOOGLE_CREDENTIALS"]

# Configurar la conexión a BigQuery usando las credenciales desde el secreto
credentials = service_account.Credentials.from_service_account_info(credentials_json)
client = bigquery.Client(credentials=credentials, location="us-central1")

# URL de la imagen de fondo
background_image_url = "https://cdn.prod.website-files.com/5ddedd0e3047ab406ee3c37e/64aeef75a9175bfa44144333_Stadium_8.0.jpg"

# Agregar estilo personalizado
st.markdown(f"""
    <style>
        .stApp {{
            background-image: url("{background_image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #E0E0E0;
            opacity: 0.75; /* Opacidad de la imagen de fondo */
        }}
        .title {{
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            padding-top: 20px;
            color: #FFFFFF;
            text-shadow: 2px 2px 6px #000;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #FFFFFF;
            text-shadow: 2px 2px 6px #000;
        }}
        .stTextInput > label {{
            color: #FFFFFF;
        }}
        .stSelectbox > label {{
            color: #FFFFFF;
        }}
        .stTextInput>div>input {{
            color: #000000;
            background-color: #FFFFFF;
        }}
        .stSelectbox>div>input {{
            color: #000000;
            background-color: #FFFFFF;
        }}
        .restaurant-card {{
            border: 1px solid #FFD700;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            background-color: rgba(0, 0, 0, 0.6);
            color: #FFFFFF;
            text-shadow: 1px 1px 3px #000;
        }}
        .restaurant-card h4 {{
            margin: 0;
            padding-bottom: 10px;
            font-size: 1.5em;
            font-weight: bold;
        }}
        .restaurant-card p {{
            margin: 0;
            padding-bottom: 10px;
            font-size: 1.2em;
        }}
        .restaurant-card a {{
            color: #1E90FF;
            text-decoration: none;
        }}
        .stButton>button {{
            background-color: #FF4500;
            color: white;
            border: 2px solid #FF4500;
            border-radius: 4px;
            padding: 10px 20px;
            font-size: 1em;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: background-color 0.3s ease;
        }}
        .stButton>button:hover {{
            background-color: black;
            color: #FF4500;
        }}
        .stMarkdown {{
            color: #FFFFFF;
            font-weight: bold;
        }}
    </style>
""", unsafe_allow_html=True)

# Cargar los datos
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

estados = load_data()

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

# Aplicar la función title() al nombre del restaurante
name = name.title()

# Botón para obtener recomendaciones
if st.button("Obtener recomendaciones"):
    if name and stadium:
        try:
            recommendations = find_similar_restaurants(name, stadium)
            st.markdown(f"<div class='stMarkdown'>Recomendaciones para {name} cerca de {stadium}:</div>", unsafe_allow_html=True)
            for _, row in recommendations.iterrows():
                st.markdown(f"""
                <div class="restaurant-card">
                    <h4>{row['name']}</h4>
                    <p>Calificación: {row['avg_rating']}</p>
                    <p><a href="{row['url']}">Visitar</a></p>
                </div>
                """, unsafe_allow_html=True)
        except ValueError as e:
            st.error(str(e))
    else:
        st.warning("Por favor, ingresa el nombre del restaurante y selecciona un estadio.")