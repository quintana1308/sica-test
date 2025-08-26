#!/usr/bin/env python3
"""
Script de prueba simple para verificar la búsqueda de empresa
"""

import sys
from sica_bot import SICABot

def test_busqueda_empresa():
    """Probar solo la funcionalidad de búsqueda de empresa"""
    
    print("🚀 Iniciando prueba de búsqueda de empresa...")
    
    # Crear instancia del bot
    bot = SICABot()
    
    # Solicitar credenciales
    print("\n📝 Ingresa tus credenciales de SICA:")
    username = input("Usuario: ")
    password = input("Contraseña: ")
    
    try:
        # 1. Login
        print("\n🔐 Realizando login...")
        if not bot.login(username, password):
            print("❌ Error en el login")
            return False
        
        # 2. Navegar a despachos
        print("\n🧭 Navegando a despachos/registrar...")
        if not bot.navigate_to_despachos_registrar():
            print("❌ Error navegando a despachos")
            return False
        
        # 3. Buscar empresa
        print("\n🔍 Buscando empresa...")
        codigo_empresa = input("Ingresa el código de la empresa a buscar: ")
        
        empresa = bot.search_empresa_by_codigo_interactive(codigo_empresa)
        if empresa:
            print("✅ ¡Búsqueda completada exitosamente!")
            print(f"📋 Empresa encontrada: {empresa.get('razon_social', 'N/A')}")
            return True
        else:
            print("❌ No se encontró empresa")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ Prueba cancelada por el usuario")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_busqueda_empresa()
    if success:
        print("\n🎉 Prueba de búsqueda completada exitosamente")
        sys.exit(0)
    else:
        print("\n💥 Prueba de búsqueda falló")
        sys.exit(1)
