import streamlit as st
import pandas as pd
from database import supabase

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="Albion Intelligence", layout="wide")

st.title("Albion Intelligence Dashboard")

# --- 1. BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Mercado")
busqueda = st.sidebar.text_input("Barra de busqueda (Nombre o ID)", "")
ciudad_filtro = st.sidebar.multiselect("Filtrar por Ciudad", 
                                     ["Lymhurst", "Martlock", "Bridgewatch", "Fort Sterling", "Thetford", "Caerleon", "Black Market"])

# --- 2. FUNCION PARA TRADUCIR Y LIMPIAR ---
def mejorar_datos(df):
    traducciones = {
        "CLOAK": "Capa", "BAG": "Bolso", "CAPE": "Capa", "HEAD": "Casco",
        "PLATE": "Placa", "LEATHER": "Cuero", "CLOTH": "Tela", "UNDEAD": "Undead"
    }
    
    def traducir(item_id):
        nombre = item_id.split('@')[0]
        for eng, esp in traducciones.items():
            nombre = nombre.replace(eng, esp)
        return nombre.replace("_", " ")

    df['Nombre ESP'] = df['item_id'].apply(traducir)
    df['Encantamiento'] = df['item_id'].apply(lambda x: x.split('@')[1] if '@' in x else "0")
    
    # Formatear precios con comas
    df['Precio Compra'] = df['price_buy'].map('{:,}'.format)
    df['Precio Venta'] = df['price_sell'].map('{:,}'.format)
    
    return df

# --- 3. CARGA DE DATOS ---
try:
    # REEMPLAZA "precios_albion" por el nombre real de tu tabla en Supabase
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

        # --- 4. TABLA PRINCIPAL ---
        st.subheader("Datos Totales del Mercado")
        
        cols_principales = ['Nombre ESP', 'Encantamiento', 'city', 'Precio Compra', 'Precio Venta', 'quality']
        
        seleccionados = st.multiselect("Selecciona items para tu lista de observacion fija:", 
                                      df['Nombre ESP'].unique(), key="selector")

        st.dataframe(df[cols_principales], use_container_width=True)

        # --- 5. PESTAÑA EMERGENTE (PREMIUM) ---
        with st.expander("VER CLASIFICACION (Solo Usuarios Premium)"):
            st.info("Esta seccion contiene la inteligencia de margenes y oportunidades.")
            st.dataframe(df[['Nombre ESP', 'Clasificacion', 'city']], use_container_width=True)

        # --- 6. TABLA DE SELECCIONADOS ---
        if seleccionados:
            st.markdown("---")
            st.subheader("Mi Lista de Seguimiento Fijo")
            df_fijo = df[df['Nombre ESP'].isin(seleccionados)]
            st.dataframe(df_fijo[cols_principales], use_container_width=True)

    else:
        st.warning("No hay datos disponibles en la base de datos.")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")

if st.button("Actualizar Dashboard"):
    st.rerun()