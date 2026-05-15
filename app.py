import streamlit as st
import json
import os
import urllib.parse
import requests
from datetime import datetime

# Configuración de tus credenciales
AIRTABLE_TOKEN = "patkQeolTgZICdPkp.555b4fbda73bfaf10a9e9f41c3288703e6141d5370697cc27663dc52fc7914aa
"
BASE_ID = "appkZ19FSlbQduoOp"
TABLE_CLIENTES = "Clientes"
TABLE_CATEGORIAS = "Categorias"

# Configuración de la página
st.set_page_config(page_title="Gestión Eloísa Neleb", page_icon="🛍️", layout="centered")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Inicializar el carrito de la compra en la sesión para que no se borre al recargar
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- FUNCIONES DE AIRTABLE ---
def obtener_categorias():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CATEGORIAS}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            registros = response.json().get("records", [])
            lista = [{"id": r["id"], "nombre": r["fields"].get("Name")} for r in registros if r["fields"].get("Name")]
            return lista
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
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CLIENTES}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            registros = response.json().get("records", [])
            lista = [{"nombre": r["fields"].get("nombre"), "telefono": r["fields"].get("telefono")} for r in registros if r["fields"].get("nombre")]
            return lista
        return []
    except:
        return []

def guardar_cliente_airtable(nombre, telefono):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CLIENTES}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
    data = {"records": [{"fields": {"nombre": nombre, "telefono": telefono}}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        return res.status_code == 200
    except:
        return False

# --- INTERFAZ DE LA APLICACIÓN ---
st.title("🛍️ Gestión Eloísa Neleb Modas")

clave = st.text_input("Introduce la contraseña:", type="password")
if clave == "1234":
    st.session_state.autenticado = True

if st.session_state.autenticado:
    st.success("Acceso concedido")
    
    # Cargar datos vivos
    categorias_data = obtener_categorias()
    nombres_categorias = [c["nombre"] for c in categorias_data] if categorias_data else ["General"]
    clientes_data = obtener_clientes_airtable()
    
    pestana_ventas, pestana_clientes, pestana_cats = st.tabs(["💰 Crear Venta", "👤 Registrar Clienta", "⚙️ Ajustes Categorías"])
    
    # --- PESTAÑA 1: CREAR VENTA (CON CARRITO MULTI-PRENDA) ---
    with pestana_ventas:
        st.subheader("Nueva Venta / Ticket de WhatsApp")
        
        # 1. Selección de Clienta
        if clientes_data:
            opciones_clientes = [f"{c['nombre']} ({c['telefono']})" for c in clientes_data]
            opciones_clientes.insert(0, "Clienta no registrada (Sin número)")
            clienta_seleccionada = st.selectbox("Buscar y seleccionar clienta:", opciones_clientes)
            
            if clienta_seleccionada != "Clienta no registrada (Sin número)":
                indice = opciones_clientes.index(clienta_seleccionada) - 1
                telefono_destino = clientes_data[indice]["telefono"]
                telefono_destino = "".join(filter(str.isdigit, str(telefono_destino)))
            else:
                telefono_destino = ""
        else:
            st.info("Aún no tienes clientas en Airtable.")
            telefono_destino = ""
            
        st.write("---")
        
        # 2. Añadir prendas a la lista actual
        st.write("**Añadir prendas al ticket actual:**")
        col1, col2 = st.columns([2, 1])
        with col1:
            prenda_actual = st.selectbox("Prenda:", nombres_categorias, key="sel_prenda")
        with col2:
            precio_actual = st.number_input("Precio (€):", min_value=0.0, step=0.5, key="num_precio")
            
        detalles_actual = st.text_input("Detalle o color (opcional):", key="txt_detalle")
        
        if st.button("➕ Añadir esta prenda al Ticket"):
            if precio_actual > 0:
                # Metemos la prenda en la lista de la sesión
                st.session_state.carrito.append({
                    "prenda": prenda_actual,
                    "precio": precio_actual,
                    "detalles": detalles_actual
                })
                st.success(f"¡Añadido: {prenda_actual} por {precio_actual:.2f}€!")
            else:
                st.warning("El precio debe ser mayor que 0.")
        
        st.write("---")
        
        # 3. Mostrar lo que va sumado en el ticket
        if st.session_state.carrito:
            st.write("**Resumen de lo que lleva sumado:**")
            total_suma = 0.0
            for i, item in enumerate(st.session_state.carrito):
                texto_item = f"• {item['prenda']} - {item['precio']:.2f}€"
                if item['detalles']:
                    texto_item += f" ({item['detalles']})"
                st.write(texto_item)
                total_suma += item['precio']
            
            st.markdown(f"### **Total Actual: {total_suma:.2f}€**")
            
            # Botón para vaciar si te equivocas
            if st.button("🗑️ Vaciar Ticket"):
                st.session_state.carrito = []
                st.rerun()
                
            st.write("---")
            
            # 4. Botón para generar el mensaje completo de WhatsApp
            if st.button("🎁 Generar Ticket Completo para WhatsApp"):
                fecha_actual = datetime.now().strftime("%d/%m/%Y")
                
                # Cabecera del mensaje
                mensaje = f" *Eloísa Neleb Modas* 🛍️\n\n¡Gracias por tu compra! \n📅 Fecha: {fecha_actual}\n\n"
                mensaje += "*Detalle de tu compra:*\n"
                
                # Desglose de cada una de las prendas guardadas
                for item in st.session_state.carrito:
                    mensaje += f"👗 {item['prenda']}: {item['precio']:.2f}€"
                    if item['detalles']:
                        mensaje += f" ({item['detalles']})"
                    mensaje += "\n"
                    
                # Cierre con el total sumado solo
                mensaje += f"\n💰 *Total: {total_suma:.2f}€*\n\n¡Esperamos que lo disfrutes! "
                
                texto_url = urllib.parse.quote(mensaje)
                
                if telefono_destino:
                    if not telefono_destino.startswith("34") and len(telefono_destino) == 9:
                        telefono_destino = "34" + telefono_destino
                    enlace_wa = f"https://wa.me/{telefono_destino}?text={texto_url}"
                else:
                    enlace_wa = f"https://wa.me/?text={texto_url}"
                    
                st.info("Ticket multibolsa generado con éxito:")
                st.markdown(f'[📲 Enviar Ticket Completo por WhatsApp]({enlace_wa})')
                
                # Vaciamos el carrito automáticamente tras generar el ticket para la siguiente venta
                st.session_state.carrito = []
        else:
            st.info("El ticket está vacío. Añade alguna prenda arriba para empezar a sumar.")

    # --- PESTAÑA 2: REGISTRAR CLIENTA ---
    with pestana_clientes:
        st.subheader("Registrar Nueva Clienta en Airtable")
        with st.form("nuevo_cliente", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre de la clienta:")
            nuevo_telefono = st.text_input("Teléfono:")
            boton_guardar = st.form_submit_button("Guardar en Airtable")
            
            if boton_guardar:
                if nuevo_nombre and nuevo_telefono:
                    if guardar_cliente_airtable(nuevo_nombre, nuevo_telefono):
                        st.success(f"¡{nuevo_nombre} se ha guardado correctamente!")
                        st.rerun()
                    else:
                        st.error("Error al guardar cliente.")
                else:
                    st.warning("Por favor, rellena ambos campos.")

    # --- PESTAÑA 3: GESTIONAR CATEGORÍAS ---
    with pestana_cats:
        st.subheader("Gestionar Categorías de la Tienda")
        with st.form("add_cat", clear_on_submit=True):
            nueva_cat = st.text_input("Añadir nueva categoría (ej: Blusas):")
            if st.form_submit_button("➕ Añadir Categoría"):
                if nueva_cat:
                    if añadir_categoria_airtable(nueva_cat):
                        st.success(f"¡'{nueva_cat}' añadida con éxito!")
                        st.rerun()
                    else:
                        st.error("Error al añadir en Airtable.")
        
        st.write("---")
        
        if categorias_data:
            cat_a_borrar = st.selectbox("Selecciona la categoría que deseas eliminar:", nombres_categorias)
            if st.button("❌ Eliminar Categoría Seleccionada"):
                id_airtable = next((c["id"] for c in categorias_data if c["nombre"] == cat_a_borrar), None)
                if id_airtable:
                    if borrar_categoria_airtable(id_airtable):
                        st.success(f"¡'{cat_a_borrar}' eliminada con éxito!")
                        st.rerun()
                    else:
                        st.error("Error al eliminar de Airtable.")
        else:
            st.info("No hay categorías para borrar en Airtable.")
