# 🤖 SICA Bot - Automatización de Login y Requests

Bot en Python para automatizar el proceso completo de login al sistema SICA (sica.sunagro.gob.ve), incluyendo la verificación de dispositivo y posterior acceso a los datos.

## 🚀 Características

- ✅ **Login automático** con usuario y contraseña
- ✅ **Extracción automática** del código de verificación de dispositivo
- ✅ **Verificación automática** del dispositivo
- ✅ **Gestión de cookies y tokens** CSRF
- ✅ **Requests autenticados** usando Livewire
- ✅ **Manejo de errores** y logging detallado

## 📋 Requisitos

- Python 3.7+
- Dependencias listadas en `requirements.txt`

## 🔧 Instalación

1. **Clonar o descargar** los archivos del proyecto
2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Uso

### Uso Básico

```python
from sica_bot import SICABot

# Crear instancia del bot
bot = SICABot()

# Realizar login completo
tokens = bot.full_login_process("tu_usuario", "tu_contraseña")

if tokens:
    # Obtener datos de despachos
    data = bot.get_despachos_data()
    print("Datos obtenidos:", data)
```

### Ejecutar el Script Principal

```bash
python sica_bot.py
```

El script te pedirá usuario y contraseña, y realizará todo el proceso automáticamente.

## 🔄 Proceso Automático

El bot realiza los siguientes pasos automáticamente:

1. **🔍 Obtiene la página de login** y extrae el token CSRF
2. **🔐 Realiza el login** con las credenciales proporcionadas
3. **📱 Extrae el código de verificación** del HTML de la página de dispositivo
4. **✅ Verifica el dispositivo** usando el código extraído
5. **🎯 Obtiene los tokens** necesarios para requests autenticados
6. **📊 Realiza requests** al sistema usando Livewire

## 📁 Archivos del Proyecto

- `sica_bot.py` - Clase principal del bot
- `ejemplo_uso.py` - Ejemplos de uso
- `requirements.txt` - Dependencias de Python
- `README.md` - Este archivo

## 🔧 Configuración Avanzada

### Personalizar Headers

```python
bot = SICABot()
bot.session.headers.update({
    'User-Agent': 'Tu User Agent personalizado'
})
```

### Usar Cookies Existentes

```python
bot = SICABot()
bot.session.cookies.update({
    '3c234b41a96dc1291ad149e71734eba388a31a59': 'valor_cookie',
    'XSRF-TOKEN': 'valor_token'
})
```

## 🛠️ Métodos Principales

### `SICABot.full_login_process(username, password)`
Realiza todo el proceso de login automáticamente.

**Parámetros:**
- `username` (str): Usuario del sistema SICA
- `password` (str): Contraseña del usuario

**Retorna:**
- `dict` con tokens y cookies si es exitoso
- `False` si hay error

### `SICABot.get_despachos_data()`
Obtiene los datos de despachos usando el request de Livewire.

**Retorna:**
- `dict` con la respuesta JSON del servidor
- `None` si hay error

### `SICABot.make_livewire_request(component_name, method_params)`
Realiza un request personalizado de Livewire.

**Parámetros:**
- `component_name` (str): Nombre encriptado del componente
- `method_params` (str): Parámetros del método a ejecutar

## 🔍 Debugging

El bot incluye logging detallado. Cada paso muestra:
- ✅ Éxito con detalles
- ❌ Errores con descripción
- 🔄 Progreso de cada paso

## ⚠️ Consideraciones de Seguridad

- **No hardcodees credenciales** en el código
- **Las cookies expiran** - el bot maneja esto automáticamente
- **El código de verificación es dinámico** - se extrae automáticamente
- **Respeta los rate limits** del servidor

## 🐛 Solución de Problemas

### Error: "No se pudo obtener el token CSRF"
- Verifica que el sitio esté accesible
- Revisa la conectividad de red

### Error: "Login falló"
- Verifica las credenciales
- Asegúrate de que la cuenta esté activa

### Error: "No se pudo extraer el código de verificación"
- El formato del código puede haber cambiado
- Revisa el HTML de la página de verificación

## 📝 Ejemplo Completo

```python
#!/usr/bin/env python3
from sica_bot import SICABot
import json

def main():
    # Crear bot
    bot = SICABot()
    
    # Login
    tokens = bot.full_login_process("usuario", "contraseña")
    
    if tokens:
        print("Login exitoso!")
        
        # Obtener datos
        data = bot.get_despachos_data()
        
        # Guardar en archivo
        with open('datos.json', 'w') as f:
            json.dump(data, f, indent=2)
            
        print("Datos guardados en datos.json")
    else:
        print("Error en login")

if __name__ == "__main__":
    main()
```

## 📞 Soporte

Para reportar bugs o solicitar funcionalidades, crea un issue en el repositorio del proyecto.

---

**⚠️ Disclaimer:** Este bot es para fines educativos y de automatización legítima. Úsalo responsablemente y respeta los términos de servicio del sistema SICA.
