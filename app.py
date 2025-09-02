import streamlit as st
import pandas as pd
import joblib
import re
from datetime import datetime
from transformers import pipeline
from supabase import create_client
import os
from dotenv import load_dotenv

# Cargar variables de entorno
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🚀 Clasificación de Leads desde Ofertas Laborales")
st.write("Archivo modelo existe:", os.path.exists("modelo_practico_optimizado.pkl")
         
# Cargar modelo y classifier con caching para mejorar performance
@st.cache_resource
def load_model():
    return joblib.load("modelo_practico_optimizado.pkl")

@st.cache_resource
def load_classifier():
    return pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

modelo = load_model()
classifier = load_classifier()

labels = ["menciona herramientas tecnológicas", "no menciona herramientas tecnológicas"]
hypothesis_template = "Este texto {}."

# Lista de tecnologías
TECH_KEYWORDS = [".NET", "Ability LMS", "Abstract", "Active Directory", "Adobe Illustrator", "Adobe InDesign", "Adobe Photoshop", "Adobe XD", "ADP", "Airflow", "Amazon EC2", "Amazon RDS", "Amazon S3", 
                 "Amazon Web Services", "Ansible", "AOS", "Apache Airflow", "Apache Hadoop", "Apache Maven", "Apache Spark", "Asana", "ASP.NET", "AT&T", "Attribution", "Autodesk", "AWS IoT", "AWS Lambda", 
                 "Azure Active Directory", "Azure Databricks", "Azure DevOps", "Bard AI", "BEM", "Benchmark", "Bitbucket", "Bootstrap", "Box", "C#", "C++", "Canva", "Carta", "CDI", "Centro", "Chef", "Component",
                 "Compose", "Confluence", "Contenido", "CSS 3", "Cypress", "D3.js", "Devise", "Django", "Docker", "Elasticsearch", "eLearning LMS", "Entity Framework", "Envoyer", "Facebook Ads", "Figma", "Flexitime", 
                 "Flutter", "G Suite", "GitHub", "GitLab", "Global-e", "Gmail", "Golang", "Google Ads", "Google Analytics", "Google Cloud Platform", "Google Docs", "Google Drive", "Google Search Console", "Google Sheets",
                 "Google Surveys", "Google Tag Manager", "Google Workspace", "Grafana", "GraphQL", "Hadoop", "Hibernate", "Hootsuite", "HTML5", "HubSpot", "Informatica", "iOS", "Java", "JavaScript", "Jenkins", "Jest", 
                 "Jira", "JOIN", "jQuery", "JSON", "Kafka", "Karriere", "Kotlin", "Kubernetes", "Laravel", "LearnPoint LMS", "LearnWorlds LMS", "Mac OS", "macOS", "Mailchimp", "MATLAB", "Microsoft Access", 
                 "Microsoft Active Directory", "Microsoft Azure", "Microsoft Dynamics 365", "Microsoft Entity Framework", "Microsoft Excel", "Microsoft Forefront", "Microsoft Hyper-V", "Microsoft Office 365",
                 "Microsoft OneDrive", "Microsoft Outlook", "Microsoft Power Apps", "Microsoft Powerpoint", "Microsoft Project", "Microsoft SharePoint", "Microsoft SQL Server", "Microsoft Teams", "Microsoft TypeScript",
                 "Microsoft Visio", "Microsoft Visual Studio", "Microsoft Windows Server", "Mode", "Modo", "MongoDB", "MySQL", "NetSuite", "Node.js", "OneDrive", "Oracle", "Passport", "Perl", "PHP", "PostgreSQL", 
                 "Postman", "Power BI", "PowerShell", "PreVue", "Processing", "Prometheus", "Propio", "Provide Support", "Python", "PyTorch", "QuickBooks", "React", "React Native", "Red Hat", "Redis", "Redux",
                 "Resonate", "Ruby", "Sage", "Salesforce", "SAP", "SAS", "Sass", "Scala", "Selenium", "SEMrush", "Serverless", "ServiceNow.com", "Shopify", "Sketch", "SketchUp", "Slack", "Snowflake", "Solidworks", "SPM",
                 "Spring", "Spring Boot", "sso", "Streamline", "Swift", "Synth", "Tableau", "TensorFlow", "Terraform", "Tower", "Trello", "TypeScript", "Unity", "Venda", "Visual Studio", "Vue.js", "Webpack", "WhatsApp",
                 "Windows", "Windows 10", "Windows Server", "WordPress", "Workday", "Workspace", "Xero", "XML", "Zoom"]

# Funciones auxiliares
def parse_days(fecha_str: str) -> int:
    """Convierte texto tipo 'hace 7 días' en int días."""
    m = re.search(r"(\d+)", fecha_str)
    return int(m.group(1)) if m else 0

def detecta_tecnologia(texto: str) -> bool:
    """Detecta si un texto menciona tecnología usando zero-shot + keywords."""
    if any(kw.lower() in texto.lower() for kw in TECH_KEYWORDS):
        return True
    result = classifier(texto, candidate_labels=labels, hypothesis_template=hypothesis_template)
    return result["labels"][0] == "menciona herramientas tecnológicas"

def calcular_flags(dias: int):
    return dias < 7, dias < 30, dias < 180

# Interfaz Streamlit
texto = st.text_area(
    "Pega aquí las ofertas laborales (bloques separados por doble salto de línea). "
    "Cada bloque debe tener:\n1ª línea: título\n2ª línea: fecha (ej: 'hace 7 días')\nResto: cuerpo")

if st.button("Analizar") and texto.strip():
    ofertas = texto.split("\n\n")
    resultados = []

    for oferta in ofertas:
        partes = oferta.strip().split("\n")
        if len(partes) < 2:
            continue

        titulo = partes[0]
        fecha_str = partes[1]
        cuerpo = " ".join(partes[2:]) if len(partes) > 2 else ""

        dias = parse_days(fecha_str)
        menor7, menor30, menor180 = calcular_flags(dias)

        menciona_cuerpo = detecta_tecnologia(cuerpo)
        menciona_titulo = detecta_tecnologia(titulo)

        # Insertar en Supabase con manejo de errores
        try:
            supabase.table("ofertas").insert({
                "titulo": titulo,
                "dias_desde_publicacion": dias,
                "menciona_tecnologia": menciona_cuerpo,
                "menciona_tecnologia_titulo": menciona_titulo,
                "dias_menor_7": menor7,
                "dias_menor_30": menor30,
                "dias_menor_180": menor180
            }).execute()
        except Exception as e:
            st.warning(f"⚠️ No se pudo insertar en Supabase: {e}")

        # Features para modelo
        features = {
            "jobs_source_description_last_180_days": int(menciona_cuerpo and menor180),
            "jobs_last_180_days": int(menor180),
            "jobs_last_30_days": int(menor30),
            "jobs_source_description_last_30_days": int(menciona_cuerpo and menor30),
            "jobs_source_description_last_7_days": int(menciona_cuerpo and menor7),
            "jobs_last_7_days": int(menor7),
            "jobs_source_title_last_180_days": int(menciona_titulo and menor180)}

        X = pd.DataFrame([features])
        prob = modelo.predict_proba(X)[0, 1]

        resultados.append([
            titulo, dias, menciona_cuerpo, menciona_titulo, menor7, menor30, menor180, round(prob, 3)])

    df = pd.DataFrame(resultados, columns=[
        "Título", "Días", "Menciona Cuerpo", "Menciona Título",
        "<7 días", "<30 días", "<180 días", "Probabilidad Cliente"])

    st.subheader("Resultados")
    st.dataframe(df)
    st.subheader("Resultados")
    st.dataframe(df)
