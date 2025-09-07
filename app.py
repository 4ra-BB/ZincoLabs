import streamlit as st
import pandas as pd
import joblib
import re
from datetime import datetime
from supabase import create_client

# Modelo principal

@st.cache_resource
def load_pipeline():
    return joblib.load("modelo_practico_optimizado.pkl")

modelo = load_pipeline()

# Coniguraciones
FEATURES = [
    "jobs_source_description_last_180_days",
    "jobs_last_180_days",
    "jobs_last_30_days",
    "jobs_source_description_last_30_days",
    "jobs_source_description_last_7_days",
    "jobs_last_7_days",
    "jobs_source_title_last_180_days"]

TECH_KEYWORDS = [
    ".NET", "Ability LMS", "Abstract", "Active Directory", "Adobe Illustrator",
    "Adobe InDesign", "Adobe Photoshop", "Adobe XD", "ADP", "Airflow",
    "Amazon EC2", "Amazon RDS", "Amazon S3", "Amazon Web Services", "Ansible",
    "AOS", "Apache Airflow", "Apache Hadoop", "Apache Maven", "Apache Spark",
    "Asana", "ASP.NET", "AT&T", "Attribution", "Autodesk",
    "AWS IoT", "AWS Lambda", "Azure Active Directory", "Azure Databricks", "Azure DevOps",
    "Bard AI", "BEM", "Benchmark", "Bitbucket", "Bootstrap",
    "Box", "C#", "C++", "Canva", "Carta",
    "CDI", "Centro", "Chef", "Component", "Compose",
    "Confluence", "Contenido", "CSS 3", "Cypress", "D3.js",
    "Devise", "Django", "Docker", "Elasticsearch", "eLearning LMS",
    "Entity Framework", "Envoyer", "Facebook Ads", "Figma", "Flexitime",
    "Flutter", "G Suite", "GitHub", "GitLab", "Global-e",
    "Gmail", "Golang", "Google Ads", "Google Analytics", "Google Cloud Platform",
    "Google Docs", "Google Drive", "Google Search Console", "Google Sheets",
    "Google Surveys", "Google Tag Manager", "Google Workspace", "Grafana", "GraphQL",
    "Hadoop", "Hibernate", "Hootsuite", "HTML5", "HubSpot", "Informatica",
    "iOS", "Java", "JavaScript", "Jenkins", "Jest",
    "Jira", "JOIN", "jQuery", "JSON", "Kafka",
    "Karriere", "Kotlin", "Kubernetes", "Laravel", "LearnPoint LMS",
    "LearnWorlds LMS", "Mac OS", "macOS", "Mailchimp", "MATLAB",
    "Microsoft Access", "Microsoft Active Directory", "Microsoft Azure",
    "Microsoft Dynamics 365", "Microsoft Entity Framework", "Microsoft Excel",
    "Microsoft Forefront", "Microsoft Hyper-V", "Microsoft Office 365",
    "Microsoft OneDrive", "Microsoft Outlook", "Microsoft Power Apps",
    "Microsoft Powerpoint", "Microsoft Project", "Microsoft SharePoint",
    "Microsoft SQL Server", "Microsoft Teams", "Microsoft TypeScript",
    "Microsoft Visio", "Microsoft Visual Studio", "Microsoft Windows Server",
    "Mode", "Modo", "MongoDB", "MySQL", "NetSuite", "Node.js", "OneDrive",
    "Oracle", "Passport", "Perl", "PHP", "PostgreSQL", "Postman", "Power BI",
    "PowerShell", "PreVue", "Processing", "Prometheus", "Propio", "Provide Support",
    "Python", "PyTorch", "QuickBooks", "React", "React Native", "Red Hat", "Redis",
    "Redux", "Resonate", "Ruby", "Sage", "Salesforce", "SAP", "SAS", "Sass",
    "Scala", "Selenium", "SEMrush", "Serverless", "ServiceNow.com", "Shopify",
    "Sketch", "SketchUp", "Slack", "Snowflake", "Solidworks", "SPM",
    "Spring", "Spring Boot", "sso", "Streamline", "Swift", "Synth", "Tableau",
    "TensorFlow", "Terraform", "Tower", "Trello", "TypeScript", "Unity", "Venda",
    "Visual Studio", "Vue.js", "Webpack", "WhatsApp", "Windows", "Windows 10",
    "Windows Server", "WordPress", "Workday", "Workspace", "Xero", "XML", "Zoom"]  

# Otras funciones
def parse_days(fecha_str: str) -> int:
    m = re.search(r"(\d+)", fecha_str)
    return int(m.group(1)) if m else 0

def detecta_tecnologia(texto: str) -> bool:
    """Detecta si alguna keyword aparece en el texto (case-insensitive)."""
    return any(kw.lower() in texto.lower() for kw in TECH_KEYWORDS)

# Esquema Streamlit

st.title("🔎 Scoring de Leads para ZincoLabs a partir de ofertas laborales")

st.markdown(
    "#### Cómo funciona esta herramienta\n"
    "Pega las ofertas de trabajo del lead que quieres revisar y completa los datos, "
    "manteniendo el contenido en su idioma original. "
    "La herramienta analizará cada oferta y te ayudará a predecir si es una empresa "
    "que tiende a contratar nuevas tecnologías.")

empresa = st.text_input("Nombre de la empresa:")

# Guardar ofertas
if "offers" not in st.session_state:
    st.session_state.offers = [ {"titulo": "", "dias": "", "descripcion": ""} ]

# Render dinámico de ofertas
for i, oferta in enumerate(st.session_state.offers):
    st.markdown(f"### Oferta {i+1}")
    cols = st.columns(3)
    oferta["titulo"] = cols[0].text_input("Título", value=oferta["titulo"], key=f"titulo_{i}")
    oferta["dias"] = cols[1].text_input("Hace cuántos días", value=oferta["dias"], key=f"dias_{i}")
    oferta["descripcion"] = cols[2].text_area("Descripción", value=oferta["descripcion"], key=f"desc_{i}")

# Botón para añadir otra oferta
if st.button("➕ Añadir otra oferta"):
    st.session_state.offers.append({"titulo": "", "dias": "", "descripcion": ""})

#Iniciar Supabase para almacenar datos
SUPABASE_URL="https://qhhtmmrqrykcmoxzhqhj.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFoaHRtbXJxcnlrY21veHpocWhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY3ODcyNTcsImV4cCI6MjA3MjM2MzI1N30.I7B1QTn_4MbQVyI87wIJgEoJ6CBvCAxHVN4p_R2CKTA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Procesamiento y predicción
if st.button("Analizar"):
    if not empresa or not st.session_state.offers:
        st.error("⚠️ Debes ingresar la empresa y al menos una oferta.")
    else:
        jobs_7, jobs_30, jobs_180 = 0, 0, 0
        desc_7, desc_30, desc_180 = 0, 0, 0
        title_180 = 0

        for oferta in st.session_state.offers:
            dias = parse_days(oferta["dias"])
            if dias == 0:
                continue

            # Contar ofertas por rango temporal
            if dias <= 7: jobs_7 += 1
            if dias <= 30: jobs_30 += 1
            if dias <= 180: jobs_180 += 1

            # Detectar tecnología en título
            if detecta_tecnologia(oferta["titulo"]) and dias <= 180:
                title_180 += 1

            # Detectar tecnología en descripción
            if detecta_tecnologia(oferta["descripcion"]):
                if dias <= 7: desc_7 += 1
                if dias <= 30: desc_30 += 1
                if dias <= 180: desc_180 += 1

        # Construcción del DataFrame de features
        input_data = pd.DataFrame([{
            "jobs_source_description_last_180_days": desc_180,
            "jobs_last_180_days": jobs_180,
            "jobs_last_30_days": jobs_30,
            "jobs_source_description_last_30_days": desc_30,
            "jobs_source_description_last_7_days": desc_7,
            "jobs_last_7_days": jobs_7,
            "jobs_source_title_last_180_days": title_180}])

        st.subheader("📊 Features construidas")
        st.dataframe(input_data)

        # Predicción
        try:
            pred_proba = modelo.predict_proba(input_data)[:, 1][0]
            pred_label = int(pred_proba >= 0.3)

            # Guardar en Supabase
            registro = input_data.to_dict(orient="records")[0]
            registro["empresa"] = empresa
            registro["probabilidad_cliente"] = float(pred_proba)
            registro["es_cliente"] = bool(pred_label)
            supabase.table("ofertas").insert(registro).execute()

            st.subheader("🔮 Predicción")
            st.write(f"Probabilidad: {pred_proba:.2f}")
            if pred_label == 1:
                st.success("✅ Parece ser que encontraste un pez gordo! A por él")
            else:
                st.error("❌ No parece ser lo que buscamos, vamos a intentar con otro.")
        except Exception as e:
            st.error(f"Error en la predicción: {e}")
