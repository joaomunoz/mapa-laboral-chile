"""
<src/Visualizacion/indicadores.py>

Cálculos del mapa a partir de las tablas: tramo de color del CL, resúmenes de Chile y de cada región, cifras por
sexo y nivel de estudios, y la evolución de la desocupación según ENE.

Decisiones:
  - El color se decide con el CL redondeado a 2 decimales, la misma cifra que se muestra (06-11-26). Antes se
    usaba el valor completo y la cifra sumaba decimales para calzar (1,598), una precisión que el dato no tiene.
    El CL se calcula completo y se redondea una sola vez, al final.
  - Los cortes 0,8 y 1,2 son los de la lectura de la tabla. Vienen de otro módulo, así que controles.py detiene el
    proceso si el color y la lectura dejan de coincidir.
  - Evolución (08-11-26): el cambio que se publica es la resta de las dos tasas ya redondeadas, para que quien lee
    pueda comprobarla (técnicos: 7,7% y 8,7% dan +1,0, aunque sin redondear sea +0,9). El rango y la lectura
    vienen de la tabla, calculados con los valores completos.
"""

from __future__ import annotations

import pandas as pd

from config import (
    CLASE_NEUTRA, COLOR_RESUMEN, CORTES_AZUL, CORTES_ROJO, DECIMALES_CL, DESOCUPADO, FUERA_FUERZA_TRABAJO, HOMBRE,
    MINIMO_VISIBLE, MUJER, OCUPADO, OCUPADOS_DIVERSIDAD_GENERO, OCUPADOS_GENERO_SUPRIMIDO, ORDEN_NIVELES,
    POBLACION_POR_SEXO, POBLACION_TOTAL_CENSO, REGION_METROPOLITANA,
)
from formato import redondear, texto_peso


def clase_color(peso: float) -> int | None:
    """Tramo de color del CL publicado, con 2 decimales; usa las mismas comparaciones que la lectura. Vacío si no hay dato."""
    if pd.isna(peso):
        return None
    peso = round(float(peso), DECIMALES_CL)
    if peso <= CORTES_AZUL[2]:
        return sum(peso > c for c in CORTES_AZUL[:2])
    if peso < CORTES_ROJO[0]:
        return CLASE_NEUTRA
    return CLASE_NEUTRA + 1 + sum(peso >= c for c in CORTES_ROJO[1:])


def ocupados_con_region_y_actividad(por_sexo: pd.DataFrame) -> pd.DataFrame:
    """Base de la participación por sexo: ocupados con región de trabajo y actividad. Una sola definición para todas las vistas."""
    return por_sexo[(por_sexo["sit_fuerza_trabajo"] == OCUPADO) & por_sexo["codigo_region_trabajo"].notna() & por_sexo["actividad_ciiu"].notna()]


def resumen_nacional(g: pd.DataFrame, total_censo: int, ene_total: float) -> dict:
    """Totales del país para una actividad; total_censo incluye a quienes no tienen región de trabajo."""
    # El mayor CL se busca sin bases pequeñas, igual que en resumen_general: si no, la tabla destacaría una región que
    # el resto del mapa descarta. Si todas son pequeñas, se usan todas para no dejar la actividad sin región.
    con_lectura = g[g["lectura"] != "base_pequena"]
    if con_lectura.empty:
        con_lectura = g
    con_personas, con_peso = g.loc[g["ocupados"].idxmax()], con_lectura.loc[con_lectura["peso_relativo"].idxmax()]
    return {"ocupados": int(g["ocupados"].sum()), "censo_total": total_censo, "ene_ocupados": int(round(g["ene_ocupados"].sum())),
            "ene_pct": redondear(100 * g["ene_ocupados"].sum() / ene_total, 1), "conc": int((g["lectura"] == "concentra").sum()),
            "mas_personas": {"r": int(con_personas["codigo_region"]), "n": int(con_personas["ocupados"]), "pct": redondear(100 * con_personas["ocupados"] / g["ocupados"].sum(), 1)},
            "mas_peso": {"r": int(con_peso["codigo_region"]), "txt": texto_peso(con_peso["peso_relativo"])}}


def sexo_por_actividad(por_sexo: pd.DataFrame) -> dict:
    """Ocupados por sexo en cada actividad, con la misma base que el mapa: lugar de trabajo y actividad informados."""
    base = ocupados_con_region_y_actividad(por_sexo)
    tabla = base.pivot_table(index="actividad_ciiu", columns="sexo", values="personas", aggfunc="sum", fill_value=0)
    return {c: {"h": int(f[HOMBRE]), "m": int(f[MUJER]), "pct_h": redondear(100 * f[HOMBRE] / (f[HOMBRE] + f[MUJER]), 1), "pct_m": redondear(100 * f[MUJER] / (f[HOMBRE] + f[MUJER]), 1)} for c, f in tabla.iterrows()}


def agregar_sexo_por_region(actividades: list[dict], por_sexo: pd.DataFrame) -> dict:
    """Agrega ocupados por sexo a cada región y actividad, y devuelve las bases de la participación por sexo.

    Con menos de MINIMO_VISIBLE personas, ni la cifra ni su participación se escriben en la página, igual que en el perfil de estudios:
    la participación sola permitiría recalcular la cifra.
    """
    base = ocupados_con_region_y_actividad(por_sexo)
    por_region = base.groupby(["codigo_region_trabajo", "sexo"])["personas"].sum()
    por_celda = base.groupby(["codigo_region_trabajo", "actividad_ciiu", "sexo"])["personas"].sum()
    por_chile = base.groupby("sexo")["personas"].sum()
    for a in actividades:
        a["sexo"]["part_h"], a["sexo"]["part_m"] = redondear(100 * a["sexo"]["h"] / por_chile[HOMBRE], 2), redondear(100 * a["sexo"]["m"] / por_chile[MUJER], 2)
        for r, d in a["regiones"].items():
            for clave, sexo in (("h", HOMBRE), ("m", MUJER)):
                v = int(por_celda.get((r, a["ciiu"], sexo), 0))
                d[clave], d["pct_" + clave] = (v, redondear(100 * v / por_region[(r, sexo)], 2)) if v >= MINIMO_VISIBLE else (None, None)
    return {"chile": {"h": int(por_chile[HOMBRE]), "m": int(por_chile[MUJER])},
            "regiones": {str(int(r)): {"h": int(por_region[(r, HOMBRE)]), "m": int(por_region[(r, MUJER)])} for r in por_region.index.levels[0]}}


def sexo_por_nivel(por_sexo: pd.DataFrame) -> tuple[dict, dict]:
    """Ocupados y desocupados por nivel y sexo. La tasa siempre usa residencia, igual que la tabla regional sin abrir."""
    c = por_sexo.dropna(subset=["nivel_titulo"])
    ocupados, desocupados = c[c["sit_fuerza_trabajo"] == OCUPADO], c[c["sit_fuerza_trabajo"] == DESOCUPADO]
    residencia = ocupados.groupby(["codigo_region", "nivel_titulo", "sexo"])["personas"].sum()
    trabajo = ocupados.dropna(subset=["codigo_region_trabajo"]).groupby(["codigo_region_trabajo", "nivel_titulo", "sexo"])["personas"].sum()
    desoc = desocupados.groupby(["codigo_region", "nivel_titulo", "sexo"])["personas"].sum()
    tasa = lambda d, o: redondear(100 * d / (d + o), 1)
    regiones: dict = {}
    for r in sorted(c["codigo_region"].unique()):
        regiones[str(int(r))] = {}
        for n in c["nivel_titulo"].unique():
            dh, dm = int(desoc.get((r, n, HOMBRE), 0)), int(desoc.get((r, n, MUJER), 0))
            regiones[str(int(r))][n] = {"oh": int(trabajo.get((r, n, HOMBRE), 0)), "om": int(trabajo.get((r, n, MUJER), 0)), "dh": dh, "dm": dm,
                                        "th": tasa(dh, residencia.get((r, n, HOMBRE), 0)), "tm": tasa(dm, residencia.get((r, n, MUJER), 0))}
    res_chile, des_chile = ocupados.groupby(["nivel_titulo", "sexo"])["personas"].sum(), desocupados.groupby(["nivel_titulo", "sexo"])["personas"].sum()
    chile = {n: {"oh": int(res_chile[(n, HOMBRE)]), "om": int(res_chile[(n, MUJER)]), "dh": int(des_chile[(n, HOMBRE)]), "dm": int(des_chile[(n, MUJER)]),
                 "th": tasa(des_chile[(n, HOMBRE)], res_chile[(n, HOMBRE)]), "tm": tasa(des_chile[(n, MUJER)], res_chile[(n, MUJER)])} for n in c["nivel_titulo"].unique()}
    return regiones, chile


def agregar_nivel_por_actividad(actividades: list[dict], por_sexo: pd.DataFrame) -> dict:
    """Perfil educativo de los ocupados de cada actividad, en Chile y por región. Los desocupados no tienen actividad registrada, así que aquí no hay tasas.

    Cada nivel va como [total, %, hombres, mujeres, % hombres, % mujeres], en el orden de ORDEN_NIVELES, porque son 960 celdas dentro de la página.
    Con menos de MINIMO_VISIBLE personas, el valor del sexo no se escribe en la página.
    """
    base = ocupados_con_region_y_actividad(por_sexo)
    base = base[base["nivel_titulo"].notna()]
    base = base[base["actividad_ciiu"].isin([a["ciiu"] for a in actividades])]

    def perfil(g: pd.DataFrame) -> list:
        cuenta = g.groupby(["nivel_titulo", "sexo"])["personas"].sum()
        h = {n: int(cuenta.get((n, HOMBRE), 0)) for n in ORDEN_NIVELES}
        m = {n: int(cuenta.get((n, MUJER), 0)) for n in ORDEN_NIVELES}
        total_h, total_m = sum(h.values()), sum(m.values())
        filas = []
        for n in ORDEN_NIVELES:
            visible = lambda v, total: (v, redondear(100 * v / total, 1)) if v >= MINIMO_VISIBLE else (None, None)
            vh, ph = visible(h[n], total_h)
            vm, pm = visible(m[n], total_m)
            filas.append([h[n] + m[n], redondear(100 * (h[n] + m[n]) / (total_h + total_m), 1), vh, vm, ph, pm])
        return filas

    grupos = {c: g for c, g in base.groupby("actividad_ciiu")}
    for a in actividades:
        g = grupos[a["ciiu"]]
        a["niveles"] = perfil(g)
        for r, d in a["regiones"].items():
            d["niveles"] = perfil(g[g["codigo_region_trabajo"] == r])
    total = base.groupby("nivel_titulo")["personas"].sum()
    return {"orden": ORDEN_NIVELES, "todas": [redondear(100 * total[n] / total.sum(), 1) for n in ORDEN_NIVELES]}


def rango_ficha(f: pd.Series, columna: str, decimales: int) -> list | None:
    """[mínimo, máximo] entre instituciones; None si la carrera tiene 1 o 2 y no hay rango. Solo existe para empleabilidad."""
    lo, hi = f[f"{columna}_min"], f[f"{columna}_max"]
    return None if pd.isna(lo) else [redondear(lo, decimales), redondear(hi, decimales)]


def resumen_estudios(niveles: pd.DataFrame, sexo_chile: dict) -> dict:
    """Relación entre nivel de estudios y trabajo en Chile, según residencia y con nivel informado. Describe, no explica: la edad también influye."""
    suma = niveles.groupby("nivel_titulo")[["ocupados_residencia", "desocupados", "fuera_fuerza_trabajo"]].sum()
    total = suma["ocupados_residencia"].sum()
    con_titulo = ["Profesional", "Tecnico"]
    por_nivel = {n: {"ocupados": int(f["ocupados_residencia"]), "pct": redondear(100 * f["ocupados_residencia"] / total, 1),
                     "tasa_desocupacion": redondear(100 * f["desocupados"] / (f["ocupados_residencia"] + f["desocupados"]), 1),
                     "tasa_participacion": redondear(100 * (f["ocupados_residencia"] + f["desocupados"]) / f.sum(), 1)} for n, f in suma.iterrows()}
    # Situación educacional: población de 15 años o más con nivel y situación laboral informados, la misma base de "Estudios y trabajo".
    poblacion = niveles.assign(personas=niveles[["ocupados_residencia", "desocupados", "fuera_fuerza_trabajo"]].sum(axis=1))
    personas = poblacion.pivot_table(index="codigo_region", columns="nivel_titulo", values="personas", aggfunc="sum")[ORDEN_NIVELES]
    educacion = {str(r): [int(v) for v in f] for r, f in personas.iterrows()}
    educacion["chile"] = [int(v) for v in personas.sum()]
    # Desocupación con y sin título en cada región, para la relación entre ambas realidades.
    grupo = niveles.assign(con_titulo=niveles["nivel_titulo"].isin(con_titulo)).groupby(["codigo_region", "con_titulo"])[["ocupados_residencia", "desocupados"]].sum()
    tasa = (100 * grupo["desocupados"] / grupo.sum(axis=1)).unstack()
    desocupacion = {str(r): [redondear(f[True], 1), redondear(f[False], 1)] for r, f in tasa.iterrows()}
    sexo = {clave: redondear(100 * sum(sexo_chile[n][campo] for n in con_titulo) / sum(d[campo] for d in sexo_chile.values()), 1) for clave, campo in (("hombres", "oh"), ("mujeres", "om"))}
    return {"niveles": por_nivel, "total": int(total), "con_titulo": int(suma.loc[con_titulo, "ocupados_residencia"].sum()), "pct_con_titulo": redondear(100 * suma.loc[con_titulo, "ocupados_residencia"].sum() / total, 1),
            "sexo": sexo, "educacion": educacion, "desocupacion_titulo": desocupacion}


def situacion_poblacion(procesado: pd.DataFrame, por_sexo: pd.DataFrame) -> dict:
    """Situación laboral de las personas de 15 años o más; la región es donde viven, porque quien no trabaja no tiene región de trabajo."""
    def contar(g: pd.DataFrame) -> dict:
        total = int(g["personas"].sum())
        por_situacion = g.groupby("sit_fuerza_trabajo")["personas"].sum()
        trabajan, buscan, no_buscan = (int(por_situacion.get(c, 0)) for c in (OCUPADO, DESOCUPADO, FUERA_FUERZA_TRABAJO))
        return {"total": total, "trabajan": trabajan, "buscan": buscan, "no_buscan": no_buscan, "sin_dato": total - trabajan - buscan - no_buscan,
                "pct_trabajan": redondear(100 * trabajan / total, 1), "pct_buscan": redondear(100 * buscan / total, 1), "pct_no_buscan": redondear(100 * no_buscan / total, 1),
                "pct_sin_dato": redondear(100 * (total - trabajan - buscan - no_buscan) / total, 1),
                "tasa_desocupacion": redondear(100 * buscan / (trabajan + buscan), 1), "tasa_participacion": redondear(100 * (trabajan + buscan) / total, 1)}
    chile = contar(procesado)
    # Se suma aparte porque esta tabla agrupa por residencia, y quien trabaja en otra región cuenta donde trabaja.
    ocupados_con_lugar = procesado[(procesado["sit_fuerza_trabajo"] == OCUPADO) & procesado["codigo_region_trabajo"].notna()]
    por_lugar = ocupados_con_lugar.groupby("codigo_region_trabajo")["personas"].sum()
    chile["lugar_trabajo"] = int(por_lugar.sum())
    regiones = {str(int(r)): contar(g) | {"lugar_trabajo": int(por_lugar.get(r, 0)), "pct_lugar_trabajo": redondear(100 * por_lugar.get(r, 0) / por_lugar.sum(), 1)} for r, g in procesado.groupby("codigo_region")}
    for r, d in regiones.items():
        d["sexo"] = {nombre: contar(por_sexo[(por_sexo["codigo_region"] == int(r)) & (por_sexo["sexo"] == codigo)]) for nombre, codigo in (("hombres", HOMBRE), ("mujeres", MUJER))}
    sexo = {}
    for nombre, codigo in (("hombres", HOMBRE), ("mujeres", MUJER)):
        grupo = contar(por_sexo[por_sexo["sexo"] == codigo])
        sexo[nombre] = grupo | {"poblacion_total": POBLACION_POR_SEXO[codigo], "menores_15": POBLACION_POR_SEXO[codigo] - grupo["total"]}
    return {"poblacion_total": POBLACION_TOTAL_CENSO, "menores_15": POBLACION_TOTAL_CENSO - chile["total"], "chile": chile, "regiones": regiones, "sexo": sexo,
            "genero_ocupados": {"diversidades": OCUPADOS_DIVERSIDAD_GENERO, "suprimido": OCUPADOS_GENERO_SUPRIMIDO}}


def resumen_general(censo: pd.DataFrame, actividades: list[dict]) -> dict:
    """Panorama de todas las actividades. Una región se distingue por lo que más pesa ahí, sin contar bases pequeñas."""
    pct_por_actividad = censo.drop_duplicates("actividad_ciiu")["pct_nacional"]
    # El orden de mayor a menor se decide con el peso sin redondear, igual que el color.
    con_lectura = censo[censo["lectura"] != "base_pequena"]
    peso_maximo = con_lectura.groupby("actividad_ciiu")["peso_relativo"].max().sort_values(ascending=False)
    regiones = {}
    for r, g in con_lectura.groupby("codigo_region"):
        distintiva = g.loc[g["peso_relativo"].idxmax()]
        regiones[str(int(r))] = {"ciiu": distintiva["actividad_ciiu"], "peso": redondear(distintiva["peso_relativo"], 6), "txt": texto_peso(distintiva["peso_relativo"]),
                                 "suave": bool(round(distintiva["peso_relativo"], DECIMALES_CL) < CORTES_ROJO[1])}
    mas_empleo = censo.loc[censo.groupby("codigo_region")["ocupados"].idxmax()].set_index("codigo_region")["actividad_ciiu"]
    for r, ciiu in mas_empleo.items():
        regiones[str(int(r))]["mas_personas"] = ciiu
    mayor_empleador = mas_empleo.value_counts()
    por_actividad = {a["ciiu"]: a for a in actividades}
    no_metropolitanas = [a for a in actividades if a["nacional"]["mas_personas"]["r"] != REGION_METROPOLITANA]
    return {"total": sum(a["nacional"]["ocupados"] for a in actividades), "pct_5_mayores": redondear(pct_por_actividad.nlargest(5).sum(), 1),
            "n_metropolitana": len(actividades) - len(no_metropolitanas), "excepciones": [{"ciiu": a["ciiu"], "r": a["nacional"]["mas_personas"]["r"]} for a in no_metropolitanas],
            "mas_desiguales": [{"ciiu": c, "r": por_actividad[c]["nacional"]["mas_peso"]["r"], "txt": por_actividad[c]["nacional"]["mas_peso"]["txt"]} for c in peso_maximo.index[:2]],
            "repartidas": [a["ciiu"] for a in actividades if a["nacional"]["conc"] == 0], "corte_suave": texto_peso(CORTES_ROJO[1]).replace(",60", ",6"),
            "mayor_empleador": {"ciiu": mayor_empleador.index[0], "n": int(mayor_empleador.iloc[0])}, "colores": COLOR_RESUMEN, "regiones": regiones}


def evolucion_desocupacion(t: pd.DataFrame) -> dict:
    """Desocupación según ENE en marzo a julio de 2024 y de 2026: Chile, por nivel de título y por región."""
    def fila(f: pd.Series) -> dict:
        t24, t26 = redondear(f["tasa_2024"], 1), redondear(f["tasa_2026"], 1)
        return {"t24": t24, "t26": t26, "dif": redondear(t26 - t24, 1), "min": redondear(f["diferencia_min"], 1),
                "max": redondear(f["diferencia_max"], 1), "lect": f["lectura"]}
    chile = t[t["codigo_region"].isna()]
    return {"chile": fila(chile[chile["nivel_titulo"] == "Todos"].iloc[0]),
            "niveles": {f["nivel_titulo"]: fila(f) for _, f in chile[chile["nivel_titulo"] != "Todos"].iterrows()},
            "regiones": {str(int(f["codigo_region"])): fila(f) for _, f in t[t["codigo_region"].notna()].iterrows()}}


def formalidad(t: pd.DataFrame) -> dict:
    """Asalariado o independiente, y formal o informal, según ENE de marzo a julio de 2026.

    Chile y los niveles llevan el reparto completo; regiones y actividades solo informalidad e independientes, porque
    las cuatro casillas por separado quedan con poca muestra en las regiones chicas. Cada cifra de una actividad se
    escribe solo si es fiable: sin informalidad fiable la actividad no aparece, y sin independientes fiables va None.
    """
    reparto = lambda f: {"af": redondear(f["pct_asalariado_formal"], 1), "ai": redondear(f["pct_asalariado_informal"], 1),
                         "xf": redondear(f["pct_independiente_formal"], 1), "xi": redondear(f["pct_independiente_informal"], 1),
                         "fam": redondear(f["pct_familiar"], 1), "inf": redondear(f["tasa_informalidad"], 1), "ind": redondear(f["pct_independientes"], 1)}
    breve = lambda f: {"inf": redondear(f["tasa_informalidad"], 1), "ind": redondear(f["pct_independientes"], 1)}
    por = lambda a: t[t["ambito"] == a]
    return {"chile": reparto(por("chile").iloc[0]),
            "niveles": {f["nivel_titulo"]: reparto(f) for _, f in por("nivel").iterrows()},
            "regiones": {str(int(f["codigo_region"])): breve(f) for _, f in por("region").iterrows()},
            "actividades": {f["actividad_ciiu"]: {"inf": redondear(f["tasa_informalidad"], 1),
                                                  "ind": redondear(f["pct_independientes"], 1) if f["fiabilidad_independientes"] == "fiable" else None}
                            for _, f in por("actividad").iterrows() if f["fiabilidad_informalidad"] == "fiable"}}
