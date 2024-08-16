### Modelo de Machine Learning K-Nearest Neighbors aplicado a un sistema de recomendación de locales gastronómicos.

[Ingreso al modelo de recomendación](https://horizon-project-modelo-knn.streamlit.app/)

### Contexto: 
Como parte del análisis de los locales gastronómicos en las cercanías de los estadios de fútbol de la Major League Soccer (MLS), el objetivo de trabajar sobre un modelo de machine learning es proporcionar al cliente una herramienta de recomendación que devuelva una lista con las mejores experiencias gastronómicas cercanas, basado en el tipo de cocina y la calificación promedio del público.

La elección de K-Nearest Neighbors (KNN) como modelo para el sistema de recomendación se fundamenta en varias razones:

Datos multidimensionales: Los datos de los locales gastronómicos suelen incluir múltiples características numéricas (calificación promedio, número de reseñas, distancia al estadio) y categóricas como ser el tipo de cocina. KNN es capaz de manejar eficientemente este tipo de datos. Si un usuario busca un lugar para comer pizza cerca del estadio, es lógico recomendarle los locales que otros usuarios que han buscado lo mismo han valorado positivamente.
No es lineal: Las relaciones entre las características y la preferencia de los usuarios pueden ser no lineales. Este modelo no asume ninguna forma funcional específica para la relación entre las variables, lo que lo hace flexible para capturar patrones complejos.
Fácil de interpretar: Es relativamente fácil entender cómo los locales recomendados son similares a los que otros usuarios han valorado positivamente. Esto facilita la explicación de las recomendaciones al usuario.
Es adaptable a nuevos datos sin necesidad de volver a entrenar el modelo por completo. A medida que se agregan nuevos locales o reseñas, el modelo se puede entrenar y actualizar automáticamente, según el requerimiento del cliente.

Ajuste a las características de la aplicación:
Selección de estadio y palabra clave: El usuario puede seleccionar un estadio y una palabra clave, lo que permite personalizar las recomendaciones. El modelo puede adaptarse fácilmente a estas restricciones al buscar los vecinos más cercanos dentro del subconjunto de datos que cumple con los criterios de búsqueda, tomándose como positivos aquellos locales con una calificación promedio superior a 3,5, y poseer al menos veinte (20) reseñas.

### Entrenamiento del modelo:

Entrenar un modelo de machine learning, en este caso un modelo KNN (K-Nearest Neighbors), es el proceso mediante el cual el modelo aprende a realizar predicciones basadas en un conjunto de datos de entrenamiento. El objetivo es que el modelo aprenda a identificar patrones y relaciones en los datos, de manera que pueda aplicar ese conocimiento para hacer predicciones en nuevos datos que no ha visto antes.
Se divide el dataset en 80% para entrenamiento y 20% para prueba a efectos de ayudar a garantizar que el modelo no solo funcione bien en los datos de entrenamiento, sino que también tenga la capacidad de generalizar y hacer buenas predicciones en datos nuevos.

### Experimentación:
Se establecieron como hiperparámetros a analizar los valores de K: (2, 5, 9).
Las métricas utilizadas en el contexto de la recomendación de restaurantes son:

**Accuracy**: Mide qué tan a menudo el modelo acierta al recomendar un restaurante.  
**Precisión**: Mide qué tan confiables son las recomendaciones. Si el modelo recomienda un restaurante, es muy probable que sea bueno.  
**Recall**: Mide qué tan completo es el modelo. Si hay muchos restaurantes buenos, ¿el modelo los encuentra todos?    
**F1-score**: Nos da una idea general de lo bueno que es el modelo, considerando tanto su precisión como su capacidad para encontrar todos los restaurantes relevantes.  

### Análisis de resultados:
**K=2**: Si bien obtuvo la mayor precisión, podría estar sobreajustado, ya que un valor de N muy bajo puede hacer que el modelo sea demasiado sensible a los datos de entrenamiento.  
**K=5**: Este valor parece ofrecer un buen equilibrio entre precisión, recall y F1-score. La alta precisión indica que el modelo predice correctamente las clases positivas (restaurantes relevantes), mientras que el alto recall indica que el modelo identifica la mayoría de las instancias positivas. El F1-score, siendo la media armónica de precisión y recall, proporciona una medida general del rendimiento del modelo.  
**K=9**: Si bien el recall es similar al de N=5, la precisión y el F1-score son ligeramente inferiores. Esto sugiere que un valor de N demasiado alto podría estar suavizando demasiado las decisiones del modelo.  

### Conclusión:
Los resultados obtenidos muestran que el valor de N=5 ofrece un equilibrio óptimo entre precisión y recall. Si bien N=2 logra una precisión ligeramente mayor, existe el riesgo de sobreajuste. Por otro lado, N=9, aunque ofrece un alto recall, presenta una ligera disminución en la precisión y el F1-score. Por lo tanto, se seleccionó N=5 como el valor óptimo para el modelo KNN, ya que permite obtener recomendaciones precisas y relevantes sin comprometer la capacidad de generalización.
