
Ingeniería de Datos para el Análisis de Restaurantes en Cercanía de Estadios de la MLS

Este documento detalla el proceso de ingeniería de datos para nuestro proyecto, que abarca la definición del alcance, el procesamiento de datos, y la construcción de la canalización de datos (Pipeline).

1. Alcance del Proyecto

El objetivo de este proyecto es realizar un análisis exhaustivo de la oferta gastronómica en las cercanías de los estadios de la Major League Soccer (MLS). Con el creciente interés en la MLS impulsado por la llegada de grandes figuras del fútbol mundial, los estadios se han convertido en epicentros de actividad no solo durante los partidos, sino también en eventos deportivos y de entretenimiento. Este proyecto busca identificar oportunidades de negocio y recomendar inversiones estratégicas en la industria gastronómica en estas áreas de alta afluencia.

Para establecer el alcance del proyecto, se emplearon técnicas avanzadas de análisis de datos y búsquedas focalizadas. Esto nos permitió centrar nuestros esfuerzos en mercados con el mayor potencial de crecimiento y retorno de inversión.

2. Procesamiento de Datos

2.1. Fuentes de Datos

Nuestras fuentes de datos incluyen:

	•	Google y Yelp: Datos extraídos en formato JSON.
	•	Transfermarkt: Datos recopilados mediante web scraping.
	•	API de Google Place: Datos actualizados diariamente.

Estos datos se sometieron a un proceso riguroso de análisis y limpieza para garantizar su calidad y compatibilidad para el análisis exploratorio de datos (EDA). Como resultado, se generaron las siguientes tablas principales:

	•	Google_Metadata: Contiene información relevante sobre los restaurantes extraída de Google.
	•	Google_Reviews: Reseñas de clientes obtenidas de Google.
	•	Stadium: Información detallada sobre los estadios de la MLS y sus ubicaciones.

Cada tabla fue procesada para asegurar la coherencia en los nombres de las columnas, eliminación de registros duplicados, y el tratamiento de valores faltantes.

3. Unificación de Datos

Para optimizar el análisis exploratorio y el desarrollo de modelos de aprendizaje automático, se realizó una unificación de los conjuntos de datos de Google, enfocándonos particularmente en las reseñas de los usuarios. Este conjunto de datos unificado proporciona una vista integral de la experiencia gastronómica en las cercanías de los estadios. La documentación detallada del proceso ETL se encuentra en el apartado “ETL Unificación”.

4. Visualización de Datos y Diccionarios

Con el fin de mejorar la comprensión de las relaciones entre las diferentes entidades en nuestro conjunto de datos, se desarrolló un Diagrama de Relación de Entidades (DER). Este diagrama visualiza las interconexiones entre los datos de los restaurantes, las reseñas y los estadios.

Además, se elaboró un Diccionario de Datos completo, que documenta cada campo en los conjuntos de datos, facilitando la interpretación y uso en análisis posteriores.

5. Pipeline de Datos

El pipeline de datos, ilustrado en el siguiente diagrama, describe el flujo de datos desde su ingesta inicial hasta su análisis y modelado final. Este pipeline está diseñado para ser escalable, eficiente y automatizado, asegurando la integridad y disponibilidad de los datos en cada etapa del proceso.

6. Descripción del Proceso de Ingeniería de Datos

6.1. Recepción de Datos:

	•	Se reciben datos en bruto provenientes de Google Maps, la API de Google Place y mediante Web Scraping desde Transfermarkt.
	•	Los datos son almacenados inicialmente en Google Cloud Storage.

6.2. Orquestación y Transformación:

	•	Utilizamos Google Cloud Composer integrado con Airflow para la orquestación del pipeline.
	•	Los DAGs (Directed Acyclic Graphs) en Airflow automatizan la extracción, transformación y carga (ETL) de los datos.
	•	Se realizan las transformaciones necesarias, como la normalización de datos, manejo de nulos, y conversión de tipos de datos.
	•	Los datos transformados se almacenan nuevamente en Google Cloud Storage antes de ser cargados en BigQuery.

6.3. Disponibilidad de Datos:

	•	Las tablas transformadas y almacenadas en Google BigQuery se ponen a disposición para análisis exploratorio (EDA), modelado ML , y visualización a través de herramientas como Power BI.
	•	Los datos están optimizados para consultas rápidas y análisis ad-hoc.
