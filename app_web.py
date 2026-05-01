import streamlit as st
import pandas as pd
from database import supabase  # Mantenemos tu conexión

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Albion Intelligence", layout="wide")

st.title("🏹 Albion Intelligence Dashboard")

# --- 1. BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros de Mercado")
busqueda = st.sidebar.text_input("Barra de búsqueda (Nombre o ID)", "")
ciudad_filtro = st.sidebar.multiselect("Filtrar por Ciudad", 
                                     ["Lymhurst", "Martlock", "Bridgewatch", "Fort Sterling", "Thetford", "Caerleon", "Black Market"])

# --- 2. FUNCIÓN PARA TRADUCIR Y LIMPIAR (LO QUE PEDISTE) ---
def mejorar_datos(df):
    # Diccionario básico para nombres en español (puedes ampliarlo)
    traducciones = {
        "CLOAK": "Capa", "BAG": "Bolso", "CAPE": "Capa", "HEAD": "Casco",
        "PLATE": "Placa", "LEATHER": "Cuero", "CLOTH": "Tela", "UNDEAD": "Undead"
    }
    
    def traducir(item_id):
        nombre = item_id.split('@')[0] # Quita el @1, @2
        for eng, esp in traducciones.items():
            nombre = nombre.replace(eng, esp)
        return nombre.replace("_", " ")

    df['Nombre ESP'] = df['item_id'].apply(traducir)
    
    # Nivel de encantamiento (Extrae el número después del @)
    df['Encantamiento'] = df['item_id'].apply(lambda x: x.split('@')[1] if '@' in x else "0")
    
    # Formatear precios con comas para legibilidad
    df['Precio Compra'] = df['price_buy'].map('{:,}'.format)
    df['Precio Venta'] = df['price_sell'].map('{:,}'.format)
    
    return df

# --- 3. CARGA DE DATOS ---
try:
    # Traemos los datos de tu Supabase
    response = supabase.table("precios_albion").select("*").execute()
    data = response.data
    df = pd.DataFrame(data)

    if not df.empty:
        df = mejorar_datos(df)

        # Aplicar Filtros
        if busqueda:
            df = df[df['Nombre ESP'].str.contains(busqueda, case=False) | df['item_id'].str.contains(busqueda, case=False)]
        if ciudad_filtro:
            df = df[df['city'].isin(ciudad_filtro)]

        # --- 4. TABLA PRINCIPAL (LEGIBLE) ---
        st.subheader("📊 Datos Totales del Mercado")
        
        # Columnas que pediste (sin la clasificación "fea")
        cols_principales = ['Nombre ESP', 'Encantamiento', 'city', 'Precio Compra', 'Precio Venta', 'quality']
        
        # Checkbox para seleccionar ítems (Lista de Seguimiento)
        # Usamos un truco de Streamlit: multiselect que actúa como "palomita"
        seleccionados = st.multiselect("✅ Selecciona ítems para tu lista de observación fija:", 
                                      df['Nombre ESP'].unique(), key="selector")

        st.dataframe(df[cols_principales], use_container_width=True)

        # --- 5. PESTAÑA EMERGENTE (PREMIUM / CLASIFICACIÓN) ---
        with st.expander("⭐ VER CLASIFICACIÓN (Solo Usuarios Premium)"):
            st.info("Esta sección contiene la inteligencia de márgenes y oportunidades.")
            st.dataframe(df[['Nombre ESP', 'Clasificacion', 'city']], use_container_width=True)

        # --- 6. TABLA DE SELECCIONADOS (ABAJO) ---
        if seleccionados:
            st.divider()
            st.subheader("📌 Mi Lista de Seguimiento Fijo")
            df_fijo = df[df['Nombre ESP'].isin(seleccionados)]
            st.dataframe(df_fijo[cols_principales], use_container_width=True)
            st.caption(f"Estás observando {len(df_fijo)} ítems específicamente.")

    else:
        st.warning("No hay datos nuevos en la base de datos.")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")

# Botón de actualización
if st.button("Actualizar Dashboard"):
    st.rerun()