import streamlit as st
import json
import os
import urllib.parse
import requests
from datetime import datetime

# Credenciales de Airtable
AIRTABLE_TOKEN = "patkQeolTgZICdPkp.555b4fbda73bfaf10a9e9f41c3288703e6141d5370697cc27663dc52fc7914aa"
BASE_ID = "appkZ19FSlbQduoOp"

TABLE_CLIENTES = "Clientes"
TABLE_CATEGORIAS = "Categorias"
TABLE_VENTAS = "Ventas"

st.set_page_config(page_title="Gestión Eloísa Neleb", page_icon="🛍️", layout="centered")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- FUNCIONES AIRTABLE ---
def obtener_categorias():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CATEGORIAS}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            registros = response.json().get("records", [])
            return [{"id": r["id"], "nombre": r["fields"].get("Name")} for r in registros if r["fields"].get("Name")]
        return []
    except:
        return []

def añadir_categoria_airtable(nombre_cat):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CATEGORIAS}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
    data = {"records": [{"fields": {"Name": nombre_cat}}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        return res.status_code == 200
    except:
        return False

def borrar_categoria_airtable(record_id):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CATEGORIAS}/{record_id}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    try:
        res = requests.delete(url, headers=headers)
        return res.status_code == 200
    except:
        return False

def obtener_clientes_airtable():
    lista = []
    offset = ""
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    try:
        while True:
            url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CLIENTES}?sort[0][field]=nombre&sort[0][direction]=asc"
            if offset:
                url += f"&offset={offset}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                registros = data.get("records", [])
                for r in registros:
                    if r["fields"].get("nombre"):
                        lista.append({
                            "id": r["id"], 
                            "nombre": r["fields"].get("nombre"), 
                            "telefono": r["fields"].get("telefono")
                        })
                offset = data.get("offset")
                if not offset:
                    break
            else:
                break
        return lista
    except:
        return []

def guardar_cliente_airtable(nombre, telefono):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CLIENTES}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}", 
        "Content-Type": "application/json; charset=utf-8"
    }
    telefono_limpio = "".join(filter(str.isdigit, str(telefono)))
    data = {"records": [{"fields": {"nombre": str(nombre), "telefono": telefono_limpio}}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        return res.status_code == 200
    except:
        return False

def borrar_cliente_airtable(record_id):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CLIENTES}/{record_id}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    try:
        res = requests.delete(url, headers=headers)
        return res.status_code == 200
    except:
        return False

def guardar_venta_airtable(clienta, detalles, total):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_VENTAS}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json; charset=utf-8"}
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    data = {
        "records": [{
            "fields": {
                "fecha": fecha_hoy,
                "clienta": str(clienta),
                "detalles": str(detalles),
                "total": str(total)
            }
        }]
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        return res.status_code == 200
    except:
        return False

def obtener_ventas_airtable():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_VENTAS}?sort[0][field]=fecha&sort[0][direction]=desc"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("records", [])
        return []
    except:
        return []

def vaciar_ventas_airtable():
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    try:
        url_get = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_VENTAS}?fields[]="
        res_get = requests.get(url_get, headers=headers)
        if res_get.status_code == 200:
            registros = res_get.json().get("records", [])
            if not registros:
                return True
            for r in registros:
                requests.delete(f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_VENTAS}/{r['id']}", headers=headers)
            return True
        return False
    except:
        return False

# --- INTERFAZ ---
st.title("🛍️ Gestión Eloísa Neleb Modas")

clave = st.text_input("Introduce la contraseña:", type="password")
if clave == "1234":
    st.session_state.autenticado = True

if st.session_state.autenticado:
    st.success("Acceso concedido")
    
    categorias_data = obtener_categorias()
    nombres_categorias = [c["nombre"] for c in categorias_data] if categorias_data else ["General"]
    clientes_data = obtener_clientes_airtable()
    
    pestana_ventas, pestana_clientes, pestana_reporte, pestana_cats = st.tabs([
        "💰 Crear Venta", "👤 Clientes", "📊 Historial Ventas", "⚙️ Categorías"
    ])
    
    with pestana_ventas:
        st.subheader("Nueva Venta / Ticket de WhatsApp")
        nombre_clienta_texto = "Cliente Mostrador"
        telefono_destino = ""
        
        if clientes_data:
            opciones_clientes = [f"{c['nombre']} ({c['telefono']})" for c in clientes_data]
            opciones_clientes.insert(0, "Clienta no registrada (Sin número)")
            clienta_seleccionada = st.selectbox("Buscar y seleccionar clienta:", opciones_clientes)
            
            if clienta_seleccionada != "Clienta no registrada (Sin número)":
                indice = opciones_clientes.index(clienta_seleccionada) - 1
                telefono_destino = clientes_data[indice]["telefono"]
                nombre_clienta_texto = clientes_data[indice]["nombre"]
                telefono_destino = "".join(filter(str.isdigit, str(telefono_destino)))
        
        st.write("---")
        st.write("**Añadir prendas al ticket:**")
        col1, col2 = st.columns([2, 1])
        with col1:
            prenda_actual = st.selectbox("Prenda:", nombres_categorias, key="sel_prenda")
        with col2:
            precio_actual = st.number_input("Precio (€):", min_value=0.0, step=0.5, key="num_precio")
            
        detalles_actual = st.text_input("Detalle o color (opcional):", key="txt_detalle")
        
        if st.button("➕ Añadir esta prenda al Ticket"):
            if precio_actual > 0:
                st.session_state.carrito.append({
                    "prenda": prenda_actual,
                    "precio": precio_actual,
                    "detalles": detalles_actual
                })
                st.success(f"¡Añadido: {prenda_actual}!")
                st.rerun()
        
        st.write("---")
        
        if st.session_state.carrito:
            st.write("**Resumen del Ticket:**")
            total_suma = 0.0
            resumen_productos_texto = ""
            
            for item in st.session_state.carrito:
                texto_item = f"• {item['prenda']} - {item['precio']:.2f}€"
                if item['detalles']:
                    texto_item += f" ({item['detalles']})"
                st.write(texto_item)
                total_suma += item['precio']
                resumen_productos_texto += f"{item['prenda']}" + (f" ({item['detalles']})" if item['detalles'] else "") + f": {item['precio']:.2f}€\n"
            
            st.markdown(f"### **Total Actual: {total_suma:.2f}€**")
            
            if st.button("🗑️ Vaciar Ticket"):
                st.session_state.carrito = []
                st.rerun()
                
            st.write("---")
            
            if st.button("🎁 Generar Ticket y Guardar Venta"):
                fecha_actual = datetime.now().strftime("%d/%m/%Y")
                nombre_corto_cli = list(nombre_clienta_texto.split())[0]
                
                mensaje_completo = (
                    f"⭐ *ELOÍSA NELEB MODAS* ⭐\n"
                    f"✨ _Estilo y versatilidad para ti_ ✨\n\n"
                    f"📅 *Fecha:* {fecha_actual}\n"
                    f"👤 *Clienta:* {nombre_corto_cli}\n\n"
                    f"🔹──────────────────🔹\n"
                    f"🛍️ *DETALLE DE TU COMPRA:*\n\n"
                )
                
                for item in st.session_state.carrito:
                    mensaje_completo += f"▪️ *{item['prenda']}*"
                    if item['detalles']:
                        mensaje_completo += f" _{item['detalles']}_"
                    mensaje_completo += f"   ➔   *{item['precio']:.2f}€*\n"
                    
                mensaje_completo += (
                    f"🔹──────────────────🔹\n\n"
                    f"💰 *TOTAL NETO:* {total_suma:.2f}€\n\n"
                    f"💖 ¡Muchas gracias por tu confianza, {nombre_corto_cli}! ¡Vuelve pronto! 🛍️✨"
                )
                
                if guardar_venta_airtable(nombre_clienta_texto, resumen_productos_texto.strip(), total_suma):
                    st.success("✅ ¡Venta registrada automáticamente en Airtable!")
                    texto_url = urllib.parse.quote(mensaje_completo)
                    if telefono_destino:
                        if not telefono_destino.startswith("34") and len(telefono_destino) == 9:
                            telefono_destino = "34" + telefono_destino
                        enlace_wa = f"https://wa.me/{telefono_destino}?text={texto_url}"
                    else:
                        enlace_wa = f"https://wa.me/?text={texto_url}"
                    st.markdown(f'[📲 Enviar Ticket por WhatsApp]({enlace_wa})')
                    st.session_state.carrito = []
                else:
                    st.error("⚠️ No se pudo registrar la venta en Airtable. Revisa la conexión.")
        else:
            st.info("El ticket está vacío.")

    with pestana_clientes:
        st.subheader("Registrar Nueva Clienta")
        with st.form("nuevo_cliente", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre de la clienta:")
            nuevo_telefono = st.text_input("Teléfono:")
            if st.form_submit_button("Guardar en Airtable"):
                if nuevo_nombre and nuevo_telefono:
                    if guardar_cliente_airtable(nuevo_nombre, nuevo_telefono):
                        st.success(f"¡{nuevo_nombre} guardada!")
                        st.rerun()
                    else:
                        st.error("Error al guardar cliente.")
                        
        st.write("---")
        st.subheader("🗑️ Eliminar Clienta")
        if clientes_data:
            nombres_borrar = [c["nombre"] for c in clientes_data]
            clienta_a_borrar = st.selectbox("Selecciona clienta a eliminar:", nombres_borrar)
            if st.button("❌ Eliminar Clienta Seleccionada"):
                id_cliente = next((c["id"] for c in clientes_data if c["nombre"] == clienta_a_borrar), None)
                if id_cliente and borrar_cliente_airtable(id_cliente):
                    st.success(f"¡{clienta_a_borrar} eliminada!")
                    st.rerun()

    with pestana_reporte:
        st.subheader("📊 Panel de Ventas e Historial")
        ventas_data = obtener_ventas_airtable()
        if ventas_data:
            total_caja = 0.0
            for v in ventas_data:
                try:
                    total_caja += float(v["fields"].get("total", 0.0))
                except:
                    pass
            
            col_est1, col_est2 = st.columns(2)
            col_est1.metric("💰 Facturación Total", f"{total_caja:.2f} €")
            col_est2.metric("🛍️ Total Ventas", f"{len(ventas_data)} tickets")
            
            st.write("---")
            for v in ventas_data:
                f = v["fields"]
                with st.expander(f"📅 {f.get('fecha','-')} | 👤 {f.get('clienta','-')} | 💵 {f.get('total',0.0)}€"):
                    st.text(f.get("detalles", "Sin detalles"))
            
            st.write("---")
            st.subheader("⚠️ Zona de Mantenimiento")
            if st.checkbox("Entiendo que esto borrará el historial visual de ventas de Airtable"):
                if st.button("🚨 VACIAR HISTORIAL DE VENTAS AHORA", type="primary"):
                    if vaciar_ventas_airtable():
                        st.success("🗑️ ¡Historial vaciado!")
                        st.rerun()
        else:
            st.info("No hay ventas registradas.")

    with pestana_cats:
        st.subheader("Gestionar Categorías")
        with st.form("add_cat", clear_on_submit=True):
            nueva_cat = st.text_input("Nueva categoría:")
            if st.form_submit_button("➕ Añadir Categoría"):
                if nueva_cat and añadir_categoria_airtable(nueva_cat):
                    st.success("¡Añadida!")
                    st.rerun()
        st.write("---")
        if categorias_data:
            cat_a_borrar = st.selectbox("Eliminar categoría:", nombres_categorias)
            if st.button("❌ Eliminar Categoría"):
                id_cat = next((c["id"] for c in categorias_data if c["nombre"] == cat_a_borrar), None)
                if id_cat and borrar_categoria_airtable(id_cat):
                    st.success("¡Eliminada!")
                    st.rerun()
