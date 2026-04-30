from database import supabase

def crear_usuario(username, discord_id, role="member"):
    """Inserta un nuevo usuario en la base de datos"""
    try:
        data = {
            "username": username,
            "discord_id": discord_id,
            "role": role
        }
        # La magia ocurre aquí: insertamos los datos en la tabla
        response = supabase.table("usuarios").insert(data).execute()
        print(f"✅ Usuario '{username}' creado exitosamente.")
        return response
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")

if __name__ == "__main__":
    # --- AQUÍ TE REGISTRAS TÚ ---
    # Cambia estos datos por los tuyos si quieres
    crear_usuario("Beligod_Admin", "Spiller#3849", role="admin")