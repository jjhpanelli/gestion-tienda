import streamlit as st
import sqlite3
import urllib.parse
from datetime import datetime

# --- 1. SEGURIDAD ---
CLAVE_ACCESO = "Eloisa2026" 

def login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        st.title("🔐 Acceso Socios - Eloísa Neleb")
        password = st.text_input("Introduce la contraseña:", type="password")
        if st.button("Entrar"):
            if password == CLAVE_ACCESO:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        return False
    return True

# --- 2. BASE DE DATOS ---
def conectar():
    conn = sqlite3.connect("gestion_tienda.db", check_same_thread=False)
    return conn

db = conectar()
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS clientes (nombre TEXT, tel TEXT, email TEXT, direccion TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS categorias (nombre TEXT UNIQUE)")
db.commit()

# --- 3. INTERFAZ ---
if login():
    st.sidebar.title("Menú Principal")
    opcion = st.sidebar.radio("Ir a:", ["Nueva Venta", "Registrar Clientes", "Categorías de Producto"])

    # Inicializar el carrito en la sesión si no existe
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []

    if opcion == "Categorías de Producto":
        st.header("🏷️ Gestión de Categorías")
        nueva_cat = st.text_input("Nombre de la categoría (ej: Vestidos, Blusas...)")
        if st.button("Guardar Categoría"):
            try:
                cursor.execute("INSERT INTO categorias VALUES (?)", (nueva_cat.strip(),))
                db.commit()
                st.success(f"Categoría '{nueva_cat}' añadida.")
            except:
                st.error("Esa categoría ya existe.")
        
        lista_cats = cursor.execute("SELECT nombre FROM categorias").fetchall()
        st.write("Categorías actuales:", [c[0] for c in lista_cats])

    elif opcion == "Registrar Clientes":
        st.header("👥 Registro de Clientes")
        with st.form("form_cliente"):
            nombre = st.text_input("Nombre completo")
            tel = st.text_input("Teléfono (ej: 34600000000)")
            if st.form_submit_button("Registrar Cliente"):
                if nombre and tel:
                    cursor.execute("INSERT INTO clientes VALUES (?,?,?,?)", (nombre, tel, "", ""))
                    db.commit()
                    st.success(f"Cliente {nombre} registrado.")

    elif opcion == "Nueva Venta":
        st.header("💰 Realizar Venta")
        
        clientes_db = cursor.execute("SELECT nombre, tel FROM clientes").fetchall()
        cats_db = cursor.execute("SELECT nombre FROM categorias").fetchall()
        
        if not clientes_db or not cats_db:
            st.warning("⚠️ Registra primero Clientes y Categorías.")
        else:
            dict_clientes = {c[0]: c[1] for c in clientes_db}
            cliente_sel = st.selectbox("Selecciona Cliente", list(dict_clientes.keys()))
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                cat_sel = st.selectbox("Añadir Artículo", [c[0] for c in cats_db])
            with col2:
                precio = st.number_input("Precio (€)", min_value=0.0, step=1.0)
            
            if st.button("➕ Añadir al Carrito"):
                st.session_state.carrito.append({"item": cat_sel, "precio": precio})
                st.toast(f"{cat_sel} añadido")

            # Mostrar el Carrito actual
            if st.session_state.carrito:
                st.subheader("🛒 Resumen de Compra")
                total_venta = 0
                for i, prod in enumerate(st.session_state.carrito):
                    col_a, col_b = st.columns([3, 1])
                    col_a.write(f"• {prod['item']}")
                    col_b.write(f"{prod['precio']}€")
                    total_venta += prod['precio']
                
                st.write(f"### TOTAL: {total_venta}€")

                if st.button("🗑️ Vaciar Carrito"):
                    st.session_state.carrito = []
                    st.rerun()

                if st.button("✅ Generar Ticket Final"):
                    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                    
                    # Construir el listado de productos para el mensaje
                    detalles_productos = ""
                    for p in st.session_state.carrito:
                        detalles_productos += f"- {p['item']}: {p['precio']}€\n"
                    
                    ticket_texto = (
                        f"*ELOÍSA NELEB MODAS*\n"
                        f"------------------------------\n"
                        f"📅 {fecha}\n"
                        f"👤 Cliente: {cliente_sel}\n"
                        f"------------------------------\n"
                        f"{detalles_productos}"
                        f"------------------------------\n"
                        f"💰 *TOTAL: {total_venta}€*\n"
                        f"------------------------------\n"
                        f"¡Gracias por tu compra!"
                    )
                    
                    telefono_cliente = dict_clientes[cliente_sel]
                    mensaje_codificado = urllib.parse.quote(ticket_texto)
                    url_whatsapp = f"https://wa.me/{telefono_cliente}?text={mensaje_codificado}"
                    
                    st.markdown(f'''
                        <a href="{url_whatsapp}" target="_blank">
                            <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; font-size:18px; cursor:pointer;">
                                🟢 ENVIAR TICKET POR WHATSAPP
                            </button>
                        </a>
                    ''', unsafe_allow_html=True)
