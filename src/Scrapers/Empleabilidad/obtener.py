"""
<src/Scrapers/Empleabilidad/obtener.py>

Módulo de extracción de Empleabilidad e Ingresos desde mifuturo.cl
(Buscador de Empleabilidad e Ingresos).

Estrategia verificada (la tabla NO expone endpoint JSON propio, se extrae del HTML):

  Nivel 1 - Tabla base (obligatorio):
      3 POST al formulario `nameTab=empleabilidad` filtrando `tipo_institucionEmp`
      en {1=CFT, 2=IP, 3=Universidad}. Devuelve 176+324+1190 = 1690 filas con
      las 9 columnas visibles + `carrera_generica` y `id_institucion` extraídos
      de los atributos `onclick` de cada fila.

  Nivel 2 - Regiones (opcional, defecto activo):
      16 llamadas `dcms_ajax_all_filter(region=N)` -> mapa id_institución ->
      regiones donde tiene sedes. Cobertura 88/105 instituciones; el resto son
      planteles sin oferta vigente en el filtro regional.

  Nivel 3 - Ingresos y percentiles (opcional, defecto activo):
      `detalleEstadisticas(id)` (252 llamadas) -> ingreso medio años 1..5 y
      percentiles 10/25/50/75/90 de año 1 y año 5. Grain Nacional x Tipo de
      Institución x Carrera (NO por institución). Cobertura ~96% de filas.

Niveles descartados tras verificación empírica (no generan código):
  - `dcms_armado_tabla_empleabilidad(id)`: sus 4 campos están MAL ETIQUETADOS.
    Verificado con 177 muestras y coincidencia 100%:
        'desercion'           == retencion_1er_anio        (de la tabla base)
        'porcentaje_titulados'== empleabilidad_1er_anio    (de la tabla base)
        'subvencionado'       == pct_continuidad_estudios  (de la tabla base)
        'pro_arancel_...'     == '0' en 194/194 casos (sin valor)
    Por tanto NO aporta información nueva.
  - `dcms_armado_tabla_carrera(id)`: join de solo 12.8% contra la tabla base
    (nombres de carrera específicos vs. genéricos) -> descartado.

Límite conocido y documentado: la empleabilidad de MiFuturo es un indicador
NACIONAL por (institución, carrera). `regiones_sede` aporta el contexto
geográfico del plantel, no un corte regional de la empleabilidad.

Salida: Entrada/empleabilidad_mifuturo.csv  (separador ';', UTF-8)
"""

from __future__ import annotations

import logging
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

# Cabecera estándar del proyecto: ruta del script y fecha de actualización.
# Permite ejecutar el archivo desde cualquier directorio de trabajo.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun.normalizador import normalizar_texto  # noqa: E402

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
URL_BUSCADOR = "https://www.mifuturo.cl/buscador-de-empleabilidad-e-ingresos/"
URL_AJAX = "https://www.mifuturo.cl/wp-admin/admin-ajax.php"

DIR_ENTRADA = Path(__file__).parent / "Entrada"
NOMBRE_SALIDA = "empleabilidad_mifuturo.csv"

SEPARADOR_CSV = ";"

# Columnas que aporta el nivel 4 (detalleEstadisticas).
COLUMNAS_INGRESOS = [
    "ingreso_medio_1er_anio", "ingreso_medio_2do_anio", "ingreso_medio_3er_anio",
    "ingreso_medio_4to_anio", "ingreso_medio_5to_anio",
    "percentil_10_anio_1", "percentil_25_anio_1", "percentil_50_anio_1",
    "percentil_75_anio_1", "percentil_90_anio_1",
    "percentil_10_anio_5", "percentil_25_anio_5", "percentil_50_anio_5",
    "percentil_75_anio_5", "percentil_90_anio_5",
]

TIPOS_INSTITUCION = {1: "Centro de Formación Técnica", 2: "Instituto Profesional", 3: "Universidad"}
REGIONES = {
    15: "Arica y Parinacota", 1: "Tarapacá", 2: "Antofagasta", 3: "Atacama",
    4: "Coquimbo", 5: "Valparaíso", 13: "Metropolitana", 6: "O'Higgins",
    7: "Maule", 16: "Ñuble", 8: "Biobío", 9: "Araucanía", 14: "Los Ríos",
    10: "Los Lagos", 11: "Aysén", 12: "Magallanes",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

# Mapea la etiqueta corta del POST al nombre completo que usa el AJAX.
_ALIAS_TIPO = {
    "CENTRO DE FORMACIÓN TÉCNICA": "CENTRO DE FORMACIÓN TÉCNICA",
    "INSTITUTO PROFESIONAL": "INSTITUTO PROFESIONAL",
    "UNIVERSIDAD": "UNIVERSIDAD",
}


def _sesion() -> requests.Session:
    """Sesión HTTP con headers compartidos."""
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def _texto_celda(td: str) -> str:
    """Texto visible de una celda, sin etiquetas HTML."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", td or "")).strip()


def _data_order(td_attrs: str) -> str | None:
    """Valor numérico crudo del atributo data-order (vive en la etiqueta <td ...>)."""
    m = re.search(r'data-order="([^"]*)"', td_attrs or "")
    return m.group(1) if m else None


# --------------------------------------------------------------------------- #
# Nivel 1 - Tabla base
# --------------------------------------------------------------------------- #
def _descargar_tabla(s: requests.Session, tipo: int | str) -> list[dict]:
    """POST al formulario del buscador y parseo de la tabla de resultados."""
    payload = {
        "nameTab": "empleabilidad",
        "tipo_institucionEmp": tipo,
        "institucionEmp": "",
        "carreraEmp": "",
    }
    resp = s.post(URL_BUSCADOR, data=payload, timeout=180)
    resp.raise_for_status()

    bloque = re.search(r'<table id="tablaEmpleabilidad".*?</table>', resp.text, re.S)
    if not bloque:
        raise RuntimeError("no se encontró <table id='tablaEmpleabilidad'> en la respuesta")

    filas: list[dict] = []
    for tr in re.findall(r'<tr[^>]*>(?!\s*<th)(.*?)</tr>', bloque.group(0), re.S):
        # Se capturan ATRIBUTOS y CONTENIDO por separado: data-order está en la
        # etiqueta de apertura <td data-order="...">texto</td>.
        celdas = re.findall(r"<td([^>]*)>(.*?)</td>", tr, re.S)
        if len(celdas) < 9:
            continue

        (a0, c0), (a1, c1), (a2, c2), (a3, c3), (a4, c4), \
            (a5, c5), (a6, c6), (a7, c7), (a8, c8) = celdas[:9]

        # onclick -> id de institución y carrera genérica
        m_inst = re.search(r"cambioabuscadorInstitucion\((\d+)\)", c0)
        m_gen = re.search(r"cambioabuscadorcarreras\(\d+,'([^']*)'\)", c2)
        if not m_inst:
            continue

        filas.append({
            "id_institucion": int(m_inst.group(1)),
            "institucion": _texto_celda(c0),
            "acreditacion_institucion": _texto_celda(c1),
            "acreditacion_anios": _data_order(a1),
            "carrera": _texto_celda(c2),
            "carrera_generica": m_gen.group(1) if m_gen else "",
            "pct_continuidad_estudios": _data_order(a3),
            "retencion_1er_anio": _data_order(a4),
            "duracion_real_semestres": _data_order(a5),
            "empleabilidad_1er_anio": _data_order(a6),
            "empleabilidad_2do_anio": _data_order(a7),
            "ingreso_prom_4to_anio": _texto_celda(c8),
            "ingreso_prom_4to_anio_tramo": _data_order(a8),
        })
    return filas


def _obtener_tabla_base(s: requests.Session) -> pd.DataFrame:
    """Une los 3 POST por tipo de institución -> etiqueta `tipo_institucion`."""
    registros: list[dict] = []
    for tipo, nombre in TIPOS_INSTITUCION.items():
        filas = _descargar_tabla(s, tipo)
        log.info("tipo_institucion=%s (%s): %d filas", tipo, nombre, len(filas))
        for f in filas:
            f["tipo_institucion"] = nombre
        registros.extend(filas)
        time.sleep(0.2)

    df = pd.DataFrame(registros)
    if df.empty:
        raise RuntimeError("la tabla base de empleabilidad llegó vacía")
    log.info("tabla base: %d filas, %d instituciones", len(df), df["id_institucion"].nunique())
    return df


# --------------------------------------------------------------------------- #
# Nivel 2 - Regiones por institución
# --------------------------------------------------------------------------- #
def _mapa_regiones(s: requests.Session) -> dict[int, list[str]]:
    """Regiones con presencia de cada institución (16 llamadas AJAX)."""
    mapa: dict[int, list[str]] = {}
    for cod, nombre in REGIONES.items():
        try:
            resp = s.post(URL_AJAX, data={"action": "dcms_ajax_all_filter", "region": cod}, timeout=60)
            data = resp.json()
        except Exception as exc:  # noqa: BLE001 - degradar sin tumbar el pipeline
            log.warning("región %s falló: %s", nombre, exc)
            continue
        # El JSON trae las claves cruzadas: rs_areas_del_conocimiento = instituciones.
        for item in data.get("rs_areas_del_conocimiento", []):
            mapa.setdefault(int(item["id"]), []).append(nombre)
        time.sleep(0.1)
    log.info("mapa regiones: %d instituciones mapeadas", len(mapa))
    return mapa


# --------------------------------------------------------------------------- #
# Nivel 3 - Ingresos y percentiles (Nacional x Tipo x Carrera)
# --------------------------------------------------------------------------- #
def _catalogo_estadisticas(s: requests.Session) -> dict[tuple[str, str], str]:
    """(tipo_institución, carrera) -> id de detalleEstadisticas."""
    resp = s.post(
        URL_BUSCADOR.replace("buscador-de-empleabilidad-e-ingresos", "buscador-de-estadisticas-por-carrera"),
        data={
            "nameTab": "estadisticas",
            "areaConocimiento_est": "",
            "tipo_institucion_est": "",
            "institucionEst": "",
            "carreraEst": "",
        },
        timeout=180,
    )
    resp.raise_for_status()
    bloque = re.search(r'<table id="table_id".*?</table>', resp.text, re.S)
    if not bloque:
        raise RuntimeError("no se encontró la tabla de estadísticas por carrera")

    cat: dict[tuple[str, str], str] = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", bloque.group(0), re.S)[1:]:
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        m_id = re.search(r"verestadisticas\('(\d+)'\)", tr)
        if len(tds) >= 2 and m_id:
            # Se elimina el link "Ver estadísticas" COMPLETO (incluido su texto),
            # luego el resto del HTML, y recién ahí se normaliza la clave.
            def _limpiar(celda: str) -> str:
                celda = re.sub(r"<a\b.*?</a>", "", celda, flags=re.S)
                return normalizar_texto(_texto_celda(celda))

            cat[(_limpiar(tds[0]), _limpiar(tds[1]))] = m_id.group(1)
    log.info("catálogo estadísticas: %d combinaciones (tipo, carrera)", len(cat))
    return cat


def _ingresos_estadistica(s: requests.Session, id_est: str) -> dict:
    """Ingreso medio años 1..5 + percentiles 10/25/50/75/90 de año 1 y 5."""
    d: dict = {}
    for intento in range(3):
        try:
            resp = s.post(URL_AJAX, data={"action": "detalleEstadisticas", "id": id_est}, timeout=60)
            resp.raise_for_status()
            d = resp.json()
            break
        except Exception as exc:  # noqa: BLE001 - el servidor corta conexiones al hacer rate-limit
            espera = 2.0 * (intento + 1)
            log.warning("detalleEstadisticas %s (intento %d/3) falló en %.1fs: %s",
                        id_est, intento + 1, espera, exc)
            time.sleep(espera)

    if not d:
        return {}
    time.sleep(0.15)
    return {
        "ingreso_medio_1er_anio": d.get("primer_ano"),
        "ingreso_medio_2do_anio": d.get("segundo_ano"),
        "ingreso_medio_3er_anio": d.get("tercer_ano"),
        "ingreso_medio_4to_anio": d.get("cuarto_ano"),
        "ingreso_medio_5to_anio": d.get("quinto_ano"),
        "percentil_10_anio_1": d.get("percentil10_a"),
        "percentil_25_anio_1": d.get("percentil25_a"),
        "percentil_50_anio_1": d.get("percentil50_a"),
        "percentil_75_anio_1": d.get("percentil75_a"),
        "percentil_90_anio_1": d.get("percentil90_a"),
        "percentil_10_anio_5": d.get("percentil10_b"),
        "percentil_25_anio_5": d.get("percentil25_b"),
        "percentil_50_anio_5": d.get("percentil50_b"),
        "percentil_75_anio_5": d.get("percentil75_b"),
        "percentil_90_anio_5": d.get("percentil90_b"),
    }


def _enriquecer_ingresos(s: requests.Session, df: pd.DataFrame) -> pd.DataFrame:
    """Adjunta ingresos/percentiles por (tipo_institución, carrera_genérica)."""
    cat = _catalogo_estadisticas(s)
    cache: dict[str, dict] = {}
    columnas: list[dict] = []
    usados = 0

    for tipo, gen in zip(df["tipo_institucion"], df["carrera_generica"]):
        clave_id = cat.get((normalizar_texto(tipo), normalizar_texto(gen)))
        if clave_id is None:
            columnas.append({})
            continue
        if clave_id not in cache:
            cache[clave_id] = _ingresos_estadistica(s, clave_id)
            usados += 1
        columnas.append(cache[clave_id])

    extra = pd.DataFrame(columnas)
    # Garantiza la presencia de todas las columnas aunque no haya ninguna coincidencia.
    for col in COLUMNAS_INGRESOS:
        if col not in extra.columns:
            extra[col] = pd.NA
    out = pd.concat([df.reset_index(drop=True), extra[COLUMNAS_INGRESOS]], axis=1)
    log.info("ingresos: %d/%d llamadas únicas, %d filas enriquecidas",
             usados, len(cat), out["ingreso_medio_1er_anio"].notna().sum())
    return out


# --------------------------------------------------------------------------- #
# Orquestador
# --------------------------------------------------------------------------- #
def obtener_empleabilidad(
    con_region: bool = True,
    con_ingresos: bool = True,
) -> Path:
    """
    Descarga y arma el CSV de empleabilidad e ingresos en Entrada/.

    Returns:
        Ruta del CSV generado.
    """
    DIR_ENTRADA.mkdir(parents=True, exist_ok=True)
    s = _sesion()

    df = _obtener_tabla_base(s)

    if con_region:
        mapa = _mapa_regiones(s)
        df["regiones_sede"] = (
            df["id_institucion"]
            .map(lambda i: "|".join(mapa.get(int(i), [])))
            .replace("", pd.NA)
        )
        log.info("regiones asignadas: %d/%d filas",
                 df["regiones_sede"].notna().sum(), len(df))

    if con_ingresos:
        df = _enriquecer_ingresos(s, df)

    destino = DIR_ENTRADA / NOMBRE_SALIDA
    df.to_csv(destino, sep=SEPARADOR_CSV, index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas, %d columnas)", destino, len(df), len(df.columns))
    return destino


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = obtener_empleabilidad()
    df_final = pd.read_csv(ruta, sep=SEPARADOR_CSV)
    print("\n=== Empleabilidad MiFuturo ===")
    print(f"Archivo : {ruta}")
    print(f"Filas   : {len(df_final):,}")
    print(f"Columnas: {len(df_final.columns)}")
    print("Campos  :", ", ".join(df_final.columns))
