import argparse
import os
import pandas as pd


def convertir_todas_hojas_a_md():
    # 1. Configurar el lector de argumentos de la terminal
    parser = argparse.ArgumentParser(
        description="Convierte TODAS las hojas de un archivo Excel (.xlsx) a un único archivo Markdown (.md)."
    )
    parser.add_argument(
        "archivo_excel", help="Ruta del archivo .xlsx que deseas convertir"
    )
    args = parser.parse_args()

    # 2. Validar archivo
    if not os.path.exists(args.archivo_excel):
        print(f"❌ Error: El archivo '{args.archivo_excel}' no existe.")
        return

    if not args.archivo_excel.lower().endswith(".xlsx"):
        print("❌ Error: El archivo debe tener una extensión .xlsx.")
        return

    try:
        # 3. Leer TODAS las hojas (sheet_name=None devuelve un diccionario)
        print("📖 Leyendo el archivo Excel...")
        hojas_excel = pd.read_excel(args.archivo_excel, sheet_name=None)

        # 4. Configurar archivo de salida
        nombre_base, _ = os.path.splitext(args.archivo_excel)
        archivo_markdown = f"{nombre_base}.md"

        with open(archivo_markdown, "w", encoding="utf-8") as f:
            # Título principal del documento basado en el nombre del archivo
            titulo_principal = (
                os.path.basename(nombre_base).replace("_", " ").title()
            )
            f.write(f"# {titulo_principal}\n\n")

            # 5. Iterar sobre cada hoja del documento
            for nombre_hoja, df in hojas_excel.items():
                print(f"⏳ Procesando pestaña: {nombre_hoja}...")

                # Escribir el nombre de la hoja como un subtítulo
                f.write(f"## {nombre_hoja}\n\n")

                # Si la hoja está vacía, saltarla o poner un aviso
                if df.empty:
                    f.write("*Esta pestaña no contiene datos.*\n\n")
                    continue

                # Limpieza de datos por hoja
                df = df.fillna("")
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

                # Convertir a tabla Markdown
                contenido_tabla = df.to_markdown(index=False)

                # Escribir la tabla y añadir espacio para la siguiente sección
                f.write(contenido_tabla)
                f.write("\n\n---\n\n")  # Línea divisoria entre pestañas

        print(f"✨ ¡Conversión exitosa de todas las pestañas!")
        print(f"📂 Archivo unificado generado en: {archivo_markdown}")

    except Exception as e:
        print(f"❌ Ocurrió un error durante la conversión: {e}")


if __name__ == "__main__":
    convertir_todas_hojas_a_md()
