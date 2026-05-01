import streamlit as st
import pandas as pd
from database import supabase

st.set_page_config(page_title="Albion Intelligence", layout="wide")

# Estilo para mejorar la visibilidad de la tabla de seguimiento
st.markdown("""
    <style>
    .stButton button { width: 100%; border-radius: 5px; }
    .fijado-container { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. MOTOR DE NOMENCLATURA ---
TIERS_OFICIALES = {
    "T3": "del Neófito", "T4": "del Adepto", "T5": "del Experto",
    "T6": "del Maestro", "T7": "del Gran Maestro", "T8": "del Anciano"
}

TRADUCCION_BASE = {
    "MOUNT_OX": "Buey de transporte",
    "CLOAK_UNDEAD": "Capa de Undead",
    "BAG": "Bolso",
    "TORCH": "Antorcha",
    "SHIELD": "Escudo",
    "MERCENARY_JACKET": "Chaqueta de mercenario"
}

def formatear_a_español(item_id):
    partes = item_id.split('@')[0].split('_')
    t_key = partes[0]
    item_key = "_".join(partes[1:])
    
    nombre_base = TRADUCCION_BASE.get(item_key, item_key.replace("_", " ").title())
    sufijo = TIERS_OFICIALES.get(t_key, t_key)
    
    return f"{nombre_base} {sufijo}"

# --- 2. INTERFAZ DE FILTROS ---
st.title("Albion Intelligence Dashboard")

c1, c2, c3, c4 = st.columns(4)
with c1:
    busqueda = st.text_input("Buscar Objeto", placeholder="Ej: Escudo...")
with c2:
    tier_filtro = st.selectbox("Nivel", ["Todos", "T3", "T4", "T5", "T6", "T7", "T8"])
with c3:
    encantamiento_filtro = st.selectbox("Encantamiento", ["Todos", "0", "1", "2", "3", "4"])
with c4:
    ciudad_filtro = st.multiselect("Ciudad", ["Lymhurst", "Martlock", "Bridgewatch", "Fort Sterling", "Thetford", "Caerleon", "Black Market"])

# --- 3. CARGA DE DATOS ---
try:
    # Consulta optimizada a historial_precios
    query = supabase.table("historial_precios").select("*").order("created_at", desc=True).limit(500)
    response = query.execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        df['Objeto'] = df['item_id'].apply(formatear_a_español)
        df['Enc.'] = df['item_id'].apply(lambda x: x.split('@')[1] if '@' in x else "0")
        df['Precio Compra'] = df['price_buy']
        df['Precio Venta'] = df['price_sell']

        # Filtros
        if busqueda:
            df = df[df['Objeto'].str.contains(busqueda, case=False)]
        if tier_filtro != "Todos":
            df = df[df['item_id'].str.startswith(tier_filtro)]
        if encantamiento_filtro != "Todos":
            df = df[df['Enc.'] == encantamiento_filtro]
        if ciudad_filtro:
            df = df[df['city'].isin(ciudad_filtro)]

        # --- 4. TABLA PRINCIPAL (FIX) ---
        st.subheader("Mercado")
        df['Fix'] = False
        
        columnas_visibles = ['Fix', 'Objeto', 'Enc.', 'city', 'Precio Compra', 'Precio Venta']
        
        res_editor = st.data_editor(
            df[columnas_visibles],
            column_config={
                "Fix": st.column_config.CheckboxColumn("Fix", default=False),
                "Precio Compra": st.column_config.NumberColumn(format="%d"),
                "Precio Venta": st.column_config.NumberColumn(format="%d")
            },
            disabled=['Objeto', 'Enc.', 'city', 'Precio Compra', 'Precio Venta'],
            hide_index=True,
            use_container_width=True,
            key="editor_principal"
        )

        # --- 5. LISTA DE SEGUIMIENTO CON COPIADO RÁPIDO ---
        fijados = res_editor[res_editor['Fix'] == True]
        
        if not fijados.empty:
            st.markdown("---")
            st.subheader("Mi Lista de Seguimiento Fijo (Acción Rápida)")
            
            # Creamos una fila por cada ítem fijado con un botón de copiar
            for index, row in fijados.iterrows():
                with st.container():
                    col_nom, col_det, col_copy = st.columns([3, 2, 1])
                    with col_nom:
                        st.markdown(f"**{row['Objeto']}**")
                    with col_det:
                        st.write(f"{row['city']} | Compra: {row['Precio Compra']:,}")
                    with col_copy:
                        # BOTÓN DE COPIAR AL PORTAPAPELES
                        if st.button(f"Copiar", key=f"btn_{index}"):
                            st.copy_to_clipboard(row['Objeto'])
                            st.toast(f"Copiado: {row['Objeto']}")
            
            st.info("Haz clic en 'Copiar' y pega el nombre directamente en el buscador de Albion.")

    else:
        st.warning("No hay datos en la tabla historial_precios.")

except Exception as e:
    st.error(f"Error: {e}")

if st.button("Actualizar"):
    st.rerun()