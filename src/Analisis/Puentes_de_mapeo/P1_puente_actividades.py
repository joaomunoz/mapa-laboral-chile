"""
<src/Analisis/Puentes_de_mapeo/P1_puente_actividades.py>

Generador del P1 · PUENTE_ACTIVIDADES del proyecto.

Salida: Salida/P1_puente_actividades.csv (CAENES 1-21 ↔ CIIU A-U, 21 filas)

  Mapea oficial CAENES (rama de actividad de ENE, `r_p_rev4cl_caenes`) ↔ sección CIIU
  (ENADEL, `actividad_ciiu`). Relación 1:1, transcrita VERBATIM del Libro de códigos ENE
  2020, Anexo 5 — no se interpreta ni se completa con fuentes externas.

Esquema: esquema.py (PUENTE_ACTIVIDADES, VALIDACIONES)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

from esquema import PUENTE_ACTIVIDADES  # noqa: E402  (esquema.py hermano)

log = logging.getLogger(__name__)

DIR_SCRAPERS = Path(__file__).resolve().parents[2] / "Scrapers"
DIR_SALIDA = Path(__file__).parent / "Salida"
SEPARADOR_SALIDA = ";"

# P1 — Actividades: CAENES (ENE) ↔ Sección CIIU (ENADEL)
# Libro de códigos ENE 2020, Anexo 5 (transcripción verbatim, relación 1:1)
# --------------------------------------------------------------------------- #
ANEXO_5_ACTIVIDADES: list[tuple[int, str, str]] = [
    (1, "A", "Agricultura, ganadería, silvicultura y pesca"),
    (2, "B", "Explotación de minas y canteras"),
    (3, "C", "Industrias manufactureras"),
    (4, "D", "Suministro de electricidad, gas, vapor y aire acondicionado"),
    (5, "E", "Suministro de agua; evacuación de aguas residuales y gestión de desechos"),
    (6, "F", "Construcción"),
    (7, "G", "Comercio al por mayor y al por menor; reparación de vehículos"),
    (8, "H", "Transporte y almacenamiento"),
    (9, "I", "Actividades de alojamiento y de servicio de comidas"),
    (10, "J", "Información y comunicaciones"),
    (11, "K", "Actividades financieras y de seguros"),
    (12, "L", "Actividades inmobiliarias"),
    (13, "M", "Actividades profesionales, científicas y técnicas"),
    (14, "N", "Actividades de servicios administrativos y de apoyo"),
    (15, "O", "Administración pública, defensa y seguridad social"),
    (16, "P", "Enseñanza"),
    (17, "Q", "Actividades de atención de la salud humana y de servicios sociales"),
    (18, "R", "Actividades artísticas, de espectáculos y deportivas"),
    (19, "S", "Otras actividades de servicios"),
    (20, "T", "Actividades de los hogares como empleadores"),
    (21, "U", "Actividades de organizaciones y organismos extraterritoriales"),
]
ORIGEN_ANEXO_5 = "Libro de códigos ENE 2020, Anexo 5"


def generar_puente_actividades() -> pd.DataFrame:
    """Construye P1: tabla 1:1 CAENES ↔ sección CIIU (Anexo 5, verbatim)."""
    df = pd.DataFrame(
        ANEXO_5_ACTIVIDADES, columns=["actividad_caenes", "actividad_ciiu", "actividad_glosa"]
    )
    df["origen"] = ORIGEN_ANEXO_5
    return df[list(PUENTE_ACTIVIDADES)].astype(PUENTE_ACTIVIDADES)


def validar_actividades(df: pd.DataFrame) -> None:
    log.info("=== Validaciones P1_puente_actividades (%d filas) ===", len(df))
    ok1 = (
        len(df) == 21
        and df["actividad_caenes"].is_unique and df["actividad_ciiu"].is_unique
        and df["actividad_caenes"].between(1, 21).all()
    )
    log.info("  [%s] 1. 21 filas, 1:1 CAENES 1-21 ↔ CIIU A-U      : actividad_caenes únicos=%s, secciones únicas=%s",
             "✓" if ok1 else "✗", df["actividad_caenes"].is_unique, df["actividad_ciiu"].is_unique)
    nulos = int(df.isna().sum().sum())
    log.info("  [%s] 2. Sin nulos                                   : %d nulos",
             "✓" if nulos == 0 else "✗", nulos)


def generar_p1() -> Path:
    """Construye, valida y exporta P1."""
    actividades = generar_puente_actividades()
    validar_actividades(actividades)
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = DIR_SALIDA / "P1_puente_actividades.csv"
    actividades.to_csv(ruta, sep=SEPARADOR_SALIDA, index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", ruta.name, len(actividades))
    return ruta


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = generar_p1()
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
