import streamlit as st
import urllib.parse
import requests
import streamlit.components.v1 as components

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
st.subheader("🎙️ Generador de Tickets por Voz")

lista_clientes = obtener_clientes()

# Inicializar el estado del texto si no existe
if "texto_voz" not in st.session_state:
    st.session_state.texto_voz = ""

# 🛠️ COMPONENTE JAVASCRIPT: Activa el dictado oficial de Google/Android directamente
st.write("Pulsa el botón de abajo para empezar a hablar:")
componente_html = """
<div style="text-align: center; margin-bottom: 20px;">
    <button id="btn-micro" style="background-color: #e74c3c; color: white; border: none; padding: 15px 30px; border-radius: 50px; font-size: 18px; font-weight: bold; cursor: pointer; width: 100%;">
        🔴 PULSAR PARA HABLAR
    </button>
    <p id="estado" style="color: #7f8c8d; font-size: 14px; margin-top: 8px;">Micrófono listo</p>
</div>

<script>
    const btn = document.getElementById('btn-micro');
    const estado = document.getElementById('estado');
    
    // Comprobar si el navegador soporta el reconocimiento de voz nativo
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        estado.innerText = "Tu móvil no soporta este sistema. Usa el teclado.";
        btn.disabled = true;
        btn.style.backgroundColor = "#7f8c8d";
    } else {
        const recognition = new SpeechRecognition();
        recognition.lang = 'es-ES';
        recognition.continuous = false;
        recognition.interimResults = false;

        btn.onclick = function() {
            try {
                recognition.start();
                estado.innerText = "🎙️ Escuchando... Habla ahora";
                btn.style.backgroundColor = "#2ecc71";
                btn.innerText = "🟢 ESCUCHANDO...";
            } catch(e) {
                // Por si ya estaba iniciado
            }
        };

        recognition.onresult = function(event) {
            const texto = event.results[0][0].transcript;
            estado.innerText = "✅ Entendido";
            btn.style.backgroundColor = "#e74c3c";
            btn.innerText = "🔴 PULSAR PARA HABLAR";
            
            # Enviar el texto de vuelta a Streamlit
            window.parent.postMessage({
                type: 'streamlit:set_widget_value',
                from: 'componente_voz',
                value: texto
            }, '*');
            
            // Forzar actualización mandando un click invisible
            const inputs = window.parent.document.getElementsByTagName('input');
            if(inputs.length > 0) { inputs[0].focus(); inputs[0].blur(); }
        };

        recognition.onerror = function(event) {
            estado.innerText = "Error o tiempo de espera agotado. Pulsa otra vez.";
            btn.style.backgroundColor = "#e74c3c";
            btn.innerText = "🔴 PULSAR PARA HABLAR";
        };
        
        recognition.onend = function() {
            btn.style.backgroundColor = "#e74c3c";
            btn.innerText = "🔴 PULSAR PARA HABLAR";
        };
    }
</script>
"""

# Renderizamos el botón nativo en pantalla
resultado = components.html(componente_html, height=100)

# Cuadro donde aparecerá automáticamente lo dictado para que lo revises
texto_final = st.text_input("Texto capturado por voz (puedes corregirlo si hace falta):", key="componente_voz")

if st.button("Generar Ticket ✨", type="primary"):
    if texto_final.strip() == "":
        st.error("¡Primero tienes que pulsar el botón rojo y hablar!")
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
            st.text_area("Ticket listo para enviar:", value=ticket, height=180)
            
            texto_url = urllib.parse.quote(ticket)
            if telefono_detected:
                url_wa = f"https://wa.me/{telefono_detected}?text={texto_url}"
                st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;">💬 Enviar por WhatsApp a {cliente_detectado}</button></a>', unsafe_allow_html=True)
            else:
                url_wa_sin = f"https://wa.me/?text={texto_url}"
                st.markdown(f'<a href="{url_wa_sin}" target="_blank" style="text-decoration:none;"><button style="background-color:#007bff;color:white;border:none;padding:12px 20px;border-radius:5px;cursor:pointer;font-weight:bold;width:100%;">📲 Compartir en WhatsApp</button></a>', unsafe_allow_html=True)
        else:
            st.error("No he detectado precios numéricos en la frase.")
