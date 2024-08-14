### Modelo de Machine Learning aplicado a un sistema de recomendación de locales gastronómicos.


Contexto: El objetivo del modelo (recomendar locales gastronómicos) y la metodología utilizada (KNN).

La elección de KNN como algoritmo para un modelo de recomendación de locales gastronómicos cerca de estadios de fútbol se fundamenta en varias razones:

Datos multidimensionales: Los datos de los locales gastronómicos suelen incluir múltiples características numéricas (calificación promedio, número de reseñas, distancia al estadio) y categóricas como ser el tipo de cocina. KNN es capaz de manejar eficientemente este tipo de datos.
Si un usuario busca un lugar para comer pizza cerca del estadio, es lógico recomendarle los locales que otros usuarios que han buscado lo mismo han valorado positivamente.
No es lineal: Las relaciones entre las características y la preferencia de los usuarios pueden ser no lineales. Este modelo no asume ninguna forma funcional específica para la relación entre las variables, lo que lo hace flexible para capturar patrones complejos.
Fácil de interprer: Es relativamente fácil entender cómo los locales recomendados son similares a los que otros usuarios han valorado positivamente. Esto facilita la explicación de las recomendaciones al usuario.
Es adaptable a nuevos datos sin necesidad de volver a entrenar el modelo por completo. A medida que se agregan nuevos locales o reseñas, el modelo se actualiza automáticamente.

Ajuste a las características de la aplicación:
Selección de estadio y palabra clave: El usuario puede seleccionar un estadio y una palabra clave, lo que permite personalizar las recomendaciones. El modelo puede adaptarse fácilmente a estas restricciones al buscar los vecinos más cercanos dentro del subconjunto de datos que cumple con los criterios de búsqueda, tomándose como positivos aquellos locales con una calificación promedio superior a 3,5, y poseer al menos veinte (20) reseñas.


### Experimentación:
Se establecieron como hiperparámetros a probar los valores de N : (2, 5, 9).
Las métricas utilizadas en el contexto de la recomendación de restaurantes:

Accuracy: Mide qué tan a menudo el modelo acierta al recomendar un restaurante.  
Precision: Mide qué tan confiables son las recomendaciones. Si el modelo recomienda un restaurante, es muy probable que sea bueno.  
Recall: Mide qué tan completo es el modelo. Si hay muchos restaurantes buenos, ¿el modelo los encuentra todos?    
F1-score: Nos da una idea general de lo bueno que es el modelo, considerando tanto su precisión como su capacidad para encontrar todos los restaurantes relevantes.  

Análisis de resultados:
N=2: Si bien obtuvo la mayor precisión, podría estar sobreajustado, ya que un valor de N muy bajo puede hacer que el modelo sea demasiado sensible a los datos de entrenamiento.
N=5: Este valor parece ofrecer un buen equilibrio entre precisión, recall y F1-score. La alta precisión indica que el modelo predice correctamente las clases positivas (restaurantes relevantes), mientras que el alto recall indica que el modelo identifica la mayoría de las instancias positivas. El F1-score, siendo la media armónica de precisión y recall, proporciona una medida general del rendimiento del modelo.
N=9: Si bien el recall es similar al de N=5, la precisión y el F1-score son ligeramente inferiores. Esto sugiere que un valor de N demasiado alto podría estar suavizando demasiado las decisiones del modelo.

Conclusión:
Los resultados obtenidos muestran que el valor de N=5 ofrece un equilibrio óptimo entre precisión y recall. Si bien N=2 logra una precisión ligeramente mayor, existe el riesgo de sobreajuste. Por otro lado, N=9, aunque ofrece un alto recall, presenta una ligera disminución en la precisión y el F1-score. Por lo tanto, se seleccionó N=5 como el valor óptimo para el modelo KNN, ya que permite obtener recomendaciones precisas y relevantes sin comprometer la capacidad de generalización.
