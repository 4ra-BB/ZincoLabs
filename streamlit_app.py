import streamlit as st
import requests


API_URL = "https://4460a7829fa1.ngrok-free.app"

st.title("🔮 Clasificador de Leads")
st.write("Completa los campos para predecir si es un buen lead o no.")


with st.form("lead_form"):
    jobs_source_description_last_180_days = st.number_input("Tecnologías mencionadas en ofertas laborales de los últimos 180 días", min_value=0, step=1)
    jobs_last_180_days = st.number_input("Cantidad de ofertas laborales que mencionan una tecnología en los últimos 180 días", min_value=0, step=1)
    jobs_last_30_days = st.number_input("Cantidad de ofertas laborales que mencionan una tecnología en los últimos 30 días", min_value=0, step=1)
    jobs_source_description_last_30_days = st.number_input("Tecnologías mencionadas en ofertas laborales de los últimos 30 días", min_value=0, step=1)
    jobs_source_description_last_7_days = st.number_input("Tecnologías mencionadas en ofertas laborales de los últimos 7 días", min_value=0, step=1)
    jobs_last_7_days = st.number_input("Cantidad de ofertas laborales que mencionan una tecnología en los últimos 7 días", min_value=0, step=1)
    jobs_source_title_last_180_days = st.number_input("Cantidad de ofertas laborales que mencionan una tecnología en su título en los últimos 180 días", min_value=0, step=1)
    is_recruiting_agency = st.checkbox("¿Es agencia de reclutamiento?")

    submitted = st.form_submit_button("Predecir")

# Llamar a la API

if submitted:
    data = {
        "jobs_source_description_last_180_days": jobs_source_description_last_180_days,
        "jobs_last_180_days": jobs_last_180_days,
        "jobs_last_30_days": jobs_last_30_days,
        "jobs_source_description_last_30_days": jobs_source_description_last_30_days,
        "jobs_source_description_last_7_days": jobs_source_description_last_7_days,
        "jobs_last_7_days": jobs_last_7_days,
        "jobs_source_title_last_180_days": jobs_source_title_last_180_days,
        "is_recruiting_agency": is_recruiting_agency
    }

    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            result = response.json().get("prediction", None)
            if result == 1:
                st.success("✅ ¡A por él!")
            else:
                st.error("❌ Este cliente no parece ser lo que buscamos")
        else:
            st.error(f"⚠️ Error en la API: {response.status_code}")
    except Exception as e:
        st.error(f"❌ No se pudo conectar a la API: {e}")
