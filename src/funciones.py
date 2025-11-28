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


#-----------CONVERTIR A DATETIME--------------------------------------------------------
def convertir_a_datetime(df, columnas):
    """
    Convierte una o varias columnas del DataFrame a formato datetime
    y devuelve clean_df con los cambios aplicados.

    Parámetros:
        df: DataFrame original.
        columnas: lista con los nombres de las columnas a convertir.

    Devuelve:
        clean_df: copia del DataFrame con conversiones aplicadas.
    """
    import pandas as pd

    # Creamos copia para no modificar el df original
    clean_df = df.copy()

    for col in columnas:
        if col not in clean_df.columns:
            print(f"[Aviso] La columna '{col}' no existe en el DataFrame.")
            continue

        # Valores nulos antes de convertir
        antes_nulos = clean_df[col].isna().sum()

        # Conversión
        clean_df[col] = pd.to_datetime(clean_df[col], errors="coerce")

        # Valores NaT generados por la conversión
        despues_nulos = clean_df[col].isna().sum()
        nuevos_nulos = despues_nulos - antes_nulos

        print(f"Columna '{col}' convertida a datetime. Nuevos NaT generados: {nuevos_nulos}")

    return clean_df



#-----------IMPUTACION ITEM--------------------------------------------------------

def imputar_items_por_categoria(df, suffix_map, verbose=True):
    """
    Imputa valores faltantes en la columna 'Item' usando un patrón:
        Item_{random(1-30)}_{suffix_categoria}

    Parámetros:
        df: DataFrame original.
        suffix_map: diccionario {categoria: sufijo}
        verbose: si True, imprime diagnóstico.

    Devuelve:
        clean_df: copia del DataFrame con 'Item' imputado.
    """
    import random
    clean_df = df.copy()

    # Índices donde Item es NaN en el original
    missing_items_idx = clean_df[clean_df["Item"].isna()].index

    for idx in missing_items_idx:
        category = clean_df.at[idx, "Category"]
        suffix = suffix_map.get(category, "UNK")  # sufijo por defecto si categoría desconocida
        random_number = random.randint(1, 30)

        clean_df.at[idx, "Item"] = f"Item_{random_number}_{suffix}"

    if verbose:
        null_count = clean_df["Item"].isna().sum()
        print(f"Número de valores nulos en Item después de imputación: {null_count}")

        if len(missing_items_idx) > 0:
            print("\nEjemplos de filas imputadas:")
            display(clean_df.loc[missing_items_idx, ["Category", "Item"]].head(10))

    return clean_df

#-----------IMPUTACION CUANTITATIVaS--------------------------------------------------------

def imputar_precios_cantidades_totales(df, verbose=True):

    clean_df = df.copy()

    # IMPUTACIÓN PRICE PER UNIT

    # 1) Fórmula: Total Spent / Quantity
    clean_df['Price Per Unit'] = (
        clean_df['Price Per Unit']
        .fillna(
            (clean_df['Total Spent'] / clean_df['Quantity'])
            .where(clean_df['Quantity'] != 0)
        )
    )

    # 2) Media agrupada por Item
    clean_df['Price Per Unit'] = (
        clean_df['Price Per Unit']
        .fillna(clean_df.groupby('Item')['Price Per Unit'].transform('mean'))
    )

    # 3) Valor fijo
    clean_df['Price Per Unit'] = clean_df['Price Per Unit'].fillna(50.0)

    # IMPUTACIÓN QUANTITY

    clean_df['Quantity'] = (
        clean_df['Quantity']
        .fillna(
            (clean_df['Total Spent'] / clean_df['Price Per Unit'])
            .where(clean_df['Price Per Unit'] != 0)
        )
    )

    clean_df['Quantity'] = (
        clean_df['Quantity']
        .fillna(clean_df.groupby('Item')['Quantity'].transform('mean'))
    )

    clean_df['Quantity'] = clean_df['Quantity'].fillna(5.0)

    # IMPUTACIÓN TOTAL SPENT

    clean_df['Total Spent'] = (
        clean_df['Total Spent']
        .fillna(clean_df['Price Per Unit'] * clean_df['Quantity'])
    )

    # RESUMEN FINAL

    if verbose:
        print("Valores nulos restantes por columna:")
        print(clean_df.isna().sum())

    return clean_df


#-----------IMPUTACION DISCOUNT--------------------------------------------------------

def limpiar_discount_y_columna_calculada(df, verbose=True):

    clean_df = df.copy()

    # IMPUTAR DISCOUNT APPLIED
    if "Discount Applied" in clean_df.columns:
        clean_df["Discount Applied"] = clean_df["Discount Applied"].fillna("False")

    # ELIMINAR COLUMNA CALCULATED TOTAL
    if "Calculated Total" in clean_df.columns:
        clean_df = clean_df.drop(columns=["Calculated Total"])

    # MÓDULO DE REPORTE
    if verbose:
        print("Valores nulos restantes en cada columna:")
        print(clean_df.isna().sum())

    return clean_df

#-----------ESTANDARIZAR NOMBRES COLUMNAS--------------------------------------------------------

def estandarizar_nombres_columnas(df, verbose=True):

    clean_df = df.copy()

    clean_df.columns = (
        clean_df.columns
            .str.lower()
            .str.replace(" ", "_", regex=False)
            .str.replace("-", "_", regex=False)
    )

    if verbose:
        print("Nombres de columnas estandarizados:")
        print(clean_df.columns.tolist())

    return clean_df


