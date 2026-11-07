"""
<src/Visualizacion/controles.py>

Controles que detienen la generación si los datos dejan de respaldar el color, la lectura o las frases de la página.

Las cifras van escritas a mano a propósito: el título, los hallazgos y las anotaciones las afirman en texto, y si los
datos cambian, el mapa no debe publicarse con frases que ya no son ciertas.
"""

from __future__ import annotations

import logging

import pandas as pd
import pyarrow.parquet as pq

from config import CLASE_NEUTRA, COLOR_RESUMEN, DIFERENCIA_AREA_MAXIMA_PCT, DIFERENCIA_AREA_SIMPLIFICADA_MAXIMA_PCT, NOMBRES_REGION, OCUPADO, OCUPADOS_DIVERSIDAD_GENERO, OCUPADOS_GENERO_SUPRIMIDO, POBLACION_POR_SEXO, POBLACION_TOTAL_CENSO, RUTA_PERSONAS
from formato import de_cada_10
from indicadores import clase_color

log = logging.getLogger(__name__)


def totales_sexo_genero_correctos() -> bool:
    """Compara las constantes con los microdatos; regenerar el mapa no los exige, así que sin ellos no hay nada que comparar."""
    if not RUTA_PERSONAS.exists():
        return True
    d = pd.read_parquet(RUTA_PERSONAS, columns=["sexo", "div_genero", "sit_fuerza_trabajo"])
    genero = d.loc[d["sit_fuerza_trabajo"] == OCUPADO, "div_genero"].value_counts()
    return d["sexo"].value_counts().to_dict() == POBLACION_POR_SEXO and genero[1] == OCUPADOS_DIVERSIDAD_GENERO and genero[-66] == OCUPADOS_GENERO_SUPRIMIDO


def validar(datos: dict, geo: dict, html: str) -> None:
    celdas = [d for a in datos["actividades"] for d in a["regiones"].values() if d["clase"] is not None]
    lectura_esperada = lambda c: "bajo_lo_nacional" if c < CLASE_NEUTRA else "similar" if c == CLASE_NEUTRA else "concentra"
    con_base = [d for d in celdas if d["lectura"] != "base_pequena"]
    texto_calza = lambda d: clase_color(float(d["peso_txt"].replace(",", "."))) == d["clase"]
    sin_dato = sum(d["clase"] is None for a in datos["actividades"] for d in a["regiones"].values())
    pob = datos["poblacion"]
    por_ciiu = {a["ciiu"]: a for a in datos["actividades"]}
    controles = {
        "El color coincide con la lectura en todas las celdas": all(lectura_esperada(d["clase"]) == d["lectura"] for d in con_base),
        "La cifra visible cae en el tramo de su color": all(texto_calza(d) for d in celdas),
        "20 actividades en la lista": len(datos["actividades"]) == 20 and "U" not in [a["ciiu"] for a in datos["actividades"]],
        "Bordes válidos antes y después de simplificar": geo["geometria_valida"],
        "El área de cada región cambia menos de 0,5% al reconstruir los bordes": geo["diferencia_area_pct"] < DIFERENCIA_AREA_MAXIMA_PCT,
        "El área de cada región cambia menos de 1% al simplificar": geo["diferencia_simplificada_pct"] < DIFERENCIA_AREA_SIMPLIFICADA_MAXIMA_PCT,
        "Minería en Chile: 268.491 con región y 275.517 en total": por_ciiu["B"]["nacional"]["ocupados"] == 268_491 and por_ciiu["B"]["nacional"]["censo_total"] == 275_517,
        "Salud: más personas en la Metropolitana y más peso en Biobío": por_ciiu["Q"]["nacional"]["mas_personas"]["r"] == 13 and por_ciiu["Q"]["nacional"]["mas_peso"]["r"] == 8,
        "Profesionales desocupados en Chile: 153.695": datos["niveles_chile"]["Profesional"]["desocupados"] == 153_695,
        "Las 16 regiones tienen sus 3 niveles": len(datos["niveles"]) == 16 and all(len(n) == 3 for n in datos["niveles"].values()),
        "16 regiones con trazado": sorted(geo["trazados"]) == sorted(NOMBRES_REGION),
        "Cada actividad tiene las 16 regiones": all(len(a["regiones"]) == 16 for a in datos["actividades"]),
        "Antofagasta en Minería: 101.929": por_ciiu["B"]["regiones"][2]["ocupados"] == 101_929,
        "Todas las carreras listadas tienen ficha": all(x["c"] in datos["fichas"] for a in datos["actividades"] for x in a["afines"] + a["indicios"]),
        # La página agrupa las carreras por nivel: una carrera con otro nivel quedaría fuera de todos los grupos.
        "Ficha: Psicología con 85.260 títulos 2007-2025 y empleabilidad de 43,7% a 89,7%": (datos["fichas"]["PSICOLOGIA"]["tit_hist"], datos["fichas"]["PSICOLOGIA"]["emp_r"]) == (85_260, [43.7, 89.7]),
        "Ficha: sin rango cuando hay aviso de pocas instituciones": all(f["emp_r"] is None for f in datos["fichas"].values() if f["alerta_inst"]),
        "Toda carrera listada es técnica o profesional": all(datos["fichas"][x["c"]]["nivel"] in ("Profesional", "Tecnico") for a in datos["actividades"] for x in a["afines"] + a["indicios"]),
        "Resumen: las 16 regiones tienen actividad distintiva y color": len(datos["resumen"]["regiones"]) == 16 and all(d["ciiu"] in COLOR_RESUMEN for d in datos["resumen"]["regiones"].values()),
        "Resumen: cada color se usa": {d["ciiu"] for d in datos["resumen"]["regiones"].values()} == set(COLOR_RESUMEN),
        "Resumen: Metropolitana en 18 de 20; excepciones en Maule y Antofagasta": datos["resumen"]["n_metropolitana"] == 18 and sorted(e["r"] for e in datos["resumen"]["excepciones"]) == [2, 7],
        "Resumen: Comercio emplea más en 12 de 16 regiones": datos["resumen"]["mayor_empleador"] == {"ciiu": "G", "n": 12},
        "Resumen: Minería y Agricultura son las más desiguales": [d["ciiu"] for d in datos["resumen"]["mas_desiguales"]] == ["B", "A"],
        "Resumen: Valparaíso y Biobío van en color suave; La Araucanía (1,60) ya no": sorted(r for r, d in datos["resumen"]["regiones"].items() if d["suave"]) == ["5", "8"],
        "CL: todas las cifras con 2 decimales": all(len(d["peso_txt"].split(",")[1]) == 2 for d in celdas),
        "Población: 15,2 millones de 15 años o más, y suman sus cuatro grupos": pob["chile"]["total"] == 15_205_784 and pob["chile"]["trabajan"] + pob["chile"]["buscan"] + pob["chile"]["no_buscan"] + pob["chile"]["sin_dato"] == pob["chile"]["total"],
        "Población: las regiones suman el total de Chile": sum(d["total"] for d in pob["regiones"].values()) == pob["chile"]["total"] and len(pob["regiones"]) == 16,
        "Población: el % que trabaja va de Ñuble a Aysén": min(pob["regiones"], key=lambda r: pob["regiones"][r]["pct_trabajan"]) == "16" and max(pob["regiones"], key=lambda r: pob["regiones"][r]["pct_trabajan"]) == "11",
        # Los indicadores, el título del mapa y sus anotaciones llevan estas afirmaciones escritas a mano: si los datos cambian, la generación se detiene.
        "Indicadores: la Metropolitana reúne 42,1% de los ocupados": pob["regiones"]["13"]["pct_lugar_trabajo"] == 42.1 and pob["regiones"]["13"]["lugar_trabajo"] == 3_286_880,
        "Mapa: 13 de 16 regiones tienen su mayor CL en Minería, Agricultura o Adm. pública": sum(d["ciiu"] in "BAO" for d in datos["resumen"]["regiones"].values()) == 13 and len(datos["resumen"]["regiones"]) == 16,
        "Indicadores: brecha de participación de 19,5 puntos": round(pob["sexo"]["hombres"]["tasa_participacion"] - pob["sexo"]["mujeres"]["tasa_participacion"], 1) == 19.5,
        "Anotaciones: Minería en el norte, Agricultura en el centro-sur y Adm. pública en los extremos": {c: sorted(int(r) for r, d in datos["resumen"]["regiones"].items() if d["ciiu"] == c) for c in "BAO"} == {"B": [1, 2, 3, 4], "A": [6, 7, 9, 10, 14, 16], "O": [11, 12, 15]},
        "Anotaciones: Antofagasta, Maule y Aysén son el mayor CL de sus grupos": all(max((d["peso"], int(r)) for r, d in datos["resumen"]["regiones"].items() if d["ciiu"] == c)[1] == m for c, m in (("B", 2), ("A", 7), ("O", 11))),
        "Sexo: hombres y mujeres suman cada grupo de la población de Chile": all(pob["sexo"]["hombres"][k] + pob["sexo"]["mujeres"][k] == v for k, v in (("poblacion_total", pob["poblacion_total"]), ("menores_15", pob["menores_15"]), ("total", pob["chile"]["total"]), ("trabajan", pob["chile"]["trabajan"]), ("buscan", pob["chile"]["buscan"]), ("no_buscan", pob["chile"]["no_buscan"]), ("sin_dato", pob["chile"]["sin_dato"]))),
        "Sexo: en cada actividad, hombres y mujeres suman sus ocupados": all(a["sexo"]["h"] + a["sexo"]["m"] == a["nacional"]["ocupados"] for a in datos["actividades"]),
        "Sexo: Comercio 665.041 y 646.953; Construcción 496.948 y 46.279": (lambda c, f: (c["h"], c["m"], f["h"], f["m"]) == (665_041, 646_953, 496_948, 46_279))(por_ciiu["G"]["sexo"], por_ciiu["F"]["sexo"]),
        "Estudios: 39,8% de los ocupados con título; desocupación 6,3%, 7,8% y 9,7%": (lambda e: e["pct_con_titulo"] == 39.8 and (e["niveles"]["Profesional"]["tasa_desocupacion"], e["niveles"]["Tecnico"]["tasa_desocupacion"], e["niveles"]["Sin_titulo"]["tasa_desocupacion"]) == (6.3, 7.8, 9.7))(datos["estudios"]),
        "Estudios: los niveles suman el total y su tasa coincide con la tabla regional": sum(d["ocupados"] for d in datos["estudios"]["niveles"].values()) == datos["estudios"]["total"] and all(datos["estudios"]["niveles"][n]["tasa_desocupacion"] == d["tasa"] for n, d in datos["niveles_chile"].items()),
        "Estudios: mujeres 46,5% y hombres 34,6% de los ocupados con título": datos["estudios"]["sexo"] == {"hombres": 34.6, "mujeres": 46.5},
        "Educación por región: suma 15.102.704 y va de Maule (21,1%) a la Metropolitana (32,9%)": (lambda e: sum(e["chile"]) == 15_102_704 and sum(sum(v) for r, v in e.items() if r != "chile") == sum(e["chile"])
            and sorted((round(100 * (v[0] + v[1]) / sum(v), 1), int(r)) for r, v in e.items() if r != "chile")[::15] == [(21.1, 7), (32.9, 13)])(datos["estudios"]["educacion"]),
        "Educación por región: se excluyen 97.157 sin nivel y 5.923 sin situación laboral, y con la tabla suman los 15 años o más":
            datos["estudios"]["excluidos"] == {"sin_nivel": 97_157, "sin_situacion": 5_923} and sum(datos["estudios"]["educacion"]["chile"]) + sum(datos["estudios"]["excluidos"].values()) == pob["chile"]["total"],
        "Educación por región: Chile 28,2% con título": (lambda c: round(100 * (c[0] + c[1]) / sum(c), 1) == 28.2)(datos["estudios"]["educacion"]["chile"]),
        "Hallazgos: 4 de cada 10 ocupados con título; 1 de cada 10 en Hogares y 8 de cada 10 en Servicios profesionales": (lambda p: de_cada_10(datos["estudios"]["pct_con_titulo"]) == 4 and (de_cada_10(min(p)), de_cada_10(max(p))) == (1, 8))(
            [100 * (a["niveles"][0][0] + a["niveles"][1][0]) / sum(f[0] for f in a["niveles"]) for a in datos["actividades"]]),
        "Desocupación menor con título en las 16 regiones: de Aysén (4,2% y 6,2%) a Biobío (9,1% y 11,1%)": (lambda d: len(d) == 16 and all(c < t for c, t in d.values()) and d["11"] == [4.2, 6.2] and d["8"] == [9.1, 11.1]
            and min(d, key=lambda r: d[r][0]) == "11" and max(d, key=lambda r: d[r][0]) == "8")(datos["estudios"]["desocupacion_titulo"]),
        "Nivel por actividad: Minería en Chile 82.082 profesionales; Antofagasta 28.576": (lambda a: a["niveles"][0] == [82_082, 30.6, 61_954, 20_128, 27.3, 48.7] and a["regiones"][2]["niveles"][0] == [28_576, 28.0, 21_907, 6_669, 25.3, 43.3])(por_ciiu["B"]),
        "Nivel por actividad: solo faltan 2.757 ocupados sin nivel informado": sum(d["ocupados"] for a in datos["actividades"] for d in a["regiones"].values()) - sum(f[0] for a in datos["actividades"] for d in a["regiones"].values() for f in d["niveles"]) == 2_757,
        "Nivel por actividad: hombres y mujeres suman el total cuando ambos se muestran": all(f[2] + f[3] == f[0] for a in datos["actividades"] for d in [a, *a["regiones"].values()] for f in d["niveles"] if f[2] is not None and f[3] is not None),
        "Nivel por actividad: 16 filas regionales con menos de 10, y ninguna nacional": sum(f[2] is None or f[3] is None for a in datos["actividades"] for d in a["regiones"].values() for f in d["niveles"]) == 16 and not any(f[2] is None or f[3] is None for a in datos["actividades"] for f in a["niveles"]),
        "Nivel por actividad: todas las actividades 27,3%, 12,3% y 60,4%": datos["perfil_estudios"]["todas"] == [27.3, 12.3, 60.4],
        "Sexo por región: en cada celda, hombres y mujeres suman sus ocupados": all(d["h"] + d["m"] == d["ocupados"] for a in datos["actividades"] for d in a["regiones"].values()),
        "Sexo por región: las bases suman la base de cada región y de Chile": all(v["h"] + v["m"] == datos["base_ocupados"]["regiones"][r] for r, v in datos["base_ocupados"]["sexo"]["regiones"].items()) and sum(datos["base_ocupados"]["sexo"]["chile"].values()) == datos["base_ocupados"]["chile"],
        "Sexo por región: Biobío en Salud 15.108 y 45.643; 4,91% y 17,22%": (lambda d: (d["h"], d["m"], d["pct_h"], d["pct_m"]) == (15_108, 45_643, 4.91, 17.22))(por_ciiu["Q"]["regiones"][8]),
        "Situación por sexo: cada región suma sus grupos": all(d["sexo"]["hombres"][k] + d["sexo"]["mujeres"][k] == d[k] for d in pob["regiones"].values() for k in ("total", "trabajan", "buscan", "no_buscan", "sin_dato")),
        "Nivel por sexo: suma los ocupados y desocupados de cada región y de Chile": all(d["sexo"]["oh"] + d["sexo"]["om"] == d["trabajo"] and d["sexo"]["dh"] + d["sexo"]["dm"] == d["desocupados"] for g in datos["niveles"].values() for d in g.values()) and all(d["sexo"]["oh"] + d["sexo"]["om"] == d["ocupados"] and d["sexo"]["dh"] + d["sexo"]["dm"] == d["desocupados"] for d in datos["niveles_chile"].values()),
        "Títulos por sexo: hombres y mujeres no superan el total; Enfermería 845 y 4.123": all(f["tit_h"] + f["tit_m"] <= f["tit"] for f in datos["fichas"].values()) and (datos["fichas"]["ENFERMERIA"]["tit_h"], datos["fichas"]["ENFERMERIA"]["tit_m"]) == (845, 4_123),
        "Sexo y género: las constantes coinciden con los microdatos, si están": totales_sexo_genero_correctos(),
        "Población: el total coincide con los microdatos, si están": not RUTA_PERSONAS.exists() or pq.ParquetFile(RUTA_PERSONAS).metadata.num_rows == POBLACION_TOTAL_CENSO,
        # La columna "Con título" se calcula en la página desde estas personas; aquí se fija contra la fuente.
        "Con título por actividad: Servicios profesionales 78,7%, Hogares 9,9% y todas 39,6%": (lambda pct: (round(pct(por_ciiu["M"]["niveles"]), 1), round(pct(por_ciiu["T"]["niveles"]), 1), round(pct([[sum(a["niveles"][i][0] for a in datos["actividades"])] for i in range(3)]), 1)) == (78.7, 9.9, 39.6))(lambda f: 100 * (f[0][0] + f[1][0]) / (f[0][0] + f[1][0] + f[2][0])),
        "Base de la participación: Valparaíso 706.053 y Chile 7.395.105": datos["base_ocupados"]["regiones"]["5"] == 706_053 and datos["base_ocupados"]["chile"] == 7_395_105,
        "Cada participación se puede recalcular con ocupados y su base": all(abs(100 * d["ocupados"] / datos["base_ocupados"]["regiones"][str(r)] - d["pct"]) < 0.0051 for a in datos["actividades"] for r, d in a["regiones"].items()),
        "Población: Chile con tasa de desocupación 8,6%, participación 59,6% y 7.801.449 con lugar de trabajo": pob["chile"]["tasa_desocupacion"] == 8.6 and pob["chile"]["tasa_participacion"] == 59.6 and pob["chile"]["lugar_trabajo"] == 7_801_449,
        "Población: ocupados por lugar de trabajo suman Chile; Antofagasta 372.015": sum(d["lugar_trabajo"] for d in pob["regiones"].values()) == pob["chile"]["lugar_trabajo"] and pob["regiones"]["2"]["lugar_trabajo"] == 372_015,
        "La plantilla quedó completa": "__DATOS__" not in html and "__GEO__" not in html,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Celdas sin dato: %d; mayor cambio de área: %.3f%% al reconstruir y %.3f%% al simplificar", sin_dato, geo["diferencia_area_pct"], geo["diferencia_simplificada_pct"])
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")
