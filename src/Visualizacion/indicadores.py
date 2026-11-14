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
    POBLACION_POR_SEXO, POBLACION_TOTAL_CENSO, REGION_METROPOLITANA, TRAMOS_EDAD, TRAMOS_IGUAL_EDAD,
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
    """Ocupados y desocupados por nivel y sexo, todos según residencia.

    Los desocupados no tienen lugar de trabajo, así que la tasa solo puede usar residencia. Los ocupados van en
    la misma base para que desocupados / (ocupados + desocupados) reproduzca la tasa de cada fila: con ocupados
    por lugar de trabajo, la cuenta no cerraba en 38 de 96 filas (Coquimbo técnico, hombres: 12,0% frente a 9,4%).
    """
    c = por_sexo.dropna(subset=["nivel_titulo"])
    ocupados, desocupados = c[c["sit_fuerza_trabajo"] == OCUPADO], c[c["sit_fuerza_trabajo"] == DESOCUPADO]
    residencia = ocupados.groupby(["codigo_region", "nivel_titulo", "sexo"])["personas"].sum()
    desoc = desocupados.groupby(["codigo_region", "nivel_titulo", "sexo"])["personas"].sum()
    tasa = lambda d, o: redondear(100 * d / (d + o), 1)
    regiones: dict = {}
    for r in sorted(c["codigo_region"].unique()):
        regiones[str(int(r))] = {}
        for n in c["nivel_titulo"].unique():
            dh, dm = int(desoc.get((r, n, HOMBRE), 0)), int(desoc.get((r, n, MUJER), 0))
            oh, om = int(residencia.get((r, n, HOMBRE), 0)), int(residencia.get((r, n, MUJER), 0))
            regiones[str(int(r))][n] = {"oh": oh, "om": om, "dh": dh, "dm": dm,
                                        "th": tasa(dh, oh), "tm": tasa(dm, om)}
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


def titulo_edad(t: pd.DataFrame) -> dict:
    """Desocupación con y sin título por tramo de edad (Censo 2024): muestra si la ventaja del título se mantiene a igual edad.

    chile: {tramo: [con título, sin título]}; regiones_igual_edad: regiones con menor desocupación con título en los 4
    tramos de 25 a 64; sin_edad: [región, %] con más activos sin edad en el Censo, que quedan fuera de la comparación, y el mayor % de las demás.
    """
    tasa = lambda g: {f["tramo_edad"]: f["tasa_desocupacion"] for _, f in g.iterrows()}
    chile = t[t["codigo_region"].isna()]
    con, sin = tasa(chile[chile["con_titulo"]]), tasa(chile[~chile["con_titulo"]])
    tramos = TRAMOS_EDAD
    reg = t[t["codigo_region"].notna() & t["tramo_edad"].isin(TRAMOS_IGUAL_EDAD)].pivot_table(index=["codigo_region", "tramo_edad"], columns="con_titulo", values="tasa_desocupacion")
    activos = t[t["codigo_region"].notna()].assign(a=t["ocupados"] + t["desocupados"])
    pct = 100 * activos[activos["tramo_edad"] == "Sin_edad"].groupby("codigo_region")["a"].sum() / activos.groupby("codigo_region")["a"].sum()
    activos_con = chile[chile["con_titulo"] & (chile["tramo_edad"] != "Sin_edad")].assign(a=lambda d: d["ocupados"] + d["desocupados"]).set_index("tramo_edad")["a"]
    return {"chile": {tr: [redondear(con[tr], 1), redondear(sin[tr], 1)] for tr in tramos},
            "regiones_igual_edad": int((reg[True] < reg[False]).groupby(level="codigo_region").all().sum()),
            "sin_edad": [str(int(pct.idxmax())), redondear(pct.max(), 0), redondear(pct.drop(pct.idxmax()).max(), 1)],
            # % de los activos con título que tiene de 18 a 24: dice por qué ese tramo no cambia la lectura. De 15 a 17 nadie
            # tiene título (su tasa con título es None).
            "pct_jovenes_con": redondear(100 * activos_con["18-24"] / activos_con.sum(), 0)}


def edad_poblacion(t: pd.DataFrame) -> dict:
    """% de ocupados y participación por tramo de edad, y ajustados por edad, en cada región (Censo 2024, residencia).

    Ajuste directo: las tasas de cada tramo de la región, combinadas con la mezcla de edades de Chile (los 7 tramos con
    edad conocida, de 15-17 a 65 o más). Responde qué % tendría la región con las edades de Chile, sin dejar fuera a
    nadie con edad conocida; quienes no tienen edad (Sin_edad) siguen en la cifra sin ajustar. En Chile, el ajustado es
    su propia cifra con edad conocida. puestos compara el orden de las 16 regiones sin ajustar (todas las personas,
    como el gráfico) y ajustado.
    """
    tramos = TRAMOS_EDAD
    con_edad = t[t["tramo_edad"].isin(tramos)]
    chile = con_edad[con_edad["codigo_region"].isna()].set_index("tramo_edad")
    peso = chile["poblacion"] / chile["poblacion"].sum()
    def tasas(g: pd.DataFrame) -> dict:
        g = g.set_index("tramo_edad")
        bruta = {"ocu": 100 * g["ocupados"].sum() / g["poblacion"].sum(), "par": 100 * (g["ocupados"] + g["desocupados"]).sum() / g["poblacion"].sum()}
        c = g.loc[tramos]
        aj = {"ocu": (c["pct_ocupados"] * peso).sum(), "par": (c["tasa_participacion"] * peso).sum()}
        # [% ocupados, participación, ocupados, población]: los dos totales van al pasar el mouse, para que cada % muestre su base.
        return {"tramos": {tr: [redondear(c.loc[tr, "pct_ocupados"], 1), redondear(c.loc[tr, "tasa_participacion"], 1),
                                int(c.loc[tr, "ocupados"]), int(c.loc[tr, "poblacion"])] for tr in tramos},
                "ocu": redondear(bruta["ocu"], 1), "par": redondear(bruta["par"], 1), "ocu_aj": redondear(aj["ocu"], 1), "par_aj": redondear(aj["par"], 1),
                "_exacto": {"ocu": bruta["ocu"], "par": bruta["par"], "ocu_aj": aj["ocu"], "par_aj": aj["par"]}}
    regiones = {str(int(r)): tasas(g) for r, g in t[t["codigo_region"].notna()].groupby("codigo_region")}
    ch = tasas(t[t["codigo_region"].isna()])
    # El orden se compara con las cifras exactas: con las redondeadas, dos regiones a 0,1 punto quedarían empatadas.
    exacto = pd.DataFrame({r: d.pop("_exacto") for r, d in regiones.items()}).T
    ch_ex = ch.pop("_exacto")
    puestos = {}
    for k in ("ocu", "par"):
        mov = exacto[k].rank(ascending=False) - exacto[k + "_aj"].rank(ascending=False)
        puestos[k] = {"iguales": int((mov == 0).sum()), "max": int(mov.abs().max())}
    sin_edad = t[(t["tramo_edad"] == "Sin_edad") & t["codigo_region"].isna()]["poblacion"].sum()
    return {"tramos": tramos, "chile": ch, "regiones": regiones, "puestos": puestos, "sin_edad": int(sin_edad),
            # En Chile el ajuste no cambia nada: es la cifra con edad conocida (control del método en controles.py).
            "chile_con_edad": redondear(100 * chile["ocupados"].sum() / chile["poblacion"].sum(), 1),
            "ajuste_chile_exacto": bool(abs(ch_ex["ocu_aj"] - 100 * chile["ocupados"].sum() / chile["poblacion"].sum()) < 1e-9)}


def resumen_estudios(niveles: pd.DataFrame, sexo_chile: dict) -> dict:
    """Relación entre nivel de estudios y trabajo en Chile, según residencia y con nivel informado. Describe, no explica: la edad también influye."""
    suma = niveles.groupby("nivel_titulo")[["ocupados_residencia", "desocupados", "fuera_fuerza_trabajo"]].sum()
    total = suma["ocupados_residencia"].sum()
    con_titulo = ["Profesional", "Tecnico"]
    # Desocupados y fuera de la fuerza de trabajo van como cifras para la barra 100% de cada nivel: derivarlos de las
    # tasas redondeadas en la página daría cantidades que no calzan con la fuente.
    por_nivel = {n: {"ocupados": int(f["ocupados_residencia"]), "desocupados": int(f["desocupados"]), "fuera": int(f["fuera_fuerza_trabajo"]),
                     "pct": redondear(100 * f["ocupados_residencia"] / total, 1),
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
    # Chile, para la fila de referencia del gráfico: se suma desde las personas y no se promedian las regiones.
    nacional = grupo.groupby(level="con_titulo").sum()
    tasa_chile = 100 * nacional["desocupados"] / nacional.sum(axis=1)
    sexo = {clave: redondear(100 * sum(sexo_chile[n][campo] for n in con_titulo) / sum(d[campo] for d in sexo_chile.values()), 1) for clave, campo in (("hombres", "oh"), ("mujeres", "om"))}
    return {"niveles": por_nivel, "total": int(total), "con_titulo": int(suma.loc[con_titulo, "ocupados_residencia"].sum()), "pct_con_titulo": redondear(100 * suma.loc[con_titulo, "ocupados_residencia"].sum() / total, 1),
            "sexo": sexo, "educacion": educacion, "desocupacion_titulo": desocupacion,
            "desocupacion_titulo_chile": [redondear(tasa_chile[True], 1), redondear(tasa_chile[False], 1)]}


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
    # Traslado medido, no supuesto: cada ocupado trae región de residencia y de trabajo. Quienes no informan dónde trabajan
    # van aparte, porque su peso cambia mucho entre regiones (0,6% en Antofagasta, 9,0% en la Metropolitana): suponerlo
    # igual en todas invertía el sentido del traslado en 4 regiones. Cuadre: viven − sin región − salen + llegan = lugar_trabajo.
    ocupados = procesado[procesado["sit_fuerza_trabajo"] == OCUPADO]
    sin_region = ocupados[ocupados["codigo_region_trabajo"].isna()].groupby("codigo_region")["personas"].sum()
    en_otra = ocupados_con_lugar[ocupados_con_lugar["codigo_region"] != ocupados_con_lugar["codigo_region_trabajo"]]
    salen, llegan = en_otra.groupby("codigo_region")["personas"].sum(), en_otra.groupby("codigo_region_trabajo")["personas"].sum()
    chile |= {"sin_region_trabajo": int(sin_region.sum()), "salen": int(en_otra["personas"].sum()), "llegan": int(en_otra["personas"].sum())}
    regiones = {str(int(r)): contar(g) | {"lugar_trabajo": int(por_lugar.get(r, 0)), "pct_lugar_trabajo": redondear(100 * por_lugar.get(r, 0) / por_lugar.sum(), 1),
                                          "sin_region_trabajo": int(sin_region.get(r, 0)), "salen": int(salen.get(r, 0)), "llegan": int(llegan.get(r, 0))}
                for r, g in procesado.groupby("codigo_region")}
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
            "repartidas": [a["ciiu"] for a in actividades if a["nacional"]["conc"] == 0], "corte_suave": texto_peso(CORTES_ROJO[1]).replace(",60", ",6"), "corte_sobre": texto_peso(CORTES_ROJO[0]).replace(",20", ",2"),
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

    Cada cifra va como [ocupados estimados, %], en unidades: en miles ("80" por 80 mil) la tabla se leía como 80
    personas y confundía. Son estimaciones con muestra, y el mapa lo dice junto a las cifras. Formal es el complemento de informal, para que el lector vea
    las dos partes que suman 100; su % se calcula desde el % informal ya redondeado, así la suma da 100 exacto.
    Chile y los niveles llevan el reparto completo; regiones y actividades solo formal, informal e independientes,
    porque las cuatro casillas por separado quedan con poca muestra en las regiones chicas. Familiar no remunerado
    va None donde no es fiable; en las actividades, el % de independientes también, y el informal lleva su fiabilidad.
    """
    def par(f, pct):
        return [int(redondear(f["ocupados"] * pct / 100, 0)), redondear(pct, 1)]

    def base(f):
        inf = redondear(f["tasa_informalidad"], 1)
        return {"ocup": int(redondear(f["ocupados"], 0)), "inf": par(f, f["tasa_informalidad"]),
                "for": [int(redondear(f["ocupados"] * (100 - f["tasa_informalidad"]) / 100, 0)), redondear(100 - inf, 1)],
                "ind": par(f, f["pct_independientes"]) if f["fiabilidad_independientes"] == "fiable" else None}

    def reparto(f):
        return {**base(f), "af": par(f, f["pct_asalariado_formal"]), "ai": par(f, f["pct_asalariado_informal"]),
                "xf": par(f, f["pct_independiente_formal"]), "xi": par(f, f["pct_independiente_informal"]),
                "fam": par(f, f["pct_familiar"]) if f["fiabilidad_familiar"] == "fiable" else None,
                # Informalidad dentro de cada grupo, [miles del grupo, % informal]: responde qué tan informal es ser
                # asalariado o independiente en cada nivel, que el reparto sobre el total no deja ver. El % se calcula
                # desde los % sin redondear; los ocupados son la suma de las dos casillas publicadas, para que el
                # gráfico y "Ver cifras" muestren la misma cifra.
                "asa": dentro(f, f["pct_asalariado_formal"], f["pct_asalariado_informal"]),
                "inx": dentro(f, f["pct_independiente_formal"], f["pct_independiente_informal"]),
                # Margen de error (±, 95%) de esos dos %: la tarjeta de informalidad los compara entre niveles.
                "asa_mas": mas(f["pct_informal_asalariados"], f["cv_informal_asalariados"]),
                "inx_mas": mas(f["pct_informal_independientes"], f["cv_informal_independientes"])}

    def mas(pct, cv):
        return redondear(1.96 * pct * cv / 100, 1)

    def dentro(f, formal, informal):
        return [par(f, formal)[0] + par(f, informal)[0], redondear(100 * informal / (formal + informal), 1)]
    por = lambda a: t[t["ambito"] == a]
    return {"chile": reparto(por("chile").iloc[0]),
            "niveles": {f["nivel_titulo"]: reparto(f) for _, f in por("nivel").iterrows()},
            # Con su ± y fiabilidad: el gráfico marca las regiones sobre o bajo Chile con todo su rango, y la frase agrupa las
            # que no se distinguen entre sí, porque Antofagasta y Magallanes, por ejemplo, difieren en 0,2 puntos.
            "regiones": {str(int(f["codigo_region"])): {**base(f), "mas": mas(f["tasa_informalidad"], f["cv_informalidad"]), "fiab": f["fiabilidad_informalidad"]}
                         for _, f in por("region").iterrows()},
            # Las 20 actividades del mapa (sin organismos extraterritoriales, 8 casos), con el ± y la fiabilidad del %
            # informal. Antes entraban solo las 15 con informal fiable, y quedaban fuera justo las más formales (Minería,
            # Financieras): tienen tan pocos informales que esa cifra chica no es fiable, pero su barra casi toda formal
            # sí lo es (el ± en puntos es el mismo). Se muestran todas y la cifra chica lleva su etiqueta.
            # xi: % informal dentro de los independientes de la actividad, [%, ±, fiabilidad]; la sección lo usa para mostrar
            # que ser independiente no implica ser informal (Servicios profesionales frente a Comercio).
            "actividades": {f["actividad_ciiu"]: {**base(f), "mas": mas(f["tasa_informalidad"], f["cv_informalidad"]), "fiab": f["fiabilidad_informalidad"],
                                                  "ind_mas": mas(f["pct_independientes"], f["cv_independientes"]),
                                                  "xi": [redondear(f["pct_informal_independientes"], 1), mas(f["pct_informal_independientes"], f["cv_informal_independientes"]),
                                                         f["fiabilidad_informal_independientes"]]}
                            for _, f in por("actividad").iterrows() if f["actividad_ciiu"] != "U"},
            # Informalidad dentro de asalariados e independientes por nivel y tramo de edad, [% informal, ±, fiabilidad,
            # ocupados formales, ocupados informales]: muestra que la diferencia por título se mantiene entre personas de la
            # misma edad. Formal es su complemento. Los ocupados dejan comprobar que las filas suman la fila Chile.
            "tramos": {g: {n: {f["tramo_edad"]: [redondear(f[f"pct_informal_{col}"], 1), mas(f[f"pct_informal_{col}"], f[f"cv_informal_{col}"]),
                                                f[f"fiabilidad_informal_{col}"], par(f, f[f"pct_{tipo}_formal"])[0], par(f, f[f"pct_{tipo}_informal"])[0]]
                                for _, f in t2.iterrows()}
                           for n, t2 in por("nivel_edad").groupby("nivel_titulo")}
                       for g, col, tipo in (("asa", "asalariados", "asalariado"), ("inx", "independientes", "independiente"))},
            # Fila Chile de la tabla por edad, mismo formato: asalariados e independientes de los tres niveles juntos, medidos
            # en el análisis sobre ese grupo (sin familiar ni sin nivel), para que sea la suma exacta de las filas y tenga su ±.
            "tramos_chile": {f["tramo_edad"]: [redondear(f["tasa_informalidad"], 1), mas(f["tasa_informalidad"], f["cv_informalidad"]),
                                               f["fiabilidad_informalidad"], par(f, 100 - f["tasa_informalidad"])[0], par(f, f["tasa_informalidad"])[0]]
                             for _, f in por("edad").iterrows()},
            # Lo único que queda fuera de la tabla por edad, los sin nivel informado, [formales, informales]: la nota lo suma
            # para cuadrar con Chile. Los tramos cubren todas las edades desde el 13-11-26.
            "sin_nivel": (lambda f: [par(f, 100 - f["tasa_informalidad"])[0], par(f, f["tasa_informalidad"])[0]])(por("sin_nivel").iloc[0])}
