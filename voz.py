import streamlit as st
import urllib.parse
import requests
import re

# Configuración de la pantalla
st.set_page_config(page_title="Voz - Eloísa Neleb", page_icon="🎙️", layout="centered")

# ==========================================
# 🔑 RECOGIDA AUTOMÁTICA DE SECRETS
# ==========================================
try:
    AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
    AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
except:
    st.error("🔑 Configura primero las llaves de Airtable en la sección de Secrets de Streamlit.")
    st.stop()

AIRTABLE_TABLE_NAME = "Clientes"

headers = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}

# Funciones de conexión con Airtable
@st.cache_data(ttl=2)
def obtener_clientes():
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}?sort[0][field]=nombre&sort[0][direction]=asc"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return [{"id": r.get("id"), "nombre": r.get("fields", {}).get("nombre", ""), "telefono": r.get("fields", {}).get("telefono", "")} for r in response.json().get("records", [])]
        return []
    except:
        return []

def agregar_cliente_airtable(nombre, telefono):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    datos = {"fields": {"nombre": nombre, "telefono": telefono}}
    try:
        response = requests.post(url, headers=headers, json=datos)
        return response.status_code == 200
    except:
        return False

def borrar_cliente_airtable(record_id):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}/{record_id}"
    try:
        response = requests.delete(url, headers=headers)
        return response.status_code == 200
    except:
        return False

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

# --- MENÚ DE PESTAÑAS ---
pestana_ticket, pestana_alta, pestana_baja = st.tabs(["🎙️ Generar Ticket", "➕ Añadir Clienta", "🗑️ Borrar Clienta"])

lista_clientes = obtener_clientes()

# ==========================================
# PESTAÑA 1: GENERADOR DE TICKETS
# ==========================================
with pestana_ticket:
    st.title("🛍️ Eloísa Neleb Modas")
    st.subheader("Generador de Tickets Inteligente")
    
    opciones_selector = ["Detectar automáticamente por voz"] + [c['nombre'] for c in lista_clientes]
    
    clienta_manual = st.selectbox(
        "Selecciona la clienta (o deja que la IA la busque en tu dictado):", 
        options=opciones_selector
    )

    texto_venta = st.text_area("Dicta la venta o escribe aquí:", placeholder="Ej: Vestido blanco de 10 blusa 7 chaleco 8", height=120)

    if st.button("Generar Ticket ✨", type="primary"):
        if texto_venta.strip() == "":
            st.error("¡Primero tienes que introducir los datos de la venta!")
        else:
            frase_limpia = texto_venta.lower()
            frase_limpia = normalizar_numeros_texto(frase_limpia)
            
            cliente_detectado = "Cliente Mostrador"
            telefono_detected = ""
            
            if clienta_manual != "Detectar automáticamente por voz" and clienta_manual is not None:
                cliente_detectado = clienta_manual
                for c in lista_clientes:
                    if c['nombre'] == clienta_manual:
                        telefono_detected = c['telefono']
                        break
            else:
                for c in lista_clientes:
                    nombre_cli = c['nombre'].lower()
                    if nombre_cli in frase_limpia or (nombre_cli.split() and nombre_cli.split()[0] in frase_limpia):
                        cliente_detectado = c['nombre']
                        telefono_detected = c['telefono']
                        break
            
            patron = re.compile(r'([a-záéíóúñ]+(?:\s+[a-záéíóúñ]+)?)\s+(?:de\s+|un\s+|una\s+)?(\d+(?:[\.,]\d+)?)\b')
            coincidencias = patron.findall(frase_limpia)
            
            prendas_encontradas = []
            total = 0.0
            
            palabras_prohibidas = {"para", "lleva", "un", "una", "el", "la", "y", "en", "con", "venta", "euros"}
            if cliente_detectado.split():
                palabras_prohibidas.add(cliente_detectado.split()[0].lower())

            for texto, numero in coincidencias:
                precio = float(numero.replace(',', '.'))
                if precio <= 0 or precio > 999:
                    continue
                
                palabras_prenda = [p for p in texto.split() if p not in palabras_prohibidas]
                
                if palabras_prenda:
                    nombre_prenda = palabras_prenda[-1]
                    if len(palabras_prenda) >= 2 and palabras_prenda[-2] not in palabras_prohibidas:
                        nombre_prenda = f"{palabras_prenda[-2]} {palabras_prenda[-1]}"
                else:
                    nombre_prenda = "Art. Moda"
                    
                prendas_encontradas.append((nombre_prenda.capitalize(), precio))
                total += precio

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
                st.error("No he podido extraer las prendas bien. Intenta dictar así: 'vestido 10 blusa 7'")

# ==========================================
# PESTAÑA 2: AÑADIR NUEVAS CLIENTAS
# ==========================================
with pestana_alta:
    st.subheader("➕ Registrar Nueva Clienta")
    with st.form("formulario_alta", clear_on_submit=True):
        nuevo_nombre = st.text_input("Nombre de la clienta:")
        nuevo_tlf = st.text_input("Teléfono (ej: 34600123456):", placeholder="Pon el 34 delante si es de España")
        enviar_alta = st.form_submit_button("Guardar en Airtable 💾")
        
        if enviar_alta:
            if nuevo_nombre.strip() == "" or nuevo_tlf.strip() == "":
                st.error("Por favor, rellena tanto el nombre como el teléfono.")
            else:
                tlf_limpio = nuevo_tlf.replace(" ", "").replace("+", "")
                if agregar_cliente_airtable(nuevo_nombre.strip(), tlf_limpio):
                    st.success(f"¡{nuevo_nombre} se ha guardado correctamente!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Vaya, hubo un problema al conectar con Airtable. Comprueba los Secrets.")

# ==========================================
# PESTAÑA 3: BORRAR CLIENTAS
# ==========================================
with pestana_baja:
    st.subheader("🗑️ Eliminar Clienta del Registro")
    if not lista_clientes:
        st.info("No hay clientas registradas todavía o la aplicación está conectando con Airtable...")
    else:
        st.write("Selecciona una clienta de la lista para borrarla para siempre de Airtable:")
        for cli in lista_clientes:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"👤 **{cli['nombre']}** ({cli['telefono']})")
            with col2:
                if st.button("Borrar ❌", key=f"del_{cli['id']}"):
                    if borrar_cliente_airtable(cli['id']):
                        st.success(f"Eliminada correctamente.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("No se pudo borrar.")
