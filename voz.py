import streamlit as st
import urllib.parse
import requests

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

# Traer los clientes ordenados de la A a la Z para la voz
def obtener_clientes():
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}?sort[0][field]=nombre&sort[0][direction]=asc"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            records = response.json().get("records", [])
            return [{"nombre": r.get("fields", {}).get("nombre", ""), "telefono": r.get("fields", {}).get("telefono", "")} for r in records]
        return []
    except:
        return []

st.title("🛍️ Eloísa Neleb Modas")
st.subheader("🎙️ Generador de Tickets por Voz")
st.write("Toca el cuadro de texto, activa el micrófono de tu teclado y dicta la venta de forma natural.")

lista_clientes = obtener_clientes()

# Entrada de dictado
texto_dictado = st.text_input("Dicta aquí la venta:", placeholder="Ej: Venta para Carmen un pantalon de 35 y un vestido de 20")

if st.button("Generar Ticket ✨", type="primary"):
    if texto_dictado.strip() == "":
        st.error("¡Primero tienes que decir o escribir algo!")
    else:
        frase = texto_dictado.lower()
        
        # 1. Buscar cliente por coincidencia inteligente
        cliente_detectado = "Cliente Mostrador"
        telefono_detectado = ""
        
        for c in lista_clientes:
            nombre_cli = c['nombre'].lower()
            if nombre_cli in frase or (nombre_cli.split() and nombre_cli.split()[0] in frase):
                cliente_detectado = c['nombre']
                telefono_detectado = c['telefono']
                break
        
        # 2. Extraer precios numéricos
        palabras = frase.split()
        numeros = []
        for p in palabras:
            num_limpio = ''.join(caracter for caracter in p if caracter.isdigit() or caracter == '.')
            if num_limpio and len(num_limpio) <= 3:
                numeros.append(float(num_limpio))
        
        # 3. Armar el ticket para WhatsApp
        if numeros:
            total = sum(numeros)
            
            ticket = f"*ELOÍSA NELEB MODAS*\n"
            ticket += f"-----------------------------------\n"
            ticket += f"🔸 Clienta: {cliente_detectado.title()}\n"
            ticket += f"-----------------------------------\n"
            for i, precio in enumerate(numeros):
                ticket += f"• Prenda {i+1}: {precio}€\n"
            ticket += f"-----------------------------------\n"
            ticket += f"💰 *TOTAL: {total}€*\n"
            ticket += f"-----------------------------------\n"
            ticket += f"¡Gracias por tu confianza! ✨"
            
            st.success(f"Clienta detectada: {cliente_detectado}")
            st.text_area("Ticket listo:", value=ticket, height=200)
            
            # Botón de enviar
            texto_url = urllib.parse.quote(ticket)
            if telefono_detectado:
                url_wa = f"https://wa.me/{telefono_detectado}?text={texto_url}"
                st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;">💬 Enviar por WhatsApp a {cliente_detectado}</button></a>', unsafe_allow_html=True)
            else:
                url_wa_sin = f"https://wa.me/?text={texto_url}"
                st.markdown(f'<a href="{url_wa_sin}" target="_blank" style="text-decoration:none;"><button style="background-color:#007bff;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;">📲 Compartir en WhatsApp (Elegir Contacto)</button></a>', unsafe_allow_html=True)
        else:
            st.error("No he detectado precios. Intenta decir: 'vestido 40 y pantalon 25'")
