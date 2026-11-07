"""
<src/Visualizacion/formato.py>

Cómo se escriben las cifras y los nombres en la página. Solo cambia lo que se muestra, nunca un cálculo.
"""

from __future__ import annotations

import re

import pandas as pd

from config import DECIMALES_CL

TILDES = {
    "Ingenieria": "Ingeniería", "Tecnico": "Técnico", "Tecnica": "Técnica", "Pedagogia": "Pedagogía", "Educacion": "Educación", "Administracion": "Administración",
    "Computacion": "Computación", "Informatica": "Informática", "Mecanica": "Mecánica", "Quimica": "Química", "Electronica": "Electrónica",
    "Electrica": "Eléctrica", "Electrico": "Eléctrico", "Agricola": "Agrícola", "Biotecnologia": "Biotecnología", "Geologia": "Geología", "Metalurgia": "Metalurgia",
    "Metalurgica": "Metalúrgica", "Logistica": "Logística", "Psicologia": "Psicología", "Odontologia": "Odontología", "Tecnologia": "Tecnología", "Medica": "Médica",
    "Dietetica": "Dietética", "Nutricion": "Nutrición", "Kinesiologia": "Kinesiología", "Fonoaudiologia": "Fonoaudiología", "Podologia": "Podología", "Clinico": "Clínico",
    "Radiologia": "Radiología", "Enfermeria": "Enfermería", "Automatizacion": "Automatización", "Instrumentacion": "Instrumentación", "Construccion": "Construcción",
    "Prevencion": "Prevención", "Gastronomia": "Gastronomía", "Gastronomica": "Gastronómica", "Turistica": "Turística", "Hoteleria": "Hotelería", "Produccion": "Producción",
    "Comunicacion": "Comunicación", "Diseno": "Diseño", "Grafico": "Gráfico", "Juridico": "Jurídico", "Publica": "Pública", "Fisica": "Física", "Matematicas": "Matemáticas",
    "Biologia": "Biología", "Sociologia": "Sociología", "Musica": "Música", "Geomineria": "Geominería", "Mineria": "Minería", "Topografia": "Topografía", "Telematica": "Telemática",
    "Biomedica": "Biomédica", "Tecnicas": "Técnicas", "Analisis": "Análisis", "Parvulos": "Párvulos", "Peluqueria": "Peluquería", "Estetica": "Estética", "Linguistica": "Lingüística",
    "Economia": "Economía", "Geografia": "Geografía", "Traduccion": "Traducción", "Interpretacion": "Interpretación", "Telecomunicaciones": "Telecomunicaciones",
    "Agronomia": "Agronomía", "Comun": "Común", "Electromecanica": "Electromecánica", "Recreacion": "Recreación", "Preparacion": "Preparación", "Y/O": "y/o",
    "Transito": "Tránsito", "Maritima": "Marítima", "Pesquera": "Pesquera", "Acuicola": "Acuícola", "Forestal": "Forestal", "Veterinaria": "Veterinaria", "Sanitaria": "Sanitaria",
}
MINUSCULAS = {"En", "De", "Del", "La", "Las", "Los", "Y", "E", "O", "A", "Con", "Para", "Al"}


def nombre_legible(texto: str) -> str:
    """Las carreras genéricas vienen en mayúsculas y sin tildes; esto solo afecta a lo que se muestra."""
    palabras = re.sub(r"\s+", " ", texto.title()).split(" ")
    salida = []
    for i, p in enumerate(palabras):
        limpia = p.strip(",()")
        nueva = TILDES.get(limpia, limpia)
        if i > 0 and nueva in MINUSCULAS:
            nueva = nueva.lower()
        salida.append(p.replace(limpia, nueva))
    return " ".join(salida)


def texto_peso(peso: float) -> str:
    """CL con 2 decimales: la misma cifra con la que se decide el color."""
    if pd.isna(peso):
        return "s/d"
    return f"{round(float(peso), DECIMALES_CL):.{DECIMALES_CL}f}".replace(".", ",")


def redondear(valor: float, decimales: int = 2) -> float | None:
    return None if pd.isna(valor) else round(float(valor), decimales)
