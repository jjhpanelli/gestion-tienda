import streamlit as st
import urllib.parse
import requests
import re

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
st.subheader("🎙️ Generador de Tickets Inteligente")
st.write("Toca el cuadro de abajo, usa el dictado por voz de tu móvil y genera el ticket desglosado.")

lista_clientes = obtener_clientes()

# Cuadro de texto donde el dictado de tu móvil escribe solo
texto_venta = st.text_area("Dicta la venta aquí:", placeholder="Ej: Venta para Carmen un pantalón 35 y una blusa 20", height=120)

if st.button("Generar Ticket ✨", type="primary"):
    if texto_venta.strip() == "":
        st.error("¡Primero tienes que introducir los datos de la venta!")
    else:
        frase = texto_venta.lower()
        
        # 1. Buscar cliente en la base de datos
        cliente_detectado = "Cliente Mostrador"
        telefono_detected = ""
        for c in lista_clientes:
            nombre_cli = c['nombre'].lower()
            if nombre_cli in frase or (nombre_cli.split() and nombre_cli.split()[0] in frase):
                cliente_detectado = c['nombre']
                telefono_detected = c['telefono']
                break
        
        # 2. Extraer prendas y precios de forma inteligente (busca texto + número)
        # Busca patrones como "pantalón 35", "blusa de 20", "vestido 45.5"
        patron = re.compile(r'([a-záéíóúñ#\s]+?)(?:de\s+)?(\d+(?:[\.,]\d+)?)\b')
        coincidencias = patron.findall(frase)
        
        prendas_encontradas = []
        total = 0.0
        
        # Palabras que queremos ignorar para que no salgan como nombre de prenda
        palabras_filtro = ["para", "un", "una", "el", "la", "y", "en", "con", "venta", cliente_detectado.lower()]
        if cliente_detectado.split():
            palabras_filtro.append(cliente_detectado.split()[0].lower())

        for texto, numero in coincidencias:
            precio = float(numero.replace(',', '.'))
            if precio <= 0 or precio > 999: # Filtro para evitar años o números raros
                continue
                
            # Limpiar el nombre de la prenda
            palabras_prenda = [p for p in texto.split() if p not in palabras_filtro]
            nombre_prenda = " ".join(palabras_prenda).strip()
            
            # Si se queda vacío, le ponemos un nombre genérico
            if not nombre_prenda:
                nombre_prenda = "Art. Moda"
                
            prendas_encontradas.append((nombre_prenda.capitalize(), precio))
            total += precio

        # 3. Generar el formato del Ticket
        if prendas_encontradas:
            ticket = f"*ELOÍSA NELEB MODAS*\n-----------------------------------\n🔸 Clienta: {cliente_detectado.title()}\n-----------------------------------\n"
            for prenda, precio in prendas_encontradas:
                ticket += f"• {prenda}: {precio}€\n"
            ticket += f"-----------------------------------\n💰 *TOTAL: {total:.2f}€*\n-----------------------------------\n¡Gracias por tu confianza! ✨"
            
            st.success(f"Ticket generado con éxito para {cliente_detectado}")
            st.text_area("Ticket listo para enviar:", value=ticket, height=220)
            
            texto_url = urllib.parse.quote(ticket)
            if telefono_detected:
                url_wa = f"https://wa.me/{telefono_detected}?text={texto_url}"
                st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;margin-top:10px;">💬 Enviar por WhatsApp a {cliente_detectado}</button></a>', unsafe_allow_html=True)
            else:
                url_wa_sin = f"https://wa.me/?text={texto_url}"
                st.markdown(f'<a href="{url_wa_sin}" target="_blank" style="text-decoration:none;"><button style="background-color:#007bff;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;margin-top:10px;">📲 Compartir en WhatsApp</button></a>', unsafe_allow_html=True)
        else:
            st.error("No he podido desglosar las prendas correctamente. Intenta dictar con el formato: 'pantalón 35 blusa 20'")
