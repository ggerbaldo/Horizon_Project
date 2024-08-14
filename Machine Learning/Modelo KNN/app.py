import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from scipy.sparse import hstack
import streamlit as st
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import os
from google.cloud import bigquery
from google.oauth2 import service_account

#Leer las credenciales desde los secretos de Streamlit
credentials_json = st.secrets["GOOGLE_CREDENTIALS"]

#Configurar la conexión a BigQuery usando las credenciales desde el secreto
credentials = service_account.Credentials.from_service_account_info(credentials_json)
client = bigquery.Client(credentials=credentials, location="us-central1")

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)

# URL de la imagen de fondo
background_image_url = "https://github.com/Pabloclementi/test/blob/main/ac515990-1f33-47ca-bdff-a0c7e85dbd05.jpeg?raw=true"

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
        a.review_text,
        a.stadium,
        a.num_of_reviews,
        a.url,
        a.avg_rating,
        b.category,
        a.name
    FROM 
    divine-builder-431018-g4.horizon.Google_reviews AS a
    INNER JOIN 
    divine-builder-431018-g4.horizon.Google_metadata AS b
    ON 
    a.gmap_id= b.gmap_id
    ORDER BY
    RAND()
    LIMIT 80000;  # Limitar a 1000 observaciones para la demostración en esta sección del código
    """
    test = client.query(query).to_dataframe()
    return test

# Cargar los datos en la variable global
test = load_data()

# Función para preprocesar el texto
def preprocess_text(text):
    if pd.isna(text):
        return ""
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())  # Convertir a minúsculas
    words = [lemmatizer.lemmatize(word) for word in words if word.isalnum() and word not in stop_words]
    return ' '.join(words)

# Cargar los modelos entrenados y datos
def load_data_and_models():
    vectorizer = joblib.load('vectorizer.pkl')
    scaler = joblib.load('scaler.pkl')
    knn_model = joblib.load('knn_model.pkl')
    # Retornar los modelos y los datos cargados previamente
    return vectorizer, scaler, knn_model, test

def main():
    st.title("Recomendación de locales gastronómicos - Modelo KNN")

    vectorizer, scaler, knn_model, test = load_data_and_models()

    # Extraer la lista de estadios únicos
    stadiums = test['stadium'].unique().tolist()
    stadiums.sort()  # Ordenar la lista alfabéticamente
    
    # Lista desplegable de estadios
    stadium_name = st.selectbox("Seleccione un estadio:", stadiums)

    keyword = st.text_input("Ingrese una clave (e.g., pizza):", "").strip().lower()  # Convertir a minúsculas

    if st.button("Ver recomendaciones"):
        if keyword and stadium_name:
            # Convertir 'stadium' a minúsculas
            test['stadium'] = test['stadium'].str.lower()
            
            # Filtrar los datos
            filtered_data = test[
                (test['category'].apply(lambda x: any(keyword in cat.lower() for cat in x.split(', ')))) |
                (test['review_text'].str.lower().str.contains(keyword, na=False)) &
                (test['stadium'] == stadium_name)
            ]

            if filtered_data.empty:
                st.write("No se encontraron locales que coincidan con los parámetros especificados.")
            else:
                filtered_data['comentario_preprocesado'] = filtered_data['review_text'].apply(preprocess_text)
                X_text_new = vectorizer.transform(filtered_data['comentario_preprocesado'])
                X_num_new = scaler.transform(filtered_data[['num_of_reviews', 'avg_rating']])
                X_new = hstack([X_text_new, X_num_new])

                n_neighbors = 5
                unique_locales = pd.DataFrame()

                while len(unique_locales) < 5 and n_neighbors <= len(filtered_data):
                    distances, indices = knn_model.kneighbors(X_new, n_neighbors=n_neighbors)
                    indices = indices.flatten()
                    valid_indices = [i for i in indices if i < len(filtered_data)]
                    closest_locales = filtered_data.iloc[valid_indices][['name', 'avg_rating', 'url']]
                    unique_locales = pd.concat([unique_locales, closest_locales]).drop_duplicates().sort_values(by=['avg_rating'], ascending=[False])
                    n_neighbors += 1

                top_5_closest_names = unique_locales.head(5).reset_index(drop=True)
                top_5_closest_names.index += 1



                for index, row in top_5_closest_names.iterrows():
                    st.markdown(f"""
                        <div class="restaurant-card">
                            <h4>{index}. {row['name']}</h4>
                            <p>Rating: {row['avg_rating']}</p>
                            <p><a href="{row['url']}" target="_blank">Ir a Googlemap</a></p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("Por favor, ingrese tanto una palabra clave como un nombre de estadio.")

if __name__ == "__main__":
    main()
