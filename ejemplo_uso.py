#!/usr/bin/env python3
"""
Ejemplo de uso del SICA Bot
Script simplificado para probar el bot
"""

from sica_bot import SICABot
import json

def ejemplo_basico():
    """Ejemplo básico de uso"""
    print("🤖 Ejemplo de uso del SICA Bot")
    print("-" * 40)
    
    # Crear instancia
    bot = SICABot()
    
    # Credenciales de prueba (cambiar por las reales)
    username = "tu_usuario"
    password = "tu_contraseña"
    
    # Login completo
    tokens = bot.full_login_process(username, password)
    
    if tokens:
        print("✅ Login exitoso!")
        
        # Obtener datos de despachos
        data = bot.get_despachos_data()
        
        if data:
            print("📊 Datos obtenidos:")
            print(f"HTML Length: {len(data.get('effects', {}).get('html', ''))}")
            print(f"Server Memo: {data.get('serverMemo', {}).get('data', {})}")
        
    else:
        print("❌ Error en login")

def ejemplo_solo_request():
    """Ejemplo para hacer solo el request si ya tienes las cookies"""
    print("🔄 Ejemplo de request directo")
    
    bot = SICABot()
    
    # Si ya tienes las cookies, puedes setearlas manualmente:
    # bot.session.cookies.update({
    #     '3c234b41a96dc1291ad149e71734eba388a31a59': 'valor_cookie',
    #     'XSRF-TOKEN': 'valor_token',
    #     # ... otras cookies
    # })
    
    # Y hacer el request directamente
    # data = bot.get_despachos_data()

if __name__ == "__main__":
    ejemplo_basico()
