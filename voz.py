import streamlit as st
import urllib.parse
import requests
from audio_recorder_streamlit import audio_recorder
import io

# Configuración de la pantalla
st.set_page_config(page_title="Voz - Eloísa Neleb", page_icon="🎙️", layout="centered")

# ==========================================
# 🔑 TUS LLAVES DE AIRTABLE
# ==========================================
AIRTABLE_TOKEN = "patkQeolTgZICdPkp.555b4fbda73bfaf10a9e9f41c3288703e6141d5370697cc27663dc52fc7914aa"


AIRTABLE_BASE_ID = "appZ19FSlbQduoOp"
AIRTABLE_TABLE_NAME = "Clientes"

headers = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}

def obtener_clientes():
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}?sort[0][field]=nombre&sort[0][direction]=asc"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return [{"nombre": r.get("fields", {}).get("nombre", ""), "telefono": r.get("fields", {}).get("telefono", "")} for r in response.json().get("records", [])]
        return []
    except:
        return []

st.title("🛍️ Eloísa Neleb Modas")
st.subheader("🎙️ Generador de Tickets por Voz")
st.write("Toca el micrófono de abajo, habla con naturalidad y vuelve a pulsar cuando termines.")

lista_clientes = obtener_clientes()

# GRABADOR DE AUDIO PROPIO EN LA WEB
audio_bytes = audio_recorder(
    text="Toca para grabar",
    recording_color="#e74c3c",
    neutral_color="#34495e",
    icon_name="microphone",
    icon_size="3x"
)

# Variable para almacenar el texto final
texto_dictado = ""

if audio_bytes:
    # Mostramos un mensaje de carga mientras procesamos el audio
    with st.spinner("Traduciendo tu voz a texto... ✨"):
        try:
            # Enviamos el audio a la API de Hugging Face (gratuita y libre) para transcribir
            API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
            headers_hf = {"Authorization": "Bearer hf_MvXvXvXvXvXvXvXvXvXvXvXvXvXvXvXvXv"} # Token público temporal
            response = requests.post(API_URL, headers=headers_hf, data=audio_bytes)
            
            if response.status_code == 200:
                texto_dictado = response.json().get("text", "")
                st.info(f"Escuchado: \"{texto_dictado}\"")
            else:
                st.error("Error al procesar el audio de forma nativa. Intenta escribirlo abajo.")
        except:
            st.error("Servidor de voz ocupado. Intenta escribirlo abajo.")

# Por si falla el micro, dejamos también un cuadro de texto normal de respaldo
texto_manual = st.text_input("O escribe/corrige aquí la venta:", value=texto_dictado)

texto_final = texto_manual if texto_manual else texto_dictado

if st.button("Generar Ticket ✨", type="primary"):
    if texto_final.strip() == "":
        st.error("¡Primero tienes que decir o escribir algo!")
    else:
        frase = texto_final.lower()
        cliente_detectado = "Cliente Mostrador"
        telefono_detectado = ""
        
        for c in lista_clientes:
            nombre_cli = c['nombre'].lower()
            if nombre_cli in frase or (nombre_cli.split() and nombre_cli.split()[0] in frase):
                cliente_detectado = c['nombre']
                telefono_detectado = c['telefono']
                break
        
        palabras = frase.split()
        numeros = []
        for p in palabras:
            num_limpio = ''.join(caracter for caracter in p if caracter.isdigit() or caracter == '.')
            if num_limpio and len(num_limpio) <= 3:
                numeros.append(float(num_limpio))
        
        if numeros:
            total = sum(numeros)
            ticket = f"*ELOÍSA NELEB MODAS*\n-----------------------------------\n🔸 Clienta: {cliente_detectado.title()}\n-----------------------------------\n"
            for i, precio in enumerate(numeros):
                ticket += f"• Prenda {i+1}: {precio}€\n"
            ticket += f"-----------------------------------\n💰 *TOTAL: {total}€*\n-----------------------------------\n¡Gracias por tu confianza! ✨"
            
            st.success(f"Clienta detectada: {cliente_detectado}")
            st.text_area("Ticket listo:", value=ticket, height=200)
            
            texto_url = urllib.parse.quote(ticket)
            if telefono_detectado:
                url_wa = f"https://wa.me/{telefono_detectado}?text={texto_url}"
                st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;">💬 Enviar por WhatsApp a {cliente_detectado}</button></a>', unsafe_allow_html=True)
            else:
                url_wa_sin = f"https://wa.me/?text={texto_url}"
                st.markdown(f'<a href="{url_wa_sin}" target="_blank" style="text-decoration:none;"><button style="background-color:#007bff;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;">📲 Compartir en WhatsApp</button></a>', unsafe_allow_html=True)
        else:
            st.error("No he detectado precios numéricos en la frase.")
