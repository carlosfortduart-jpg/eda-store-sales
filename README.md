# eda-store-sales
Proyecto EDA

Este proyecto realiza un análisis exploratorio de datos (EDA) sobre un conjunto de ventas de una tienda minorista. El objetivo principal es comprender la calidad del dataset, aplicar un proceso completo de limpieza y transformación, y extraer insights relevantes sobre ventas, categorías, métodos de pago y comportamiento de los clientes.

# Resumen del análisis realizado

## Evaluación de la calidad del dataset
Identificamos valores nulos, inconsistencias y posibles duplicados. Revisamos todas las columnas para evaluar su completitud y estructura.

## Proceso de limpieza (Data Cleaning)
- Imputación de valores faltantes mediante reglas basadas en negocio y estadística.
- Normalización y estandarización del nombre de columnas.
- Generación de una versión final depurada del dataset (retail_store_sales_clean.csv).

## Análisis exploratorio (EDA)
Analizamos patrones de comportamiento en las ventas, incluyendo:
- Distribución de variables numéricas.
- Relación entre métodos de pago y ventas.
- Ingresos por categoría.
- Análisis temporal de ventas mensuales.
- Correlaciones entre variables numéricas.

## Visualizaciones clave
Generamos gráficos para interpretar de manera clara los hallazgos más relevantes en:
-Categorías de productos.
-Métodos de pago.
-Tendencias temporales.

Estas visualizaciones permiten identificar tendencias, estacionalidades, correlaciones y comportamiento anómalo en los datos.

## Exportación del dataset limpio
El dataframe procesado se guarda en la carpeta /data/ para facilitar futuros análisis o construcción de modelos.

