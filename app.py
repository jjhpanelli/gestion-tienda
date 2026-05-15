import streamlit as st
import json
import os

# Configuración de la página
st.set_page_config(page_title="Gestión Eloísa Neleb", page_icon="🛍️", layout="centered")

# Inicializar bases de datos en la sesión
if 'categorias' not in st.session_state:
    st.session_state.categorias = ["Vestidos", "Pantalones", "Camisas"]

if 'clientes' not in st.session_state:
    st.session_state.clientes = []

# Sistema de seguridad simple
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Acceso Socios - Eloísa Neleb")
    clave = st.text_input("Introduce la contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "Eloisa2026":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
else:
    # Menú lateral
    st.sidebar.title("Menú Principal")
    opcion = st.sidebar.radio("Ir a:", ["Nueva Venta", "Registrar Clientes", "Categorías de Producto"])

    # 1. NUEVA VENTA
    if opcion == "Nueva Venta":
        st.title("🛍️ Nueva Venta")
        
        if not st.session_state.clientes:
            st.warning("Primero debes registrar al menos un cliente.")
        elif not st.session_state.categorias:
            st.warning("Primero debes tener al menos una categoría de producto.")
        else:
            # Seleccionar cliente
            nombres_clientes = [c['nombre'] for c in st.session_state.clientes]
            cliente_sel = st.selectbox("Selecciona el Cliente:", nombres_clientes)
            
            st.write("---")
            st.subheader("Prendas de la venta:")
            
            # Formulario dinámico simplificado para precios
            precios_venta = {}
            for cat in st.session_state.categorias:
                precio = st.number_input(f"Precio para {cat} (€):", min_value=0.0, value=0.0, step=0.5, key=f"venta_{cat}")
                if precio > 0:
                    precios_venta[cat] = precio
            
            st.write("---")
            
            if st.button("Generar Ticket para WhatsApp"):
                if not precios_venta:
                    st.error("Debes poner el precio de al menos una prenda.")
                else:
                    total = sum(precios_venta.values())
                    
                    # Construcción del texto del ticket
                    texto_ticket = f"*ELOÍSA NELEB MODAS*\n"
                    texto_ticket += f"-----------------------------------\n"
                    texto_ticket += f"🔸 Cliente: {cliente_sel.title()}\n"
                    texto_ticket += f"-----------------------------------\n"
                    for cat, pre in precios_venta.items():
                        texto_ticket += f"• {cat}: {pre}€\n"
                    texto_ticket += f"-----------------------------------\n"
                    texto_ticket += f"💰 *TOTAL: {total}€*\n"
                    texto_ticket += f"-----------------------------------\n"
                    texto_ticket += f"¡Gracias por tu compra! ✨"
                    
                    # Guardar en sesión para mostrarlo
                    st.session_state.ticket_generado = texto_ticket
            
            # Mostrar ticket si existe
            if 'ticket_generado' in st.session_state:
                st.subheader("Ticket listo:")
                st.text_area("", value=st.session_state.ticket_generado, height=250)
                st.info("Copia el texto de arriba y pégalo en el WhatsApp de tu cliente.")

    # 2. REGISTRAR CLIENTES
    elif opcion == "Registrar Clientes":
        st.title("👥 Gestión de Clientes")
        
        # Añadir Cliente
        with st.form("nuevo_cliente"):
            st.subheader("Añadir Nuevo Cliente")
            nombre = st.text_input("Nombre completo del cliente:")
            telefono = st.text_input("Teléfono (Opcional):")
            if st.form_submit_button("Guardar Cliente"):
                if nombre.strip() == "":
                    st.error("El nombre no puede estar vacío.")
                else:
                    st.session_state.clientes.append({"nombre": nombre.strip(), "telefono": telefono.strip()})
                    st.success(f"Cliente '{nombre}' guardado con éxito.")
                    st.rerun()
        
        # Eliminar Cliente (NUEVO)
        if st.session_state.clientes:
            st.write("---")
            st.subheader("🗑️ Eliminar un Cliente")
            nombres_clientes = [c['nombre'] for c in st.session_state.clientes]
            cliente_a_borrar = st.selectbox("Selecciona el cliente que deseas quitar:", nombres_clientes, key="borrar_cli")
            if st.button("Eliminar Cliente Seleccionado", type="primary"):
                st.session_state.clientes = [c for c in st.session_state.clientes if c['nombre'] != cliente_a_borrar]
                st.success(f"Cliente '{cliente_a_borrar}' eliminado.")
                st.rerun()

    # 3. CATEGORÍAS DE PRODUCTO
    elif opcion == "Categorías de Producto":
        st.title("🏷️ Gestión de Categorías")
        
        # Añadir Categoría
        nombre_cat = st.text_input("Nombre de la nueva categoría (ej: Vestidos, Blusas...):")
        if st.button("Guardar Categoría"):
            if nombre_cat.strip() == "":
                st.error("El nombre no puede estar vacío.")
            elif nombre_cat.strip().title() in st.session_state.categorias:
                st.error("Esta categoría ya existe.")
            else:
                st.session_state.categorias.append(nombre_cat.strip().title())
                st.success(f"Categoría '{nombre_cat}' añadida.")
                st.rerun()
        
        # Eliminar Categoría (NUEVO)
        if st.session_state.categorias:
            st.write("---")
            st.subheader("🗑️ Eliminar una Categoría")
            cat_a_borrar = st.selectbox("Selecciona la categoría que deseas quitar:", st.session_state.categorias, key="borrar_cat")
            if st.button("Eliminar Categoría Seleccionada", type="primary"):
                st.session_state.categorias.remove(cat_a_borrar)
                st.success(f"Categoría '{cat_a_borrar}' eliminada.")
                st.rerun()
