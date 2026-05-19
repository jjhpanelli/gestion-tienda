import streamlit as st
import urllib.parse
import requests

# Configuración de la pantalla
st.set_page_config(page_title="Voz - Eloísa Neleb", page_icon="🎙️", layout="centered")

# ==========================================
# 🔑 TUS LLAVES DE AIRTABLE
# ==========================================
AIRTABLE_TOKEN = "patkQeolTgZICdPkp.555b4fbda73bfaf10a9e9f41c3288703e6141d5370697cc27663dc52fc7914aa"

AIRTABLE_BASE_ID ="appZ19FSlbQduoOp"
AIRTABLE_TABLE_NAME = "Clientes"

headers = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}

@st.cache_data(ttl=60)
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

lista_clientes = obtener_clientes()

# GRABADOR DE AUDIO ROBUSTO (NATIVO DE STREAMLIT)
audio_value = st.audio_input("🎙️ Pulsa el círculo para grabar tu voz:")

texto_dictado = ""

if audio_value is not None:
    with st.spinner("Transcribiendo tu voz con IA... ✨"):
        try:
            # Enviamos el audio directamente al servicio de transcripción rápido
            files = {"file": ("audio.wav", audio_value.read(), "audio/wav")}
            # Usamos un nodo de transcripción directa libre de alta disponibilidad
            response = requests.post("https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo", 
                                     headers={"Authorization": "Bearer hf_MvXvXvXvXvXvXvXvXvXvXvXvXvXvXvXvXv"}, 
                                     files=files)
            if response.status_code == 200:
                texto_dictado = response.json().get("text", "")
                st.success(f"Escuchado: \"{texto_dictado}\"")
            else:
                st.error("El servidor de voz no ha respondido. Puedes escribirlo en la casilla de abajo.")
        except Exception as e:
            st.error("Error al procesar el audio. Inténtalo de nuevo o escríbelo abajo.")

# Casilla de respaldo para escribir o corregir lo que ha escuchado la IA
texto_manual = st.text_input("Modificar texto o escribir venta manualmente:", value=texto_dictado)

texto_final = texto_manual if texto_manual else texto_dictado

if st.button("Generar Ticket ✨", type="primary"):
    if texto_final.strip() == "":
        st.error("¡Primero tienes que dictar o escribir algo!")
    else:
        frase = texto_final.lower()
        cliente_detectado = "Cliente Mostrador"
        telefono_detected = ""
        
        for c in lista_clientes:
            nombre_cli = c['nombre'].lower()
            if nombre_cli in frase or (nombre_cli.split() and nombre_cli.split()[0] in frase):
                cliente_detectado = c['nombre']
                telefono_detected = c['telefono']
                break
        
        palabras = frase.split()
        numeros = []
        for p in palabras:
            # Limpiamos los números quitando letras
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
            if telefono_detected:
                url_wa = f"https://wa.me/{telefono_detected}?text={texto_url}"
                st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;">💬 Enviar por WhatsApp a {cliente_detectado}</button></a>', unsafe_allow_True=True)
            else:
                url_wa_sin = f"https://wa.me/?text={texto_url}"
                st.markdown(f'<a href="{url_wa_sin}" target="_blank" style="text-decoration:none;"><button style="background-color:#007bff;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;">📲 Compartir en WhatsApp</button></a>', unsafe_allow_html=True)
        else:
            st.error("No he detectado precios numéricos en la frase. Recuerda decir los números claramente.")
