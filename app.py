import streamlit as st
import json
import os
import urllib.parse
import requests

AIRTABLE_TOKEN = "patkQeolTgZICdPkp.555b4fbda73bfaf10a9e9f41c3288703e6141d5370697cc27663dc52fc7914aa"

BASE_ID = "BASE_ID = "appkZ19FSlbQduoOp""
TABLE_NAME = "Clientes"

# Configuración de la página
st.set_page_config(page_title="Gestión Eloísa Neleb", page_icon="🛍️", layout="centered")

# Inicializar categorías en la sesión
if 'categorias' not in st.session_state:
    st.session_state.categorias = ["Vestidos", "Pantalones", "Camisas"]

# Sistema de seguridad simple
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Función para enviar datos a Airtable
def guardar_en_airtable(nombre, telefono):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [
            {
                "fields": {
                    "nombre": nombre,
                    "telefono": telefono
                }
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error de Airtable: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

# Formulario de la aplicación
st.title("Gestión de Clientes")

clave = st.text_input("Introduce la contraseña:", type="password")
if clave == "1234":  # Cambia esto por tu contraseña real
    st.session_state.autenticado = True
    st.success("Acceso concedido")

if st.session_state.autenticado:
    st.subheader("Registrar Nuevo Cliente")
    
    with st.form("nuevo_cliente", clear_on_submit=True):
        nuevo_nombre = st.text_input("Nombre de la clienta:")
        nuevo_telefono = st.text_input("Teléfono (con prefijo si es necesario):")
        boton_guardar = st.form_submit_button("Guardar en Airtable")
        
        if boton_guardar:
            if nuevo_nombre and nuevo_telefono:
                conseguido = guardar_en_airtable(nuevo_nombre, nuevo_telefono)
                if conseguido:
                    st.success(f"¡{nuevo_nombre} se ha guardado correctamente en Airtable!")
            else:
                st.warning("Por favor, rellena ambos campos.")
