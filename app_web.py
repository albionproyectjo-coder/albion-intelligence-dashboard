import streamlit as st
import pandas as pd
from database import supabase

st.set_page_config(page_title="Albion Intelligence Pro", layout="wide")

# --- NOMENCLATURA Y TRADUCCION ---
TIERS_OFICIALES = {"T3": "del Neófito", "T4": "del Adepto", "T5": "del Experto", "T6": "del Maestro", "T7": "del Gran Maestro", "T8": "del Anciano"}
TRADUCCION_BASE = {"MOUNT_OX": "Buey de transporte", "CLOAK_UNDEAD": "Capa de Undead", "BAG": "Bolso", "TORCH": "Antorcha", "SHIELD": "Escudo", "MERCENARY_JACKET": "Chaqueta de mercenario"}

def formatear_nombre(item_id):
    partes = item_id.split('@')[0].split('_')
    t_key = partes[0]
    item_key = "_".join(partes[1:])
    nombre = TRADUCCION_BASE.get(item_key, item_key.replace("_", " ").title())
    return f"{nombre} {TIERS_OFICIALES.get(t_key, t_key)}"

# --- INTERFAZ DE FILTROS ---
st.title("Albion Intelligence - Panel de Control")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    busqueda = st.text_input("Buscar Objeto", placeholder="Ej: Buey...")
    ciudad_compra = st.multiselect("Ciudad de Compra", ["Lymhurst", "Martlock", "Bridgewatch", "Fort Sterling", "Thetford", "Caerleon"])
with col_f2:
    tier_f = st.selectbox("Nivel", ["Todos", "T3", "T4", "T5", "T6", "T7", "T8"])
    ciudad_venta = st.multiselect("Ciudad de Venta (Analisis Oro)", ["Black Market", "Caerleon", "Lymhurst", "Martlock", "Bridgewatch", "Fort Sterling", "Thetford"])
with col_f3:
    encant_f = st.selectbox("Encantamiento", ["Todos", "0", "1", "2", "3", "4"])
    tipo_impuesto = st.radio("Tipo de Impuesto de Venta", ["Premium (4%)", "Normal (8%)"], horizontal=True)

tasa = 0.04 if "Premium" in tipo_impuesto else 0.08

# --- CARGA DE DATOS (2000 REGISTROS) ---
try:
    response = supabase.table("historial_precios").select("*").order("created_at", desc=True).limit(2000).execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        df['Objeto'] = df['item_id'].apply(formatear_nombre)
        df['Enc.'] = df['item_id'].apply(lambda x: x.split('@')[1] if '@' in x else "0")
        
        # Filtros Base
        if busqueda: df = df[df['Objeto'].str.contains(busqueda, case=False)]
        if tier_f != "Todos": df = df[df['item_id'].str.startswith(tier_f)]
        if encant_f != "Todos": df = df[df['Enc.'] == encant_f]
        
        # --- TABLA 1: MIEMBROS ACCESO GRATIS ---
        st.header("Precios Miembros Acceso Gratis")
        df_gratis = df.copy()
        if ciudad_compra: df_gratis = df_gratis[df_gratis['city'].isin(ciudad_compra)]
        
        st.dataframe(df_gratis[['Objeto', 'Enc.', 'city', 'price_buy', 'price_sell', 'quality']], 
                     hide_index=True, use_container_width=True)

        # --- TABLA 2: MIEMBROS ORO (INTELIGENCIA) ---
        st.markdown("---")
        st.header("Precios Miembros Oro (Analisis de Margen)")
        
        if not ciudad_venta:
            st.info("Selecciona una 'Ciudad de Venta' para ver el analisis de profit.")
        else:
            # Calculo de Profit: (Precio Venta * (1 - Tasa)) - Precio Compra
            df_oro = df.copy()
            df_oro['Venta Neta'] = df_oro['price_sell'] * (1 - tasa)
            df_oro['Profit Est.'] = df_oro['Venta Neta'] - df_oro['price_buy']
            
            # Filtro por ciudad de venta
            df_oro = df_oro[df_oro['city'].isin(ciudad_venta)]
            
            # Formateo para que sea facil de copiar
            df_oro['Profit Est.'] = df_oro['Profit Est.'].map('{:,.0f}'.format)
            
            st.data_editor(
                df_oro[['Objeto', 'Enc.', 'city', 'price_buy', 'price_sell', 'Profit Est.']],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Objeto": st.column_config.TextColumn("Objeto (Click para copiar)"),
                    "Profit Est.": st.column_config.TextColumn("Profit (Tras Impuestos)")
                }
            )

        # --- SECCION DE COPIADO RAPIDO ---
        st.subheader("Copiado Rapido para Mercado")
        item_para_copiar = st.selectbox("Selecciona objeto para copiar nombre", df['Objeto'].unique())
        st.code(item_para_copiar, language="text")
        st.caption("Copia el texto de arriba y pegalo en el buscador de Albion.")

    else:
        st.warning("No hay datos suficientes.")

except Exception as e:
    st.error(f"Error: {e}")

if st.button("Actualizar Todo"):
    st.rerun()