import streamlit as st
import json
import os
import urllib.parse
import requests
from datetime import datetime

# Cambia las comillas de abajo por tu Token real que empieza por pat...
AIRTABLE_TOKEN = "Pega_aquí_tu_token_de_Airtable"
BASE_ID = "appkZ19FSlbQduoOp"
TABLE_NAME = "Clientes"

# Configuración de la página
st.set_page_config(page_title="Gestión Eloísa Neleb", page_icon="🛍️", layout="centered")

# Inicializar categorías en la sesión
if 'categorias' not in st.session_state:
    st.session_state.categorias = ["Vestidos", "Pantalones", "Camisas", "Blusas", "Faldas"]

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
st.title("🛍️ Gestión Eloísa Neleb Modas")

clave = st.text_input("Introduce la contraseña:", type="password")
if clave == "1234":  # Tu contraseña de acceso
    st.session_state.autenticado = True

if st.session_state.autenticado:
    st.success("Acceso concedido")
    
    # Crear pestañas para organizar la app y que no sea un lío
    pestana_ventas, pestana_clientes = st.tabs(["💰 Crear Venta", "👤 Registrar Clienta"])
    
    # --- PESTAÑA 1: CREAR VENTA ---
    with pestana_ventas:
        st.subheader("Nueva Venta / Ticket de WhatsApp")
        
        prenda = st.selectbox("Selecciona el tipo de prenda:", st.session_state.categorias)
        precio = st.number_input("Precio de la prenda (€):", min_value=0.0, step=0.5)
        detalles = st.text_area("Notas o detalles de la prenda (opcional):")
        
        if st.button("Generar Ticket para WhatsApp"):
            if precio > 0:
                # Crear el texto del mensaje para enviar por WhatsApp
                fecha_actual = datetime.now().strftime("%d/%m/%Y")
                mensaje = f" *Eloísa Neleb Modas* 🛍️\n\n" \
                          f"¡Gracias por tu compra! \n" \
                          f"📅 Fecha: {fecha_actual}\n" \
                          f"👗 Prenda: {prenda}\n" \
                          f"💰 Total: {precio:.2f}€\n"
                if detalles:
                    mensaje += f"📝 Notas: {detalles}\n"
                mensaje += f"\n¡Esperamos que lo disfrutes! "
                
                # Convertir a formato URL para WhatsApp
                texto_url = urllib.parse.quote(mensaje)
                enlace_wa = f"https://wa.me/?text={texto_url}"
                
                st.info("Ticket generado con éxito. Haz clic abajo para enviarlo:")
                st.markdown(f'[📲 Enviar Ticket por WhatsApp]({enlace_wa})')
            else:
                st.warning("Por favor, introduce un precio mayor que 0.")

    # --- PESTAÑA 2: REGISTRAR CLIENTA ---
    with pestana_clientes:
        st.subheader("Registrar Nueva Clienta en Airtable")
        
        with st.form("nuevo_cliente", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre de la clienta:")
            nuevo_telefono = st.text_input("Teléfono:")
            boton_guardar = st.form_submit_button("Guardar en Airtable")
            
            if boton_guardar:
                if nuevo_nombre and nuevo_telefono:
                    conseguido = guardar_en_airtable(nuevo_nombre, nuevo_telefono)
                    if conseguido:
                        st.success(f"¡{nuevo_nombre} se ha guardado correctamente en Airtable!")
                else:
                    st.warning("Por favor, rellena ambos campos.")
