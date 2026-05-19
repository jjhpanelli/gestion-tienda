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

# Diccionario para convertir números dictados en texto a dígitos reales
def normalizar_numeros_texto(texto):
    numeros_letras = {
        "uno": "1", "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5",
        "seis": "6", "siete": "7", "ocho": "8", "nueve": "9", "diez": "10",
        "once": "11", "doce": "12", "trece": "13", "catorce": "14", "quince": "15",
        "veinte": "20", "treinta": "30", "cuarenta": "40", "cincuenta": "50"
    }
    palabras = texto.split()
    palabras_transformadas = [numeros_letras.get(p, p) for p in palabras]
    return " ".join(palabras_transformadas)

st.title("🛍️ Eloísa Neleb Modas")
st.subheader("🎙️ Generador de Tickets Inteligente")

lista_clientes = obtener_clientes()

# Cuadro de texto limpio
texto_venta = st.text_area("Dicta la venta aquí:", placeholder="Ej: Carmen lleva un vestido 35 y una blusa de 20", height=120)

if st.button("Generar Ticket ✨", type="primary"):
    if texto_venta.strip() == "":
        st.error("¡Primero tienes que introducir los datos de la venta!")
    else:
        # Normalizar el texto (pasar a minúsculas y cambiar números en letras a dígitos)
        frase_limpia = texto_venta.lower()
        frase_limpia = normalizar_numeros_texto(frase_limpia)
        
        # 1. Buscar cliente en la base de datos
        cliente_detectado = "Cliente Mostrador"
        telefono_detected = ""
        for c in lista_clientes:
            nombre_cli = c['nombre'].lower()
            if nombre_cli in frase_limpia or (nombre_cli.split() and nombre_cli.split()[0] in frase_limpia):
                cliente_detectado = c['nombre']
                telefono_detected = c['telefono']
                break
        
        # 2. Extraer combinaciones de Prenda + Precio de forma estricta
        # Busca cualquier palabra descriptiva seguida opcionalmente de "de/un/una" y luego el número
        patron = re.compile(r'([a-záéíóúñ]+(?:\s+[a-záéíóúñ]+)?)\s+(?:de\s+|un\s+|una\s+)?(\d+(?:[\.,]\d+)?)\b')
        coincidencias = patron.findall(frase_limpia)
        
        prendas_encontradas = []
        total = 0.0
        
        # Palabras prohibidas que jamás deben ser consideradas el nombre de una prenda
        palabras_prohibidas = {"para", "lleva", "un", "una", "el", "la", "y", "en", "con", "venta", "euros"}
        if cliente_detectado.split():
            palabras_prohibidas.add(cliente_detectado.split()[0].lower())

        for texto, numero in coincidencias:
            precio = float(numero.replace(',', '.'))
            if precio <= 0 or precio > 999:
                continue
            
            # Limpiar el bloque de texto previo quedándonos solo con las palabras reales de la prenda
            palabras_prenda = [p for p in texto.split() if p not in palabras_prohibidas]
            
            # Si el texto anterior contiene palabras de relleno, nos quedamos estrictamente con la última palabra (que suele ser el sustantivo: "vestido", "blusa")
            if palabras_prenda:
                nombre_prenda = palabras_prenda[-1]
                # Si venía con un adjetivo detrás (ej: "vestido blanco"), intentamos rescatar las dos últimas palabras válidas
                if len(palabras_prenda) >= 2 and palabras_prenda[-2] not in palabras_prohibidas:
                    nombre_prenda = f"{palabras_prenda[-2]} {palabras_prenda[-1]}"
            else:
                nombre_prenda = "Art. Moda"
                
            prendas_encontradas.append((nombre_prenda.capitalize(), precio))
            total += precio

        # 3. Generar el Formato Final del Ticket
        if prendas_encontradas:
            ticket = f"*ELOÍSA NELEB MODAS*\n-----------------------------------\n🔸 Clienta: {cliente_detectado.title()}\n-----------------------------------\n"
            for prenda, precio in prendas_encontradas:
                ticket += f"• {prenda}: {precio:.2f}€\n"
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
            st.error("No he podido extraer las prendas bien. Intenta dictar así: 'vestido 10 blusa 7 chaleco 8'")
