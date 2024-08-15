
# Aplicación de Recomendación de Restaurantes

## Descripción

Esta aplicación es una herramienta interactiva desarrollada en Python usando Streamlit. Su objetivo es proporcionar recomendaciones de restaurantes cercanos a estadios, utilizando un modelo basado en similitudes coseno. Los datos son extraídos desde Google BigQuery.

## Estructura del Código

### 1. Importación de Librerías
   - **`streamlit as st`**: Streamlit se utiliza para crear la interfaz de usuario interactiva.
   - **`pandas as pd`**: Pandas se utiliza para manejar y procesar los datos en formato DataFrame.
   - **`MultiLabelBinarizer`**: De la biblioteca de `sklearn.preprocessing`, este módulo se utiliza para convertir las categorías en variables binarias (one-hot encoding).
   - **`cosine_similarity`**: De la biblioteca `sklearn.metrics.pairwise`, esta función calcula la similitud coseno entre vectores.
   - **`json`**: Se utiliza para manejar y parsear archivos JSON, en este caso, las credenciales.
   - **`google.cloud.bigquery`**: Se utiliza para interactuar con Google BigQuery.
   - **`google.oauth2.service_account`**: Se utiliza para manejar la autenticación y las credenciales con Google Cloud.

### 2. Configuración de Credenciales
   - Las credenciales de Google Cloud se leen desde los secretos de Streamlit, lo que permite la conexión segura a BigQuery.

### 3. Estilo Personalizado
   - Se utiliza la función `st.markdown` para aplicar un estilo CSS personalizado a la aplicación, incluyendo el fondo, los textos, y los botones.

### 4. Carga de Datos
   - La función `load_data()` ejecuta una consulta SQL a BigQuery para obtener los datos de restaurantes cercanos a estadios. Los datos se almacenan en un DataFrame de Pandas llamado Estados.

### 5. Funciones Principales
   - **`filter_by_city(estados, stadium)`**: Filtra los restaurantes basados en el estadio seleccionado.
   - **`find_similar_restaurants(name, stadium, num_recommendations=5)`**: Encuentra restaurantes similares al restaurante dado, dentro de la misma ciudad. Utiliza la similitud coseno entre un vector que representa características de los restaurantes (calificación, número de reseñas, y categoría).

### 6. Interfaz de Usuario
   - **Selección del Estadio**: El usuario puede seleccionar un estadio de una lista desplegable.
   - **Input del Nombre del Restaurante**: El usuario ingresa el nombre del restaurante que desea utilizar como referencia.
   - **Generación de Recomendaciones**: Al hacer clic en un botón, la aplicación genera una lista de recomendaciones de restaurantes similares al seleccionado, mostrando su nombre, calificación, y un enlace a su Google Maps.

## Detalles Técnicos

- **Autenticación con Google Cloud**: Se realiza mediante el uso de `service_account.Credentials.from_service_account_info`, que toma las credenciales en formato JSON. Esto permite a la aplicación conectarse y realizar consultas a BigQuery.
  
- **Similitud Coseno**: Este algoritmo calcula la similitud entre restaurantes basándose en sus características. La similitud coseno es adecuada para este caso ya que mide la similitud de vectores independientemente de su magnitud.

- **Pivot Table y One-Hot Encoding**: El DataFrame se organiza en una tabla pivotada para permitir la comparación de características numéricas (`avg_rating`, `num_of_reviews`). Las categorías de los restaurantes son convertidas en vectores binarios para que puedan ser incluidas en el cálculo de similitud.


## Conclusión

Este código proporciona una funcionalidad interesante para recomendar restaurantes basados en similitudes calculadas con la similitud coseno. Es un ejemplo excelente de cómo se pueden combinar diferentes herramientas y técnicas, como Streamlit, BigQuery, y Machine Learning, para crear una aplicación web interactiva y útil.
