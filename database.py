import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
# --- CONEXIÓN SUPABASE ---
# Intentamos sacar de secrets (Nube), si no existe, usamos un string vacío o lo que tengas en .env
url = st.secrets.get("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY")

if not url or not key:
    # Esto es solo por si lo corres local en tu PC y usas un archivo .env
    import os
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# --- CONFIGURACIÓN DISCORD ---
DISCORD_TOKEN = st.secrets.get("DISCORD_TOKEN")
DISCORD_CLIENT_ID = st.secrets.get("DISCORD_CLIENT_ID")


load_dotenv()

# Configuración de las credenciales
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
# ... después de las líneas de os.environ.get ...
print(f"DEBUG: URL cargada es: {url}")
print(f"DEBUG: KEY cargada es: {key[:10]}...") # Solo mostramos el inicio por seguridad
# Creamos el cliente de conexión
supabase: Client = create_client(url, key)

# --- PRUEBA DE CONEXIÓN ---
if __name__ == "__main__":
    try:
        # Intentamos leer la tabla de usuarios que creamos
        response = supabase.table("usuarios").select("*").execute()
        print("✅ ¡Conexión exitosa con Albion Market Intelligence!")
        print("La base de datos respondió correctamente.")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        # Añade esto a tu connection.py actual
