import httpx
import asyncio
from database import supabase
from bot_control import enviar_alerta_platino

# --- CONFIGURACIÓN DE BÚSQUEDA ---
CIUDADES = "Caerleon,BlackMarket,Bridgewatch,Fort Sterling,Martlock,Thetford,Lymhurst"
# Lista ampliada para analizar miles de combinaciones
ITEMS_BASE = [
    "BAG_INSIGHT", "MOUNT_OX", "CAPE", "BAG", "ARMOR_PLATE_SET1", 
    "BOOTS_PLATE_SET1", "HEAD_PLATE_SET1", "MAIN_CURSEDSTAFF", "MAIN_FIRESTAFF",
    "MAIN_FROSTSTAFF", "MAIN_ARCANESTAFF", "MAIN_NATURESTAFF", "MAIN_HOLYSTAFF"
]
TIERS = ["T4", "T5", "T6", "T7", "T8"]
ENCANTAMIENTOS = ["", "@1", "@2", "@3"]
CALIDADES = "1,2,3,4,5"

# --- VISTA DE ADMIN ---
USUARIO_ACTUAL = "admin_juanma"
LISTA_AUTORIZADOS = ["admin_juanma", "admin"]

def analizar_y_clasificar(datos, user_id):
    print(f"\n{'='*25} REPORTE DE OPORTUNIDADES {'='*25}")
    encontrado = False

    for r in datos:
        item = r['item_id']
        p_compra = r['buy_price_max']
        p_venta = r['sell_price_min']
        ciudad = r['city']
        calidad = r['quality']

        if p_venta <= 0 or p_compra <= 0: continue

        profit_pre = (p_compra * 0.935) - p_venta 
        roi = (profit_pre / p_venta) * 100 if p_venta > 0 else 0

        # --- JERARQUÍA DE TICKETS ---
        es_platino = roi > 50 or profit_pre > 250000
        es_oro = (roi > 18 or profit_pre > 80000) and not es_platino
        es_publico = roi > 8 and not es_oro and not es_platino

        ticket_msg = f"📍 {ciudad.ljust(12)} | {item.ljust(20)} | Q:{calidad} | Profit: +{int(profit_pre):,} ({int(roi)}% ROI)"

        if es_platino:
            encontrado = True
            print(f"💎 [PLATINO] {ticket_msg}")
            # Esta línea manda la info al bot de forma asíncrona
            asyncio.create_task(enviar_alerta_platino({
                'item_id': item,
                'city': ciudad,
                'profit': int(profit_pre)
            }))
        
        elif es_oro:
            encontrado = True
            if user_id in LISTA_AUTORIZADOS:
                print(f"🌟 [ORO] {ticket_msg}")
            else:
                print(f"🔒 [ORO] Oportunidad oculta en {ciudad}...")
        
        elif es_publico:
            encontrado = True
            print(f"📢 [PÚBLICO] {ticket_msg}")

    if not encontrado:
        print("❌ No se encontraron oportunidades que superen el margen en este escaneo.")

def generar_lotes(lista, n):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]

async def escanear_lote(client, lote_items):
    items_str = ",".join(lote_items)
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{items_str}?locations={CIUDADES}&qualities={CALIDADES}"
    try:
        response = await client.get(url, timeout=15.0)
        return response.json()
    except Exception:
        return []

async def ejecutar_escaneo_total():
    items_completos = [f"{t}_{i}{e}" for t in TIERS for i in ITEMS_BASE for e in ENCANTAMIENTOS]
    lotes = list(generar_lotes(items_completos, 50))
    
    print(f"🚀 Iniciando escaneo masivo de {len(items_completos)} combinaciones...")
    
    async with httpx.AsyncClient() as client:
        tareas = [escanear_lote(client, lote) for lote in lotes]
        resultados = await asyncio.gather(*tareas)
        
        todos_los_datos = [reg for sublista in resultados for reg in sublista if reg['sell_price_min'] > 0]
        
        if todos_los_datos:
            bulk_data = [
                {
                    "item_id": r['item_id'],
                    "city": r['city'],
                    "price_sell": r['sell_price_min'],
                    "price_buy": r['buy_price_max'],
                    "quality": r['quality']
                } for r in todos_los_datos
            ]
            
            try:
                supabase.table("historial_precios").insert(bulk_data).execute()
                print(f"✅ Éxito: {len(bulk_data)} registros guardados en Supabase.")
            except Exception as e:
                print(f"⚠️ Error Supabase: {e}")
            
            analizar_y_clasificar(todos_los_datos, USUARIO_ACTUAL)

import time

def ejecutar_escaneo():
    while True:
        print(f"\n🚀 [{time.strftime('%H:%M:%S')}] Iniciando nueva ronda de escaneo...")
        try:
            # Aquí va tu lógica actual de buscar precios y filtrar
            # ... (el código que ya tienes que llama al API) ...
            
            print(f"✅ Ronda finalizada. Esperando 60 segundos para refrescar datos...")
        except Exception as e:
            print(f"❌ Error inesperado: {e}. Reintentando en 10 segundos...")
            time.sleep(10)
            continue
            
        time.sleep(60) # El descanso ideal para no saturar el API
import time
# ... tus otros imports ...

def ejecutar_recoleccion():
    print("Iniciando escaneo de mercado...")
    # Aquí va tu lógica actual de buscar precios y subirlos a Supabase
    # ...
    print("Escaneo finalizado. Esperando 15 minutos...")

if __name__ == "__main__":
    while True:
        try:
            ejecutar_recoleccion()
        except Exception as e:
            print(f"Ocurrió un error: {e}")
        
        # Espera 15 minutos (900 segundos) antes de volver a empezar
        time.sleep(900)

if __name__ == "__main__":
    ejecutar_escaneo()