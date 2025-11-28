#-----------ESTRUCTURA DEL DATASET--------------------------------------------------------
def ver_estructura(df):
    """
    Muestra la forma del DataFrame, sus primeras filas,
    la información de tipos y el conteo de nulos.
    """
    print("Shape (filas, columnas):", df.shape)

    # Primeras 10 filas
    display(df.head(10))

    # Información del DataFrame
    df.info()
  
#-----------RESUMEN VARIABLES CATEGÓRICAS Y CUANTITATIVAS--------------------------------------------------------
def resumen_num_cat(df):
    """
    Muestra un resumen exploratorio de:
    - Variables numéricas (describe + rango)
    - Cardinalidad de todas las columnas
    - Top valores de columnas categóricas
    """

    import pandas as pd

    print("=== RESUMEN VARIABLES NUMÉRICAS ===")
    numeric_cols = df.select_dtypes(include=['int64', 'float64'])
    numeric_summary = numeric_cols.describe().T
    numeric_summary["range"] = numeric_summary["max"] - numeric_summary["min"]
    display(numeric_summary)

    print("\n=== CARDINALIDAD (VALORES ÚNICOS) ===")
    unique_counts = pd.DataFrame(df.nunique(dropna=False), columns=['n_unique']).sort_values(
        'n_unique', ascending=False)
    display(unique_counts.head(40))

    print("\n=== TOP VALORES VARIABLES CATEGÓRICAS ===")
    non_num_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    for col in non_num_cols:
        print(f"\nColumna: {col} — Unique: {df[col].nunique(dropna=False)} — Nulos: {df[col].isnull().sum()}")
        print(df[col].value_counts(dropna=False).head(20).to_string())

#-----------EVALUACIÓN DATOS --------------------------------------------------------

def calidad_datos(df, numeric_cols=None):
    """
    Evalúa la calidad de los datos mediante:
    - Valores nulos
    - Filas duplicadas
    - Inconsistencias en columnas tipo Total = Precio * Cantidad (si existen)
    - Valores negativos en columnas numéricas
    - Detección de outliers con IQR

    Parámetros:
        df: DataFrame a analizar
        numeric_cols: lista opcional de columnas numéricas para análisis de outliers
    """

    import pandas as pd
    import numpy as np

    print("=== NULOS ===")
    missing = pd.DataFrame(df.isnull().sum(), columns=['missing_count'])
    missing['missing_pct'] = (missing['missing_count'] / len(df)) * 100
    display(missing.sort_values('missing_pct', ascending=False).head(30))

    print("\n=== DUPLICADOS ===")
    dup_count = df.duplicated().sum()
    print("Filas duplicadas exactas:", dup_count)
    if dup_count > 0:
        display(df[df.duplicated(keep=False)].head(20))

    print("\n=== INCONSISTENCIAS TOTAL SPENT (SI APLICA) ===")
    cols_needed = {'Price Per Unit', 'Quantity', 'Total Spent'}
    if cols_needed.issubset(df.columns):
        df['Calculated Total'] = df['Price Per Unit'] * df['Quantity']
        inconsistencias = df[np.abs(df['Total Spent'] - df['Calculated Total']) > 0.001]
        print("Inconsistencias detectadas:", len(inconsistencias))
    else:
        print("No se encontraron columnas necesarias para revisar inconsistencias.")

    print("\n=== VALORES NEGATIVOS (SI APLICA) ===")
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    negativos = df[(df[numeric_cols] < 0).any(axis=1)]
    print("Filas con valores negativos:", len(negativos))

    print("\n=== OUTLIERS (IQR) ===")
    for col in numeric_cols:
        if df[col].dtype not in ['int64', 'float64']:
            continue

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]
        print(f"{col}: {len(outliers)} outliers detectados")


