"""
<src/Visualizacion/controles.py>

Controles que detienen la generación si los datos dejan de respaldar el color, la lectura o las frases de la página.

Las cifras van escritas a mano a propósito: el título, los hallazgos y las anotaciones las afirman en texto, y si los
datos cambian, el mapa no debe publicarse con frases que ya no son ciertas.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from config import CLASE_NEUTRA, COLOR_RESUMEN, CORTES_ROJO, DIFERENCIA_AREA_MAXIMA_PCT, DIFERENCIA_AREA_SIMPLIFICADA_MAXIMA_PCT, MINIMO_VISIBLE, NOMBRES_REGION, OCUPADO, OCUPADOS_DIVERSIDAD_GENERO, OCUPADOS_GENERO_SUPRIMIDO, POBLACION_POR_SEXO, POBLACION_TOTAL_CENSO, RUTA_PERSONAS, TRAMOS_EDAD, TRAMOS_IGUAL_EDAD
from formato import de_cada_10
from indicadores import clase_color

# Tramos donde la página afirma que la diferencia por título "se mantiene a igual edad" (comun/tramos_edad.py); los
# demás se muestran pero no entran.
IGUAL_EDAD = TRAMOS_IGUAL_EDAD

log = logging.getLogger(__name__)


def totales_sexo_genero_correctos() -> bool:
    """Compara las constantes con los microdatos; regenerar el mapa no los exige, así que sin ellos no hay nada que comparar."""
    if not RUTA_PERSONAS.exists():
        return True
    d = pd.read_parquet(RUTA_PERSONAS, columns=["sexo", "div_genero", "sit_fuerza_trabajo"])
    genero = d.loc[d["sit_fuerza_trabajo"] == OCUPADO, "div_genero"].value_counts()
    return d["sexo"].value_counts().to_dict() == POBLACION_POR_SEXO and genero[1] == OCUPADOS_DIVERSIDAD_GENERO and genero[-66] == OCUPADOS_GENERO_SUPRIMIDO


# Los nombres oficiales se escribieron a mano y 4 de 20 no estaban en ningún glosario: se comparan con la fuente.
RUTA_DICCIONARIO_CENSO = Path(__file__).resolve().parents[2] / "Datos" / "datos_externos" / "glosarios" / "CENSO_2024" / "diccionario_variables_censo2024.xlsx"


def nombres_segun_diccionario(actividades: list[dict]) -> bool:
    """Compara el nombre oficial de cada actividad con la etiqueta de cod_caenes en el diccionario del Censo 2024."""
    d = pd.read_excel(RUTA_DICCIONARIO_CENSO, sheet_name="tabla_personas", header=None, usecols=[1, 3, 4])
    d = d[d[1] == "cod_caenes"]
    oficial = dict(zip(d[3].astype(str).str.strip(), d[4].astype(str).str.strip()))
    return all(oficial.get(a["ciiu"]) == a["glosa"] for a in actividades)


def nombres_globales_js(codigo: str) -> list[str]:
    """Nombres que un archivo JS define a nivel superior: function, const y let al inicio de línea, fuera de cualquier bloque."""
    nombres = []
    for linea in codigo.splitlines():
        if linea.startswith("function "):
            nombres.append(re.match(r"function (\w+)", linea).group(1))
        if not linea.startswith(("const ", "let ")):
            continue
        # Separa sentencias por ";" y nombres por "," solo fuera de paréntesis, corchetes, llaves, textos y plantillas.
        nivel, comilla, actual, sentencias, partes = 0, None, "", [], []
        for c in linea:
            if comilla:
                comilla = None if c == comilla else comilla
            elif c in "'\"`":
                comilla = c
            elif c in "([{":
                nivel += 1
            elif c in ")]}":
                nivel -= 1
            elif nivel == 0 and c in ",;":
                partes.append(actual); actual = ""
                if c == ";":
                    sentencias.append(partes); partes = []
                continue
            actual += c
        sentencias.append(partes + [actual])
        for partes in sentencias:
            if partes and re.match(r"\s*(const|let) ", partes[0]):
                partes[0] = re.sub(r"\s*(const|let) ", "", partes[0], count=1)
                nombres += [m.group(1) for x in partes if (m := re.match(r"\s*(\w+)\s*=", x))]
    return nombres


def validar(datos: dict, geo: dict, html: str, codigo_js: dict[str, str], sin_listar: list[str]) -> None:
    celdas = [d for a in datos["actividades"] for d in a["regiones"].values() if d["clase"] is not None]
    lectura_esperada = lambda c: "bajo_lo_nacional" if c < CLASE_NEUTRA else "similar" if c == CLASE_NEUTRA else "concentra"
    con_base = [d for d in celdas if d["lectura"] != "base_pequena"]
    texto_calza = lambda d: clase_color(float(d["peso_txt"].replace(",", "."))) == d["clase"]
    sin_dato = sum(d["clase"] is None for a in datos["actividades"] for d in a["regiones"].values())
    pob = datos["poblacion"]
    por_ciiu = {a["ciiu"]: a for a in datos["actividades"]}
    evo_filas = [datos["evolucion"]["chile"], *datos["evolucion"]["niveles"].values(), *datos["evolucion"]["regiones"].values()]
    controles = {
        "El color coincide con la lectura en todas las celdas": all(lectura_esperada(d["clase"]) == d["lectura"] for d in con_base),
        "La cifra visible cae en el tramo de su color": all(texto_calza(d) for d in celdas),
        "20 actividades en la lista": len(datos["actividades"]) == 20 and "U" not in [a["ciiu"] for a in datos["actividades"]],
        "Nombres oficiales: los 20 coinciden con el diccionario del Censo 2024": nombres_segun_diccionario(datos["actividades"]),
        "Bordes válidos antes y después de simplificar": geo["geometria_valida"],
        "El área de cada región cambia menos de 0,5% al reconstruir los bordes": geo["diferencia_area_pct"] < DIFERENCIA_AREA_MAXIMA_PCT,
        "El área de cada región cambia menos de 1% al simplificar": geo["diferencia_simplificada_pct"] < DIFERENCIA_AREA_SIMPLIFICADA_MAXIMA_PCT,
        "Minería en Chile: 268.491 con región y 275.517 en total": por_ciiu["B"]["nacional"]["ocupados"] == 268_491 and por_ciiu["B"]["nacional"]["censo_total"] == 275_517,
        # La frase que reemplazó al aviso de edad en Trabajo por región se arma con estos conteos: si cambian, se revisa.
        # En Chile el ajuste por edad debe dar su propia cifra con edad conocida (la mezcla de referencia es la de Chile).
        "Edad y empleo por región: ajustando por edad, 14 de 16 regiones en el mismo puesto (máx. 1) en ocupados y 16 de 16 en participación; en Chile el ajuste no cambia nada": (
            (e := datos["poblacion"]["edad"])["puestos"] == {"ocu": {"iguales": 14, "max": 1}, "par": {"iguales": 16, "max": 0}}
            and e["ajuste_chile_exacto"] and e["chile"]["ocu_aj"] == e["chile_con_edad"] and e["chile"]["ocu"] == datos["poblacion"]["chile"]["pct_trabajan"]
            and all(e["regiones"][str(r)]["ocu"] == datos["poblacion"]["regiones"][str(r)]["pct_trabajan"] for r in range(1, 17))),
        # El gráfico "Región donde más pesa" pinta cada barra con el tramo del mapa y nombra a las que no llegan a 1,2: esa
        # frase solo vale si no concentrar en su región de mayor CL equivale a no concentrar en ninguna.
        "CL del resumen: Comercio, Servicios administrativos y Hogares no concentran en ninguna región, y las barras usan el color del mapa": (
            {c for c, a in por_ciiu.items() if not any(v["lectura"] == "concentra" for v in a["regiones"].values())}
            == {c for c, a in por_ciiu.items() if a["regiones"][a["nacional"]["mas_peso"]["r"]]["lectura"] != "concentra"} == {"G", "N", "T"}
            and "background:${relleno(v)}" in re.search(r"function graficoCL\(\)\{.*?\n// ", codigo_js["js/vistas/resumen.js"], re.S).group(0)),
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
        "Título de Actividades: mujeres de 93,4% en Hogares a 8,5% en Construcción; Minería con CL 8,06 en Antofagasta": (lambda s: (s[0][0], round(s[0][1], 1), s[-1][0], round(s[-1][1], 1)) == ("T", 93.4, "F", 8.5))(sorted(((a["ciiu"], a["sexo"]["pct_m"]) for a in datos["actividades"]), key=lambda x: -x[1]))
            and (datos["resumen"]["mas_desiguales"][0]["txt"], datos["resumen"]["mas_desiguales"][0]["r"]) == ("8,06", 2),
        "Resumen: Minería y Agricultura son las más desiguales": [d["ciiu"] for d in datos["resumen"]["mas_desiguales"]] == ["B", "A"],
        # La leyenda del mapa dice que el color suave también pesa más que en Chile: ninguna región puede quedar bajo 1,2.
        "Resumen: la actividad con mayor CL de cada región tiene CL de 1,2 o más": all(round(d["peso"], 2) >= CORTES_ROJO[0] for d in datos["resumen"]["regiones"].values()),
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
        # La fila de Chile del gráfico por región se suma desde las personas: debe calzar con las cifras de cada nivel.
        # "No la explica la edad" (tarjeta y Estudios y trabajo): las 16 regiones con menor desocupación con título en cada
        # tramo de 25 a 64; Chile de 8,7/11,3 (25-34) a 5,3/8,0 (55-64); al revés de 18 a 24; nadie con título de 15 a 17;
        # Aysén con 20% sin edad.
        "Estudios por edad: 16 regiones con título menor en cada tramo de 25 a 64; Chile 8,7/11,3 y 5,3/8,0; al revés de 18 a 24; sin título de 15 a 17; Aysén 20% sin edad": (lambda d: (
            d["regiones_igual_edad"] == 16 and d["chile"]["25-34"] == [8.7, 11.3] and d["chile"]["55-64"] == [5.3, 8.0]
            and d["chile"]["18-24"][0] > d["chile"]["18-24"][1] and d["chile"]["15-17"][0] is None and d["sin_edad"] == ["11", 20, 3.9]
            and all(v[0] < v[1] for t, v in d["chile"].items() if t not in ("15-17", "18-24"))))(datos["estudios"]["edad"]),
        # Una sola definición de tramos (comun/tramos_edad.py): si una tabla por edad se aparta, las secciones dejan de
        # poder compararse entre sí, que es lo que pasaba con 15-24 y 18-64.
        "Edad: las 3 tablas por edad (Trabajo por región, Estudios y trabajo, Formalidad) usan los mismos 7 tramos, de 15-17 a 65 o más": (
            datos["tramos_edad"] == TRAMOS_EDAD == ["15-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
            and datos["poblacion"]["edad"]["tramos"] == TRAMOS_EDAD and list(datos["estudios"]["edad"]["chile"]) == TRAMOS_EDAD
            and list(datos["formalidad"]["tramos_chile"]) == TRAMOS_EDAD),
        "Estudios: Chile 6,8% con título y 9,7% sin título, igual que sumar los niveles": (lambda e: e["desocupacion_titulo_chile"] == [6.8, 9.7]
            and round(100 * (e["niveles"]["Profesional"]["desocupados"] + e["niveles"]["Tecnico"]["desocupados"]) / sum(e["niveles"][n]["ocupados"] + e["niveles"][n]["desocupados"] for n in ("Profesional", "Tecnico")), 1) == 6.8
            and e["desocupacion_titulo_chile"][1] == e["niveles"]["Sin_titulo"]["tasa_desocupacion"])(datos["estudios"]),
        "Educación por región: suma 15.102.704 y va de Maule (21,1%) a la Metropolitana (32,9%)": (lambda e: sum(e["chile"]) == 15_102_704 and sum(sum(v) for r, v in e.items() if r != "chile") == sum(e["chile"])
            and sorted((round(100 * (v[0] + v[1]) / sum(v), 1), int(r)) for r, v in e.items() if r != "chile")[::15] == [(21.1, 7), (32.9, 13)])(datos["estudios"]["educacion"]),
        "Educación por región: se excluyen 97.157 sin nivel y 5.923 sin situación laboral, y con la tabla suman los 15 años o más":
            datos["estudios"]["excluidos"] == {"sin_nivel": 97_157, "sin_situacion": 5_923} and sum(datos["estudios"]["educacion"]["chile"]) + sum(datos["estudios"]["excluidos"].values()) == pob["chile"]["total"],
        "Educación por región: Chile 28,2% con título": (lambda c: round(100 * (c[0] + c[1]) / sum(c), 1) == 28.2)(datos["estudios"]["educacion"]["chile"]),
        "Hallazgos: 4 de cada 10 ocupados con título; 1 de cada 10 en Hogares y 8 de cada 10 en Servicios profesionales": (lambda p: de_cada_10(datos["estudios"]["pct_con_titulo"]) == 4 and (de_cada_10(min(p)), de_cada_10(max(p))) == (1, 8))(
            [100 * (a["niveles"][0][0] + a["niveles"][1][0]) / sum(f[0] for f in a["niveles"]) for a in datos["actividades"]]),
        "Desocupación menor con título en las 16 regiones: con título de Aysén (4,2%) a Biobío (9,1%); sin título de Aysén (6,2%) a La Araucanía (11,6%)": (lambda d: len(d) == 16 and all(c < t for c, t in d.values())
            and [(r, d[r][i]) for i in (0, 1) for r in (min(d, key=lambda r: d[r][i]), max(d, key=lambda r: d[r][i]))] == [("11", 4.2), ("8", 9.1), ("11", 6.2), ("9", 11.6)])(datos["estudios"]["desocupacion_titulo"]),
        "Nivel por actividad: Minería en Chile 82.082 profesionales; Antofagasta 28.576": (lambda a: a["niveles"][0] == [82_082, 30.6, 61_954, 20_128, 27.3, 48.7] and a["regiones"][2]["niveles"][0] == [28_576, 28.0, 21_907, 6_669, 25.3, 43.3])(por_ciiu["B"]),
        "Nivel por actividad: solo faltan 2.757 ocupados sin nivel informado": sum(d["ocupados"] for a in datos["actividades"] for d in a["regiones"].values()) - sum(f[0] for a in datos["actividades"] for d in a["regiones"].values() for f in d["niveles"]) == 2_757,
        "Nivel por actividad: hombres y mujeres suman el total cuando ambos se muestran": all(f[2] + f[3] == f[0] for a in datos["actividades"] for d in [a, *a["regiones"].values()] for f in d["niveles"] if f[2] is not None and f[3] is not None),
        "Nivel por actividad: 16 filas regionales con menos de 10, y ninguna nacional": sum(f[2] is None or f[3] is None for a in datos["actividades"] for d in a["regiones"].values() for f in d["niveles"]) == 16 and not any(f[2] is None or f[3] is None for a in datos["actividades"] for f in a["niveles"]),
        "Nivel por actividad: todas las actividades 27,3%, 12,3% y 60,4%": datos["perfil_estudios"]["todas"] == [27.3, 12.3, 60.4],
        "Sexo por región: en cada celda, hombres y mujeres suman sus ocupados cuando ambos se muestran": all(d["h"] + d["m"] == d["ocupados"] for a in datos["actividades"] for d in a["regiones"].values() if d["h"] is not None and d["m"] is not None),
        "Sexo por región: bajo 10 no se escribe la cifra ni su participación": all((d[s] is None) == (d["pct_" + s] is None) and (d[s] is None or d[s] >= MINIMO_VISIBLE) for a in datos["actividades"] for d in a["regiones"].values() for s in ("h", "m")),
        "Sexo por región: las bases suman la base de cada región y de Chile": all(v["h"] + v["m"] == datos["base_ocupados"]["regiones"][r] for r, v in datos["base_ocupados"]["sexo"]["regiones"].items()) and sum(datos["base_ocupados"]["sexo"]["chile"].values()) == datos["base_ocupados"]["chile"],
        "Sexo por región: Biobío en Salud 15.108 y 45.643; 4,91% y 17,22%": (lambda d: (d["h"], d["m"], d["pct_h"], d["pct_m"]) == (15_108, 45_643, 4.91, 17.22))(por_ciiu["Q"]["regiones"][8]),
        "Situación por sexo: cada región suma sus grupos": all(d["sexo"]["hombres"][k] + d["sexo"]["mujeres"][k] == d[k] for d in pob["regiones"].values() for k in ("total", "trabajan", "buscan", "no_buscan", "sin_dato")),
        "Nivel por sexo: suma los ocupados y desocupados de cada región y de Chile": all(d["sexo"]["oh"] + d["sexo"]["om"] == d["ocupados"] and d["sexo"]["dh"] + d["sexo"]["dm"] == d["desocupados"] for g in datos["niveles"].values() for d in g.values()) and all(d["sexo"]["oh"] + d["sexo"]["om"] == d["ocupados"] and d["sexo"]["dh"] + d["sexo"]["dm"] == d["desocupados"] for d in datos["niveles_chile"].values()),
        # Ocupados, desocupados y tasa van en la misma base (residencia), así que la cuenta del lector reproduce la tasa.
        "Nivel por región: desocupados / (ocupados + desocupados) da la tasa en las 48 filas y en las 96 por sexo; Antofagasta técnico 36.901, 2.731 y 6,9%":
            all(round(100 * d["desocupados"] / (d["ocupados"] + d["desocupados"]), 1) == d["tasa"]
                and round(100 * d["sexo"]["dh"] / (d["sexo"]["oh"] + d["sexo"]["dh"]), 1) == d["sexo"]["th"]
                and round(100 * d["sexo"]["dm"] / (d["sexo"]["om"] + d["sexo"]["dm"]), 1) == d["sexo"]["tm"] for g in datos["niveles"].values() for d in g.values())
            and (lambda d: (d["ocupados"], d["desocupados"], d["tasa"]) == (36_901, 2_731, 6.9))(datos["niveles"]["2"]["Tecnico"]),
        # Misma regla que lecturaDesocNivel (region.js): diferencia con tasas redondeadas; bajo 0,5 pp es "casi igual".
        "Desocupación por nivel: baja con más estudios en las 16 regiones; Antofagasta menor y Coquimbo mayor que Chile en los 3 niveles; Atacama mayor solo en técnico; Valparaíso 0,5 cuenta como mayor":
            (lambda cat: all(g["Profesional"]["tasa"] < g["Tecnico"]["tasa"] < g["Sin_titulo"]["tasa"] for g in datos["niveles"].values())
             and cat("2") == ["menor"] * 3 and cat("4") == ["mayor"] * 3 and cat("3") == ["igual", "mayor", "igual"] and cat("5") == ["mayor", "igual", "igual"])(
                lambda r: [(lambda d: "igual" if abs(d) < 0.5 else "menor" if d < 0 else "mayor")(round(round(datos["niveles"][r][n]["tasa"] - datos["niveles"][r][n]["nacional"], 1) * 10) / 10)
                           for n in ("Profesional", "Tecnico", "Sin_titulo")]),
        # Misma regla que lecturaSexoRegion (region.js): brecha de participación con tasas redondeadas, como la de la portada.
        "Sexo por región: brecha mayor en O'Higgins y Maule (23,8) y menor en Aysén (13,4), frente a 19,5 en Chile; Magallanes con más desocupación en mujeres (6,7% y 6,1%)":
            (lambda reg, brecha: brecha(pob["sexo"]) == 19.5 and max(brecha(reg[r]["sexo"]) for r in reg) == brecha(reg["6"]["sexo"]) == brecha(reg["7"]["sexo"]) == 23.8
             and min(brecha(reg[r]["sexo"]) for r in reg) == brecha(reg["11"]["sexo"]) == 13.4
             and (reg["12"]["sexo"]["mujeres"]["tasa_desocupacion"], reg["12"]["sexo"]["hombres"]["tasa_desocupacion"]) == (6.7, 6.1))(
                {str(k): v for k, v in pob["regiones"].items()}, lambda x: round(round(x["hombres"]["tasa_participacion"] - x["mujeres"]["tasa_participacion"], 1) * 10) / 10),
        # Traslado medido con la región de residencia y de trabajo de cada ocupado: el cuadre debe cerrar exacto en cada
        # región, lo que sale de una región llega a otra, y la fila A nunca supera a los que trabajan en la región.
        # Fija O'Higgins (salen más de los que llegan) y la Metropolitana (llegan más), que el supuesto anterior invertía.
        "Traslado por región: viven − sin región − salen + llegan = trabajan en ella en las 16; salen = llegan = 292.221; O'Higgins −5.767 y Metropolitana +20.913":
            (lambda reg: all(x["trabajan"] - x["sin_region_trabajo"] - x["salen"] + x["llegan"] == x["lugar_trabajo"] for x in reg.values())
             and sum(x["salen"] for x in reg.values()) == sum(x["llegan"] for x in reg.values()) == pob["chile"]["salen"] == 292_221
             and sum(x["sin_region_trabajo"] for x in reg.values()) == pob["chile"]["sin_region_trabajo"] == pob["chile"]["trabajan"] - pob["chile"]["lugar_trabajo"]
             and sum(datos["base_ocupados"]["regiones"].values()) == datos["base_ocupados"]["chile"]
             and all(x["lugar_trabajo"] - datos["base_ocupados"]["regiones"][r] >= 0 for r, x in reg.items())
             and (reg["6"]["trabajan"], reg["6"]["sin_region_trabajo"], reg["6"]["salen"], reg["6"]["llegan"], reg["6"]["lugar_trabajo"], datos["base_ocupados"]["regiones"]["6"]) == (423_209, 16_256, 22_938, 17_171, 401_186, 385_312)
             and reg["6"]["llegan"] - reg["6"]["salen"] == -5_767 and reg["13"]["llegan"] - reg["13"]["salen"] == 20_913)(
                {str(k): v for k, v in pob["regiones"].items()}),
        # El gráfico de CL de cada región (region.js) usa escala logarítmica con dominio fijo de 1/16 a 16: un CL fuera
        # de ese rango, o nulo, se saldría de la barra. Los conteos fijan la frase de lectura con los cortes del mapa.
        "CL por región: los 320 CL caben entre 1/16 y 16; O'Higgins 2 sobre, 11 similares y 7 bajo Chile; Antofagasta 3, 4 y 13":
            all(x["regiones"][r]["peso"] is not None and 1 / 16 < x["regiones"][r]["peso"] < 16 for x in datos["actividades"] for r in x["regiones"])
            and all([sum(x["regiones"][r]["lectura"] == k for x in datos["actividades"]) for k in ("concentra", "similar", "bajo_lo_nacional")] == c
                    for r, c in ((6, [2, 11, 7]), (2, [3, 4, 13]))),
        # El circular de áreas (carreras.js) dibuja hasta 4 áreas y "Otras áreas" con el resto hasta 100%: el resto no puede
        # ser negativo, ni en % ni en titulados, y debe coincidir con el % que dan sus titulados (0,5 por redondeo).
        "Áreas, circular: hasta 4 áreas y Otras áreas no negativa, que cuadra con sus titulados; Construcción 12,2% e Inmobiliarias 52,5%":
            all(len(a["areas"]) <= 4 and (r := round(100 - sum(x["pct"] for x in a["areas"]), 1)) >= 0
                and (t := a["tit_casen"] - sum(x["tit"] for x in a["areas"])) >= 0 and abs(100 * t / a["tit_casen"] - r) <= 0.5
                for a in datos["actividades"] if a["areas"])
            and [round(100 - sum(x["pct"] for x in por_ciiu[c]["areas"]), 1) for c in ("F", "L")] == [12.2, 52.5],
        "Títulos por sexo: hombres y mujeres no superan el total; Enfermería 845 y 4.123": all(f["tit_h"] + f["tit_m"] <= f["tit"] for f in datos["fichas"].values()) and (datos["fichas"]["ENFERMERIA"]["tit_h"], datos["fichas"]["ENFERMERIA"]["tit_m"]) == (845, 4_123),
        "Sexo y género: las constantes coinciden con los microdatos, si están": totales_sexo_genero_correctos(),
        "Población: el total coincide con los microdatos, si están": not RUTA_PERSONAS.exists() or pq.ParquetFile(RUTA_PERSONAS).metadata.num_rows == POBLACION_TOTAL_CENSO,
        # La columna "Con título" se calcula en la página desde estas personas; aquí se fija contra la fuente.
        "Con título por actividad: Servicios profesionales 78,7%, Hogares 9,9% y todas 39,6%": (lambda pct: (round(pct(por_ciiu["M"]["niveles"]), 1), round(pct(por_ciiu["T"]["niveles"]), 1), round(pct([[sum(a["niveles"][i][0] for a in datos["actividades"])] for i in range(3)]), 1)) == (78.7, 9.9, 39.6))(lambda f: 100 * (f[0][0] + f[1][0]) / (f[0][0] + f[1][0] + f[2][0])),
        "Base de la participación: Valparaíso 706.053 y Chile 7.395.105": datos["base_ocupados"]["regiones"]["5"] == 706_053 and datos["base_ocupados"]["chile"] == 7_395_105,
        "Cada participación se puede recalcular con ocupados y su base": all(abs(100 * d["ocupados"] / datos["base_ocupados"]["regiones"][str(r)] - d["pct"]) < 0.0051 for a in datos["actividades"] for r, d in a["regiones"].items()),
        "Población: Chile con tasa de desocupación 8,6%, participación 59,6% y 7.801.449 con lugar de trabajo": pob["chile"]["tasa_desocupacion"] == 8.6 and pob["chile"]["tasa_participacion"] == 59.6 and pob["chile"]["lugar_trabajo"] == 7_801_449,
        "Población: ocupados por lugar de trabajo suman Chile; Antofagasta 372.015": sum(d["lugar_trabajo"] for d in pob["regiones"].values()) == pob["chile"]["lugar_trabajo"] and pob["regiones"]["2"]["lugar_trabajo"] == 372_015,
        # Los títulos del resumen salen de los datos; aquí se fija lo que afirman hoy.
        "Títulos: la desocupación por región va de Aysén (5,4%) a La Araucanía (10,4%)": (lambda t: (min(t, key=t.get), t[min(t, key=t.get)], max(t, key=t.get), t[max(t, key=t.get)]) == ("11", 5.4, "9", 10.4))({r: d["tasa_desocupacion"] for r, d in pob["regiones"].items()}),
        "Evolución: Chile 8,6% en 2024 y 9,5% en 2026, sube; 16 regiones y 3 niveles": (lambda e: (e["chile"]["t24"], e["chile"]["t26"], e["chile"]["lect"]) == (8.6, 9.5, "sube") and len(e["regiones"]) == 16 and len(e["niveles"]) == 3)(datos["evolucion"]),
        "Evolución: sube o baja solo si el rango publicado queda a un lado del cero": all(d["lect"] == ("sube" if d["min"] > 0 else "baja" if d["max"] < 0 else "sin_cambio_claro") for d in evo_filas),
        "Evolución: el cambio publicado es la resta de las tasas y cae en su rango": all(d["dif"] == round(d["t26"] - d["t24"], 1) and d["min"] <= d["dif"] <= d["max"] for d in evo_filas),
        "Evolución: suben Arica y Parinacota, Tarapacá, Valparaíso, Biobío y Los Lagos; ninguna baja": sorted(int(r) for r, d in datos["evolucion"]["regiones"].items() if d["lect"] == "sube") == [1, 5, 8, 10, 15] and not any(d["lect"] == "baja" for d in evo_filas),
        "Formalidad: Chile 26,6% informal y 24,1% independiente; 12,3%, 17,1% y 36,0% por nivel": (lambda f: (f["chile"]["inf"][1], f["chile"]["ind"][1], f["niveles"]["Profesional"]["inf"][1], f["niveles"]["Tecnico"]["inf"][1], f["niveles"]["Sin_titulo"]["inf"][1]) == (26.6, 24.1, 12.3, 17.1, 36.0))(datos["formalidad"]),
        # La frase por región usa grupos: los que se cruzan con la más informal (todos sobre Chile con su rango) y los que
        # quedan bajo Chile con su rango; los dos grupos no se cruzan entre sí. Si cambia, la frase ya no es la medida.
        "Formalidad: 16 regiones fiables; más alta en La Araucanía, Ñuble, Los Ríos y Arica (sobre Chile), bajo Chile Antofagasta, Magallanes y Metropolitana; los grupos no se cruzan": (lambda t, c: (
            len(t) == 16 and all(d["fiab"] == "fiable" for d in t.values())
            and (lambda top: sorted(r for r, d in t.items() if d["inf"][1] + d["mas"] >= top["inf"][1] - top["mas"]))(max(t.values(), key=lambda d: d["inf"][1])) == ["14", "15", "16", "9"]
            and all(t[r]["inf"][1] - t[r]["mas"] > c for r in ("9", "14", "15", "16"))
            and sorted(r for r, d in t.items() if d["inf"][1] + d["mas"] < c) == ["12", "13", "2"]
            and max(t[r]["inf"][1] + t[r]["mas"] for r in ("2", "12", "13")) < min(t[r]["inf"][1] - t[r]["mas"] for r in ("9", "14", "15", "16"))))(datos["formalidad"]["regiones"], datos["formalidad"]["chile"]["inf"][1]),
        # El complemento se muestra para que el lector vea las dos partes: formal e informal suman 100 exacto en el %
        # y, en miles, el total con 1 de tolerancia por redondear cada cifra.
        "Formalidad: formal e informal suman 100% y los ocupados de cada fila": all(round(d["for"][1] + d["inf"][1], 1) == 100 and abs(d["for"][0] + d["inf"][0] - d["ocup"]) <= 1
            for d in [datos["formalidad"]["chile"], *datos["formalidad"]["niveles"].values(), *datos["formalidad"]["regiones"].values(), *datos["formalidad"]["actividades"].values()]),
        # La tabla redondea cada casilla: se tolera 0,2 de diferencia al sumar cinco cifras de un decimal.
        "Formalidad: los repartos suman 100 y la informalidad es la suma de sus casillas": all(abs(d["af"][1] + d["ai"][1] + d["xf"][1] + d["xi"][1] + d["fam"][1] - 100) <= 0.2 and abs(d["ai"][1] + d["xi"][1] + d["fam"][1] - d["inf"][1]) <= 0.2
            for d in [datos["formalidad"]["chile"], *datos["formalidad"]["niveles"].values()] if d["fam"]),
        # La frase "se mantiene a igual edad" de la sección se apoya en esto: 3 niveles x 4 tramos, y en cada
        # tramo el rango de sin título queda entero sobre el de profesional.
        "Formalidad: por edad, los 7 tramos en asalariados e independientes (sin título superior de 15 a 17 años); de 25 a 64, independientes fiables y sin título sobre profesional con todo el rango; ± 1,3 y 2,4 en los niveles": (lambda f, x: (
            all(sorted(f["tramos"][g]) == ["Profesional", "Sin_titulo", "Tecnico"] and all(list(v) == (TRAMOS_EDAD if n == "Sin_titulo" else TRAMOS_EDAD[1:]) for n, v in f["tramos"][g].items()) for g in ("asa", "inx"))
            and all(c[e][2] == "fiable" for c in x.values() for e in IGUAL_EDAD)
            and all(x["Sin_titulo"][e][0] - x["Sin_titulo"][e][1] > x["Profesional"][e][0] + x["Profesional"][e][1] for e in IGUAL_EDAD)
            and (f["niveles"]["Sin_titulo"]["inx_mas"], f["niveles"]["Profesional"]["inx_mas"]) == (1.3, 2.4)))(datos["formalidad"], datos["formalidad"]["tramos"]["inx"]),
        # "La diferencia es mayor entre los de más edad" (tarjeta y sección): el rango de profesionales de 25-34 queda entero
        # sobre el de 55-64, y la diferencia con sin título es mayor en 55-64. Si deja de cumplirse, la frase ya no es cierta.
        "Formalidad: independientes profesionales de 25-34 sobre los de 55-64 con todo el rango, y diferencia con sin título mayor en 55-64": (lambda x: (
            x["Profesional"]["25-34"][0] - x["Profesional"]["25-34"][1] > x["Profesional"]["55-64"][0] + x["Profesional"]["55-64"][1]
            and x["Sin_titulo"]["55-64"][0] - x["Profesional"]["55-64"][0] > x["Sin_titulo"]["25-34"][0] - x["Profesional"]["25-34"][0]))(datos["formalidad"]["tramos"]["inx"]),
        # La fila Chile de la tabla por edad está para comprobar que las filas cuadran: la nota dice que es su suma.
        # De 15 a 17 solo hay filas sin título superior: nadie tiene título a esa edad.
        "Formalidad: por edad, las 6 filas (asalariados e independientes por nivel) suman la fila Chile (±6 por redondeo), y cada % informal es el de sus ocupados": (lambda f, ch: all(
            abs(sum(f[g][n][e][i] for g in f for n in f[g] if e in f[g][n]) - ch[e][i]) <= 6 for e in ch for i in (3, 4))
            and all(abs(100 * c[4] / (c[3] + c[4]) - c[0]) <= 0.1 for c in [*ch.values(), *(f[g][n][e] for g in f for n in f[g] for e in f[g][n])]))(
            datos["formalidad"]["tramos"], datos["formalidad"]["tramos_chile"]),
        # La línea de cuadre de la tabla por edad: la tabla más lo que queda fuera da los formales e informales de Chile.
        "Formalidad: la tabla por edad más los sin nivel informado suman los asalariados e independientes formales e informales de Chile (±10)": (lambda f: all(
            abs(sum(v[i] for v in f["tramos_chile"].values()) + f["sin_nivel"][i - 3] - tot) <= 10
            for i, tot in ((3, f["chile"]["af"][0] + f["chile"]["xf"][0]), (4, f["chile"]["ai"][0] + f["chile"]["xi"][0]))))(datos["formalidad"]),
        "Formalidad: informales dentro de cada grupo, asalariados 16,4% e independientes 57,0% en Chile; independientes 22,6% profesional y 69,2% sin título": (lambda f: (f["chile"]["asa"][1], f["chile"]["inx"][1], f["niveles"]["Profesional"]["inx"][1], f["niveles"]["Sin_titulo"]["inx"][1]) == (16.4, 57.0, 22.6, 69.2))(datos["formalidad"]),
        "Formalidad: los ocupados de asalariados e independientes son la suma de sus casillas publicadas y cuadran con los ocupados": all(d["asa"][0] == d["af"][0] + d["ai"][0] and d["inx"][0] == d["xf"][0] + d["xi"][0] and abs(d["inx"][0] - d["ind"][0]) <= 1 and (d["fam"] is None or abs(d["asa"][0] + d["inx"][0] + d["fam"][0] - d["ocup"]) <= 2)
            for d in [datos["formalidad"]["chile"], *datos["formalidad"]["niveles"].values()]),
        "Formalidad: familiar no remunerado sin muestra solo en Profesional y Técnico": datos["formalidad"]["chile"]["fam"] is not None and {k for k, d in datos["formalidad"]["niveles"].items() if d["fam"] is None} == {"Profesional", "Tecnico"},
        # Gráfico por actividad: las 20 del mapa, 15 con informal fiable (las otras 5, las más formales, llevan etiqueta);
        # de más a menos formal, Minería 96,0% a Hogares 40,9%; y lo que falta para Chile (sin rama y organismos
        # internacionales) es menos de 1%, como lo dice su nota.
        # Título del gráfico por actividad: el grupo sobre 93% formal y la más informal, que se separa de la segunda con su
        # margen. Frase de independientes: Servicios profesionales y Comercio con el mismo % de independientes (los rangos se
        # cruzan) y un % informal dentro de ellos muy distinto (fiables y sin cruzarse).
        "Formalidad: sobre 93% formal Minería, Electricidad y Finanzas; Hogares la más informal con todo su rango": (lambda a: (
            sorted(k for k, d in a.items() if d["for"][1] > 93) == ["B", "D", "K"]
            and (lambda o: o[0][0] == "T" and o[0][1]["inf"][1] - o[0][1]["mas"] > o[1][1]["inf"][1] + o[1][1]["mas"])(sorted(a.items(), key=lambda x: -x[1]["inf"][1]))))(datos["formalidad"]["actividades"]),
        "Formalidad: independientes en Servicios profesionales y Comercio, mismo % (rangos se cruzan) y 14,0% frente a 56,6% informal (fiables, sin cruzarse)": (lambda m, g: (
            m["ind"] is not None and g["ind"] is not None and abs(m["ind"][1] - g["ind"][1]) < m["ind_mas"] + g["ind_mas"]
            and m["xi"][2] == g["xi"][2] == "fiable" and m["xi"][0] + m["xi"][1] < g["xi"][0] - g["xi"][1]
            and (m["xi"][0], g["xi"][0]) == (14.0, 56.6)))(datos["formalidad"]["actividades"]["M"], datos["formalidad"]["actividades"]["G"]),
        "Formalidad: 20 actividades, 15 con informal fiable e independientes en 14; formal de 96,0% en Minería a 40,9% en Hogares; suman Chile salvo menos de 1%": (lambda a, c: (
            set(a) == set(por_ciiu) and sum(d["fiab"] == "fiable" for d in a.values()) == 15 and sum(d["ind"] is not None for d in a.values()) == 14
            and all(d["fiab"] in ("fiable", "poco_fiable", "no_fiable") and d["mas"] is not None for d in a.values())
            and (lambda o: (o[0][0], o[0][1]["for"][1], o[-1][0], o[-1][1]["for"][1]) == ("B", 96.0, "T", 40.9))(sorted(a.items(), key=lambda x: x[1]["inf"][1]))
            and 0 < c["ocup"] - sum(d["ocup"] for d in a.values()) < c["ocup"] / 100))(datos["formalidad"]["actividades"], datos["formalidad"]["chile"]),
        # La sección de áreas cuenta una actividad solo si todo su rango de 95% supera 50%: con el valor puntual,
        # Electricidad (54,0%, rango 45,0 a 63,0) entraba sin que la muestra lo permita.
        "Áreas: 5 actividades con más de la mitad de sus titulados de una sola área (Salud 76,4%, Construcción 65,3%)": sorted(a["ciiu"] for a in datos["actividades"] if a["areas"] and a["areas"][0]["min"] > 50) == ["B", "F", "K", "P", "Q"]
            and por_ciiu["Q"]["areas"][0]["pct"] == 76.4 and por_ciiu["F"]["areas"][0]["pct"] == 65.3,
        "Áreas: solo Enseñanza y Salud superan 50% en las dos direcciones; Construcción reúne 14,3% de Ingeniería": sorted(a["ciiu"] for a in datos["actividades"] if a["areas"] and a["areas"][0]["min"] > 50 and a["areas"][0]["en_area_min"] > 50) == ["P", "Q"]
            and (por_ciiu["P"]["areas"][0]["en_area"], por_ciiu["Q"]["areas"][0]["en_area"], por_ciiu["F"]["areas"][0]["en_area"]) == (75.8, 62.8, 14.3),
        # La tabla de cifras publica la base en personas: cada % debe salir de esas mismas cifras (0,1 de tolerancia por
        # redondeo). Las 20 actividades suman 3.585.361 de 3.587.295 titulados: el resto (1.934) está en organismos
        # internacionales, que no son una actividad del mapa pero sí cuentan en el total de cada área.
        "Áreas: los dos % publicados salen de sus bases, y las 20 actividades suman 3.585.361 titulados": all(abs(100 * x["tit"] / a["tit_casen"] - x["pct"]) <= 0.1 and abs(100 * x["tit"] / x["tit_area"] - x["en_area"]) <= 0.1
            for a in datos["actividades"] for x in a["areas"]) and sum(a["tit_casen"] for a in datos["actividades"]) == 3_585_361,
        # La tabla publica el rango como ± (la mitad del rango): vale solo si el rango es simétrico (0,1 por redondeo).
        "Áreas: el margen de error ± representa el rango publicado (simétrico)": all(abs((x[hi] - x[c]) - (x[c] - x[lo])) <= 0.1 + 1e-9
            for a in datos["actividades"] for x in a["areas"] for c, lo, hi in (("pct", "min", "max"), ("en_area", "en_area_min", "en_area_max"))),
        # El periodo de la ENE lo escribe la página desde DATOS.periodos: escrito a mano, quedaría atrás al cambiar los meses.
        # En frases, la región va con enReg ("en la Metropolitana"); nomReg queda para títulos, listas y tablas.
        "Texto: ninguna frase escribe el nombre de una región tras en, de, a o desde sin pasar por enReg": not any(re.search(r"\b(en|En|de|a|desde)( <strong>)? ?\$\{nomReg\(", c) for c in codigo_js.values()),
        "Periodos: ningún JS escribe a mano los meses de la ENE": not any(re.search(r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) a \w+ de 20\d\d", c) for c in codigo_js.values()),
        "Periodos: la página no nombra el periodo de ENE que ya no se usa": "2025-2026" not in html and "diciembre de 2025" not in html,
        "La plantilla quedó completa": all(m not in html for m in ("__DATOS__", "__GEO__", "__ESTILOS__", "__CODIGO__")),
        # Sin módulos, los archivos JS comparten un solo espacio de nombres: uno repetido pisaría al otro sin aviso.
        "JS: ningún nombre global se define en dos archivos": len(todos := [n for c in codigo_js.values() for n in nombres_globales_js(c)]) == len(set(todos)) and len(todos) > 50,
        "Web: todos los archivos de css/ y js/ están en la lista del generador": not sin_listar,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Celdas sin dato: %d; mayor cambio de área: %.3f%% al reconstruir y %.3f%% al simplificar", sin_dato, geo["diferencia_area_pct"], geo["diferencia_simplificada_pct"])
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")
