import sys
import os
from database import supabase

import streamlit as st
import pandas as pd
from database import supabase # Esto es lo que fallaba

# Configuración de la página
st.set_page_config(page_title="Albion Market Intelligence", layout="wide")

st.title("Albion Market Intelligence Dashboard")

# Botón para refrescar datos
if st.button('Actualizar Datos'):
    try:
        # Traemos los últimos 2000 registros
        response = supabase.table("historial_precios").select("*").order("created_at", desc=True).limit(2000).execute()
        data = response.data
        
        if data:
            df = pd.DataFrame(data)
            
            # --- AQUÍ VA LA FUNCIÓN CLASIFICAR ---
            def clasificar(row):
                p_compra = row['price_buy']
                p_venta = row['price_sell']
                if p_compra <= 0 or p_venta <= 0: return None
                
                profit = (p_compra * 0.935) - p_venta
                roi = (profit / p_venta) * 100
                
                # FILTRO DE PRIVACIDAD: Si es Platino (>50% ROI), no lo mostramos en la web
                if roi > 50 or profit > 250000: 
                    return None 
                
                if roi > 18 or profit > 80000: return "🌟 ORO"
                if roi > 8: return "📢 PUBLICO"
                return "📉 BAJO MARGEN"

            # Aplicamos la clasificación
            df['Clasificacion'] = df.apply(clasificar, axis=1)
            
            # Borramos las filas que son None (los Platinos ocultos)
            df = df.dropna(subset=['Clasificacion'])

            # --- MÉTRICAS ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Registros en Vista", len(df))
            with col2:
                oros = len(df[df['Clasificacion'] == "🌟 ORO"])
                st.metric("Tickets Oro Detectados", oros)
            with col3:
                st.metric("Estado del Sistema", "Online")
                
            # --- TABLA CON ESTILO ---
            st.subheader("Panel de Oportunidades Filtradas")
            
            # Reordenar columnas para limpieza visual
            cols = ['Clasificacion', 'item_id', 'city', 'price_buy', 'price_sell', 'quality', 'created_at']
            df = df[cols]

            # Función para los colores de las etiquetas
            def color_tokens(val):
                if val == "🌟 ORO": color = '#f1c40f'
                elif val == "📢 PUBLICO": color = '#2ecc71'
                else: color = '#95a5a6'
                return f'background-color: {color}; color: black; font-weight: bold'

            # Cambia .applymap por .map
            st.dataframe(df.style.map(color_tokens, subset=['Clasificacion']), use_container_width=True)

            # --- GRÁFICA ---
            st.subheader("Analisis de Precios por Ciudad")
            st.bar_chart(data=df, x='city', y='price_sell')
            
        else:
            st.info("Sin registros nuevos en la base de datos.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")