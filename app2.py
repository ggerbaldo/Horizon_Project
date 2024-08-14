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
                    st.markdown(f"*{index}. {row['name']}* - Rating: {row['avg_rating']}")
                    st.markdown(f"[Ir a Googlemap]({row['url']})")
                    
        else:
            st.write("Por favor, ingrese tanto una palabra clave como un nombre de estadio.")

if __name__ == "__main__":
    main()