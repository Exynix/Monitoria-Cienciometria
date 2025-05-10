# ---------------------- Importación de librerias ----------------------
import pandas as pd
import re
import knime.scripting.io as knio # Assuming this is for your KNIME environment
import traceback # Kept for robust error handling
import html # To decode HTML entities like &nbsp;

# ---------------------- Definición de palabras clave de salud ----------------------
TERMINOS_SALUD = [
    # Términos en español
    "salud", "médic", "medic", "clínic", "clinic", "sanitar", "hospital",
    "enferm", "pacient", "diagnós", "diagnos", "tratamiento", "terapia", "terapéutic",
    "oncolog", "cáncer", "cancer", "cardio", "neuro", "psiquiatr", "psicolog",
    "ortoped", "traumatolog", "pediatr", "geriátr", "geriatr", "ginecolog",
    "obstetric", "dermatolog", "oftalmolog", "otorrin", "endocrin", "hematolog",
    "inmunolog", "anestesi", "cirugía", "cirugia", "quirúrg", "quirurg",
    "cardiovascular", "respirator", "pulmon", "pulmón", "cerebr", "neurolog",
    "digestiv", "gastrointestin", "renal", "riñón", "rinon", "hepátic", "hepatic",
    "musculoesquelét", "musculoesquelet", "dérmico", "dermic", "piel", "ocular",
    "auditiv", "óseo", "oseo", "hueso", "articul", "sangre", "sanguíneo", "sanguineo",
    "diabetes", "hipertens", "artritis", "esclerosis", "alzheimer", "parkinson",
    "demencia", "epilepsia", "asma", "alergia", "infeccion", "infección", "viral",
    "bacteria", "covid", "virus", "sindrome", "síndrome", "tumor", "lesion", "lesión",
    "fractura", "transplante", "trasplante", "metástasis", "metastasis",
    "epidemiolog", "pandemia", "prevención", "prevencion", "vacuna", "inmuniza",
    "salubridad", "higiene", "sanitari", "nutrición", "nutricion", "dietétic", "dietetic",
    "biomédic", "biomedic", "farmacolog", "farmacéutic", "farmaceutic", "genétic",
    "genetic", "genómic", "genomic", "proteómic", "proteomic", "radiolog", "imagenolog",
    "tomografía", "tomografia", "resonancia", "ultrasonido", "ecografía", "ecografia",
    "quimioterapia", "radioterapia", "rehabilitac", "fisioterapia", "inmunoterapia",
    "farmacoterap", "psicoterap", "quirúrgic", "quirurgic", "prótesis", "protesis",
    "implante", "prescripción", "prescripcion", "medicament", "fármaco", "farmaco",
    "calidad de vida", "bienestar", "cuidado paliativo", "hospicio", "soporte vital",
    "cronico", "crónico", "terminal", "supervivencia", "sobrevida", "mortalidad",
    "morbilidad", "discapacid", "capacidad funcional", "autonomía", "autonomia",
    "ensayo clínico", "ensayo clinico", "estudio cohorte", "grupo control",
    "placebo", "doble ciego", "eficacia", "inocuidad", "seguridad", "adverso",

    # English health-related terms
    "health", "medical", "clinical", "sanitary", "healthcare", "hospital",
    "disease", "illness", "patient", "diagnos", "treatment", "therapy", "therapeutic",
    "oncology", "cancer", "cardio", "neuro", "psychiatr", "psycholog",
    "orthoped", "traumatology", "pediatric", "geriatric", "gynecolog",
    "obstetric", "dermatolog", "ophthalmolog", "otolaryngolog", "endocrinolog", "hematolog",
    "immunolog", "anesthes", "surgery", "surgical", "cardiovascular", "respiratory",
    "lung", "cerebr", "neurolog", "digestive", "gastrointest", "renal", "kidney",
    "hepatic", "liver", "musculoskeletal", "dermic", "skin", "ocular", "eye",
    "auditory", "ear", "bone", "joint", "blood", "diabetes", "hypertens", "arthritis",
    "sclerosis", "alzheimer", "parkinson", "dementia", "epilepsy", "asthma", "allergy",
    "infection", "viral", "bacteria", "covid", "virus", "syndrome", "tumor", "lesion",
    "fracture", "transplant", "metastasis", "epidemiolog", "pandemic", "prevention",
    "vaccine", "immunization", "hygiene", "nutrition", "diet", "biomedical", "pharmacolog",
    "pharmaceutical", "genetic", "genomic", "proteomic", "radiology", "imaging",
    "tomography", "resonance", "ultrasound", "sonography", "chemotherapy", "radiotherapy",
    "rehabilitation", "physiotherapy", "immunotherapy", "pharmacotherapy", "psychotherapy",
    "prosthesis", "implant", "prescription", "medication", "drug", "quality of life",
    "wellbeing", "palliative care", "hospice", "life support", "chronic", "terminal",
    "survival", "mortality", "morbidity", "disability", "functional capacity", "autonomy",
    "clinical trial", "cohort study", "control group", "placebo", "double blind",
    "efficacy", "safety", "adverse effect", "wellness", "telemedicine", "telehealth",

    # Medical specialties in English that might not be covered above
    "urology", "nephrology", "rheumatology", "pulmonology", "gastroenterology",
    "neonatology", "intensive care", "emergency", "pathology", "microbiology",
    "virology", "parasitology", "anatomy", "physiology", "histology", "cytology",
    "biochemistry", "biophysics", "epidemiology", "public health", "community health",

    # Medical technology and procedures in English
    "mri", "ct scan", "pet scan", "x-ray", "xray", "ultrasound", "ecg", "ekg", "eeg",
    "biopsy", "catheter", "stent", "pacemaker", "defibrillator", "ventilator",
    "dialysis", "endoscopy", "laparoscopy", "robotic surgery", "laser surgery",
    "cryotherapy", "stem cell", "gene therapy", "immunotherapy", "nanotechnology"
]

# ---------------------- Función para limpiar el nombre del proyecto ----------------------
def limpiar_nombre_proyecto(nombre_original: str) -> str:
    """
    Limpia el nombre del proyecto eliminando HTML, prefijos numéricos y fechas/pies de página.
    """
    if not isinstance(nombre_original, str):
        return ""

    # 0. Decodificar entidades HTML (como &nbsp;, &amp;, etc.)
    text = html.unescape(nombre_original)

    # 1. Manejar <br> como principal separador para la fecha/footer.
    # Reemplazamos <br> (y sus variantes con espacios) con un delimitador único.
    # Esto ayuda a aislar la parte del nombre antes de la fecha.
    text_sin_br = re.sub(r"\s*<br\s*/?>\s*", " ||BR_SEPARATOR|| ", text, flags=re.IGNORECASE)

    # Tomar solo la parte antes del primer "||BR_SEPARATOR||" si existe
    if "||BR_SEPARATOR||" in text_sin_br:
        main_part = text_sin_br.split("||BR_SEPARATOR||", 1)[0]
    else:
        main_part = text_sin_br

    # 2. Eliminar todas las demás etiquetas HTML de la parte principal.
    text_sin_html_tags = re.sub(r"<[^>]+>", " ", main_part)

    # 3. Eliminar prefijos como "1.- ", "2. ", "Investigación y desarrollo:", etc.
    # Primero, el prefijo de tipo de proyecto más específico:
    nombre_intermedio = re.sub(r"^(Investigación y desarrollo|Research and development)\s*:\s*", "", text_sin_html_tags, flags=re.IGNORECASE).strip()
    # Luego, el prefijo numérico:
    nombre_limpio = re.sub(r"^\s*\d+\s*[\.-]?\s*", "", nombre_intermedio).strip()

    # 4. (Opcional pero recomendado) Si después de quitar <br>, fechas aún pueden estar pegadas sin un <br> previo:
    # Este es un intento más agresivo de quitar fechas al final del string si no fueron separadas por <br>.
    # Formatos de fecha: YYYY/M, YYYY/MM, YYYY-MM, YYYY-MM-DD, MM/DD/YYYY
    # Seguido por " - Algo" o simplemente al final de la cadena.
    # El (?:...) es un grupo de no captura. \s* maneja espacios. .*? es no codicioso.
    date_footer_pattern = r"\s+(?:\d{4}/\d{1,2}|\d{4}-\d{1,2}(?:-\d{1,2})?|\d{1,2}/\d{1,2}/\d{4})\s*(?:-\s*.*)?$"

    # Intentar eliminar este patrón si está al final del nombre_limpio
    # Hacemos esto después de la limpieza de HTML y prefijos para tener un string más limpio
    match_date_at_end = re.search(date_footer_pattern, nombre_limpio)
    if match_date_at_end:
        nombre_limpio = nombre_limpio[:match_date_at_end.start()]

    # 5. Normalizar todos los caracteres de espacio (incluyendo \xa0, tabs, etc.) a un solo espacio ASCII.
    # Y eliminar cualquier espacio extra al principio o al final.
    nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio).strip()

    return nombre_limpio

# ---------------------- Función de filtrado y recolección de términos ----------------------
def es_proyecto_salud(nombre_proyecto_original: str, tipo_proyecto_original: str = None) -> tuple[bool, list[str]]:
    """
    Determina si un proyecto está relacionado con la salud y devuelve los términos coincidentes.
    El nombre del proyecto se limpia antes de la búsqueda.
    """
    matched_terms = []

    nombre_limpio = limpiar_nombre_proyecto(nombre_proyecto_original)

    if not nombre_limpio: # Si después de limpiar, el nombre está vacío
        return False, matched_terms

    texto_a_buscar = nombre_limpio.lower()

    if tipo_proyecto_original is not None and isinstance(tipo_proyecto_original, str) and tipo_proyecto_original.strip() != "":
        # Limpiar también el tipo_proyecto
        tipo_limpio = re.sub(r'<[^>]+>', ' ', html.unescape(tipo_proyecto_original)) # Quitar HTML
        tipo_limpio = re.sub(r'\s+', ' ', tipo_limpio).strip().lower() # Normalizar espacios
        if tipo_limpio: # Añadir solo si no está vacío después de limpiar
            texto_a_buscar += " " + tipo_limpio


    for termino in TERMINOS_SALUD:
        # Usar \b para asegurar que 'termino' es una palabra completa o el inicio de una palabra.
        # re.escape(termino) es importante si los términos pudieran tener caracteres especiales de regex.
        if re.search(r'\b' + re.escape(termino), texto_a_buscar, re.IGNORECASE):
            matched_terms.append(termino)

    if matched_terms:
        return True, list(set(matched_terms)) # Devolver términos únicos
    else:
        return False, matched_terms

# ---------------------- Procesamiento principal ----------------------
try:
    proyectos_df = knio.input_tables[0].to_pandas()

    print(f"DataFrame de entrada: {proyectos_df.shape[0]} filas, {proyectos_df.shape[1]} columnas.")
    # print(f"Columnas: {proyectos_df.columns.tolist()}")

    col_nombre_proyecto = 'Nombre Producto'
    col_tipo_proyecto = 'Tipo Proyecto'

    if col_nombre_proyecto not in proyectos_df.columns:
        raise ValueError(f"Columna '{col_nombre_proyecto}' no encontrada. Verifique el nombre.")
    if col_tipo_proyecto not in proyectos_df.columns:
        print(f"INFO: Columna '{col_tipo_proyecto}' no encontrada. Se procederá sin ella.")
        proyectos_df[col_tipo_proyecto] = None # Añadir columna vacía para que .get no falle y la lógica sea uniforme

    if proyectos_df.empty:
        output_columns = proyectos_df.columns.tolist()
        if 'terminos_coincidentes' not in output_columns:
            output_columns.append('terminos_coincidentes')
        if 'nombre_proyecto_limpio' not in output_columns:
            output_columns.append('nombre_proyecto_limpio')
        proyectos_salud_df = pd.DataFrame(columns=output_columns)
        print("DataFrame de entrada vacío. Saliendo con tabla vacía.")
    else:
        # Crear columna de nombre limpio para depuración y posible uso futuro
        proyectos_df['nombre_proyecto_limpio'] = proyectos_df[col_nombre_proyecto].apply(limpiar_nombre_proyecto)

        print("\nEjemplos de limpieza de nombres (primeras 5 filas):")
        for i in range(min(5, proyectos_df.shape[0])):
            nombre_original_ej = str(proyectos_df.iloc[i].get(col_nombre_proyecto, "")) # Convertir a str para seguridad
            nombre_limpio_ej = proyectos_df['nombre_proyecto_limpio'].iloc[i]
            tipo_proyecto_ej = str(proyectos_df.iloc[i].get(col_tipo_proyecto, ""))
            print(f"Original: {nombre_original_ej[:150]}...")
            print(f"Limpio  : {nombre_limpio_ej[:150]}...")
            if tipo_proyecto_ej and tipo_proyecto_ej != "None":
                print(f"Tipo Proy: {tipo_proyecto_ej[:50]}...")
            print("---")

        health_info_results = proyectos_df.apply(
            lambda row: es_proyecto_salud(
                row.get(col_nombre_proyecto),
                row.get(col_tipo_proyecto)
            ),
            axis=1
        )

        proyectos_df['terminos_coincidentes'] = health_info_results.apply(lambda x: "|".join(x[1]))
        is_health_filter = health_info_results.apply(lambda x: x[0])
        proyectos_salud_df = proyectos_df[is_health_filter].copy()

    print(f"Proyectos relacionados con salud encontrados: {len(proyectos_salud_df)}")
    if not proyectos_salud_df.empty:
        print("Ejemplo de las primeras filas filtradas:")
        cols_to_show = [col_nombre_proyecto, 'nombre_proyecto_limpio']
        if col_tipo_proyecto in proyectos_salud_df.columns:
            cols_to_show.append(col_tipo_proyecto)
        cols_to_show.append('terminos_coincidentes')
        # Filtrar cols_to_show para que solo contenga columnas que realmente existen en proyectos_salud_df
        cols_to_show = [col for col in cols_to_show if col in proyectos_salud_df.columns]
        print(proyectos_salud_df[cols_to_show].head(3))

    # Decide si quieres incluir 'nombre_proyecto_limpio' en la salida final
    # Si no, puedes hacer: proyectos_salud_df = proyectos_salud_df.drop(columns=['nombre_proyecto_limpio'])
    knio.output_tables[0] = knio.Table.from_pandas(proyectos_salud_df)

except Exception as e:
    print("ERROR GRAVE DURANTE EL PROCESAMIENTO:")
    print(str(e))
    print("Traceback detallado:")
    print(traceback.format_exc())

    df_columns = ['Nombre Producto', 'Tipo Proyecto', 'terminos_coincidentes', 'nombre_proyecto_limpio'] # Columnas base
    if 'proyectos_df' in locals() and isinstance(proyectos_df, pd.DataFrame) and not proyectos_df.empty:
        # Intentar obtener columnas del df original si existe
        df_columns = proyectos_df.columns.tolist()
        if 'terminos_coincidentes' not in df_columns: df_columns.append('terminos_coincidentes')
        if 'nombre_proyecto_limpio' not in df_columns: df_columns.append('nombre_proyecto_limpio')

    empty_df = pd.DataFrame(columns=df_columns)
    knio.output_tables[0] = knio.Table.from_pandas(empty_df)