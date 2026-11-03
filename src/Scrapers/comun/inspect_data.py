"""
<src/Scrapers/comun/inspect_data.py>

Módulo de inspección rigurosa de datos para datasets CSV (con soporte de esquemas múltiples,
selección por solape de columnas y delimitadores automáticos) y Excel.
Uso CLI: python3 inspect_data.py <ruta_archivo>
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import numpy as np
import pandas as pd


class TeeLogger:
    """Clase para duplicar la salida estándar en la consola y en un archivo de texto."""
    def __init__(self, archivo_log: Path):
        self.terminal = sys.stdout
        self.log = open(archivo_log, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def cerrar(self):
        self.log.close()


def _es_tipo_dtype(valor: str) -> bool:
    """Reconoce si un string es un tipo de dato válido de pandas (dtype)."""
    v = valor.lower()
    return (
        any(t in v for t in ("int", "float", "string", "datetime"))
        or v in ("object", "bool", "boolean", "category")
    )


def cargar_esquema_si_existe(ruta_archivo: Path, columnas: list[str] | None = None):
    """
    Busca esquema.py en la carpeta del archivo o su padre y retorna el diccionario
    de tipos MEJOR AJUSTADO al dataset:

      - Si hay varios diccionarios (una fuente que genera dos tablas),
        se elige el que tenga MAYOR SOLAPE de columnas con el archivo real.
      - Se filtran las claves a las columnas efectivamente presentes.
    """
    carpetas_a_buscar = [ruta_archivo.parent, ruta_archivo.parent.parent]
    candidatos: list[dict] = []

    for carpeta in carpetas_a_buscar:
        esquema_path = carpeta / "esquema.py"
        if not esquema_path.exists():
            continue
        try:
            spec = importlib.util.spec_from_file_location("esquema_dinamico", str(esquema_path))
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)
            # Recolectar todos los diccionarios de esquema del módulo
            # (excluye diccionarios anidados como TABLAS_* o mapeos de etiquetas).
            for attr_name in dir(modulo):
                attr = getattr(modulo, attr_name)
                if (
                    isinstance(attr, dict)
                    and len(attr) > 0
                    and all(isinstance(v, str) for v in attr.values())
                    and any(_es_tipo_dtype(v) for v in attr.values())
                ):
                    candidatos.append(attr)
        except Exception as e:
            print(f"Aviso: No se pudo cargar esquema.py: {e}")
        if candidatos:
            break  # Priorizar la carpeta más cercana al archivo

    if not candidatos:
        return None

    # Sin columnas de referencia → primer candidato (compatibilidad histórica)
    if columnas is None:
        return candidatos[0]

    # Selección por mayor solape de columnas
    set_cols = set(columnas)
    mejor = max(candidatos, key=lambda d: len(set(d) & set_cols))
    if not set(mejor) & set_cols:
        return None
    esquema_efectivo = {k: v for k, v in mejor.items() if k in set_cols}
    if len(candidatos) > 1:
        print(f"[esquema] Seleccionado diccionario con {len(esquema_efectivo)}/{len(set_cols)} columnas coincidentes.")
    return esquema_efectivo


def inspeccion_rigurosa(ruta_archivo: str | Path):
    """
    Paso 1: Auditoría y contexto profundo del dataset (CSV o Excel) aplicando esquema si existe.
    Guarda automáticamente los resultados en un archivo <nombre>_inspeccion.txt en la misma ruta.
    """
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    # Definir la ruta agregando '_inspeccion.txt' al nombre base de la tabla
    ruta_reporte = ruta.with_name(f"{ruta.stem}_inspeccion.txt")

    # Redirigir stdout desde el inicio → el aviso de selección de esquema también queda en el .txt
    original_stdout = sys.stdout
    logger = TeeLogger(ruta_reporte)
    sys.stdout = logger

    try:
        # Leer solo el encabezado para conocer las columnas reales del archivo
        ext = ruta.suffix.lower()
        if ext in [".xlsx", ".xls"]:
            columnas = list(pd.read_excel(ruta, nrows=0).columns)
        else:
            try:
                columnas = list(pd.read_csv(ruta, sep=None, engine="python", nrows=0).columns)
            except Exception:
                columnas = list(pd.read_csv(ruta, sep=";", nrows=0).columns)

        # Seleccionar esquema con mayor solape de columnas (varios diccionarios soportados)
        esquema = cargar_esquema_si_existe(ruta, columnas)

        # Carga de datos según extensión y esquema
        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(ruta)
        else:
            try:
                if esquema:
                    df = pd.read_csv(ruta, sep=None, engine="python", dtype=esquema)
                else:
                    df = pd.read_csv(ruta, sep=None, engine="python")
            except Exception:
                if esquema:
                    df = pd.read_csv(ruta, sep=";", dtype=esquema)
                else:
                    df = pd.read_csv(ruta, sep=";")

        total_filas = len(df)

        print("="*60)
        print("📋 REPORTE DE INSPECCIÓN RIGUROSA DE DATOS")
        print(f"📁 Archivo: {ruta.name}")
        print("="*60)
        
        # 1. Dimensiones generales
        print(f"🔹 Dimensiones: {df.shape[0]} filas | {df.shape[1]} columnas")
        print(f"🔹 Tipo de Índice: {type(df.index)}")
        print(f"🔹 Registros Duplicados Absolutos: {df.duplicated().sum()} ({(df.duplicated().sum()/total_filas)*100:.2f}%)")
        print(f"🔹 Memoria Total Estimada: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB\n")
        
        # 2. Diagnóstico columna por columna
        print("🔬 MATRIZ DE CALIDAD POR COLUMNA:")
        print("-" * 115)
        print(f"{'Columna':<30} | {'Tipo':<12} | {'Nulos':<8} | {'% Nulos':<8} | {'Únicos':<8} | {'Espacios Vacíos':<15} | {'Memoria':<10}")
        print("-" * 115)
        
        for col in df.columns:
            # Calcular métricas básicas
            tipo = str(df[col].dtype)
            nulos = df[col].isna().sum()
            pct_nulos = (nulos / total_filas) * 100 if total_filas > 0 else 0
            unicos = df[col].nunique()
            memoria_mb = df[col].memory_usage(deep=True) / (1024**2)
            
            # Detectar strings que son solo espacios en blanco
            espacios_blanco = 0
            if df[col].dtype == 'object':
                try:
                    espacios_blanco = df[col].astype(str).str.isspace().sum()
                except Exception:
                    pass
                
            print(f"{str(col):<30} | {tipo:<12} | {nulos:<8} | {pct_nulos:<7.2f}% | {unicos:<8} | {espacios_blanco:<15} | {memoria_mb:<8.3f} MB")
        
        print("-" * 115)
        
        # 3. Separación de variables para el analista
        num_cols = df.select_dtypes(include=[np.number, pd.Int64Dtype()]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        print(f"\n🧠 Clasificación Automática de Variables:")
        print(f"   - Numéricas ({len(num_cols)}): {num_cols}")
        print(f"   - Categóricas/Texto ({len(cat_cols)}): {cat_cols}")
        print(f"   - Fechas ({len(date_cols)}): {date_cols}\n")
        
        # 4. Muestreo aleatorio controlado
        print("🎲 MUESTRA ALEATORIA DE 5 REGISTROS PARA CONTEXTO:")
        print(df.sample(n=min(5, len(df)), random_state=42) if len(df) > 0 else "DataFrame vacío")
        print("="*60)
        
    finally:
        # Asegurar que se restaure stdout y se cierre el archivo correctamente pase lo que pase
        sys.stdout = original_stdout
        logger.cerrar()
        print(f"\n💾 Reporte guardado con éxito en: {ruta_reporte}\n")
        
    return df


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 inspect_data.py <ruta_archivo>")
        sys.exit(1)
    
    archivo = sys.argv[1]
    inspeccion_rigurosa(archivo)
