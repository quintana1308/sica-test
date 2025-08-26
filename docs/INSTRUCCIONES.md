# 🚀 Instrucciones para Ejecutar SICA Bot en Entorno Virtual

## 📋 Requisitos Previos
- Python 3.7 o superior
- Acceso a terminal/línea de comandos
- Conexión a internet

## 🔧 Opción 1: Instalación Automática (Recomendada)

### Ejecutar Script de Configuración
```bash
# Dar permisos de ejecución al script
chmod +x setup.sh

# Ejecutar configuración automática
bash setup.sh
```

El script automáticamente:
- ✅ Verifica Python3
- ✅ Crea el entorno virtual
- ✅ Instala todas las dependencias
- ✅ Te pregunta si quieres ejecutar el bot

## 🔧 Opción 2: Instalación Manual

### Paso 1: Crear Entorno Virtual
```bash
# Crear entorno virtual llamado 'venv'
python3 -m venv venv
```

### Paso 2: Activar Entorno Virtual
```bash
# En macOS/Linux
source venv/bin/activate

# En Windows
venv\Scripts\activate
```

Verás que el prompt cambia a algo como: `(venv) usuario@mac:`

### Paso 3: Actualizar pip
```bash
pip install --upgrade pip
```

### Paso 4: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 5: Ejecutar el Bot
```bash
python3 sica_bot.py
```

## 🎯 Uso Diario

### Para usar el bot después de la instalación:

1. **Activar entorno virtual**:
   ```bash
   source venv/bin/activate
   ```

2. **Ejecutar el bot**:
   ```bash
   python3 sica_bot.py
   ```

3. **Desactivar entorno** (cuando termines):
   ```bash
   deactivate
   ```

## 📝 Ejemplo de Sesión Completa

```bash
# Navegar al directorio del proyecto
cd /Users/aleguizamon/Sites/ADN/windsurf/adn-sica-bot-test

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el bot
python3 sica_bot.py

# El bot te pedirá credenciales:
# 👤 Usuario: tu_usuario
# 🔒 Contraseña: tu_contraseña

# Desactivar cuando termines
deactivate
```

## 🛠️ Comandos Útiles

### Verificar Instalación
```bash
# Verificar Python
python3 --version

# Verificar pip (con entorno activado)
pip list

# Verificar dependencias específicas
pip show requests beautifulsoup4
```

### Reinstalar Dependencias
```bash
# Si hay problemas, reinstalar todo
pip install --force-reinstall -r requirements.txt
```

### Limpiar y Recrear Entorno
```bash
# Eliminar entorno actual
rm -rf venv

# Crear nuevo entorno
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🐛 Solución de Problemas

### Error: "python3: command not found"
```bash
# Instalar Python3 en macOS
brew install python3

# O usar el instalador oficial de python.org
```

### Error: "No module named 'venv'"
```bash
# En algunos sistemas necesitas instalar venv
sudo apt-get install python3-venv  # Ubuntu/Debian
```

### Error: "Permission denied"
```bash
# Dar permisos al script
chmod +x setup.sh
```

### Error de Conexión SSL
```bash
# Actualizar certificados
pip install --upgrade certifi
```

## 📊 Estructura de Archivos

```
adn-sica-bot-test/
├── venv/                    # Entorno virtual (se crea automáticamente)
├── sica_bot.py             # Bot principal
├── requirements.txt        # Dependencias
├── setup.sh               # Script de instalación
├── ejemplo_uso.py         # Ejemplos de uso
├── README.md              # Documentación
├── INSTRUCCIONES.md       # Este archivo
└── despachos_response.json # Respuesta guardada (se crea al ejecutar)
```

## ⚠️ Notas Importantes

1. **Siempre activar el entorno virtual** antes de ejecutar el bot
2. **No commitear la carpeta venv** al control de versiones
3. **Mantener actualizadas las dependencias** regularmente
4. **Usar credenciales reales** del sistema SICA

## 🔒 Seguridad

- **No hardcodees credenciales** en el código
- **Usa variables de entorno** para datos sensibles:
  ```bash
  export SICA_USER="tu_usuario"
  export SICA_PASS="tu_contraseña"
  ```
- **El bot maneja automáticamente** cookies y tokens

## 📞 Soporte

Si tienes problemas:
1. Verifica que el entorno virtual esté activado
2. Revisa que todas las dependencias estén instaladas
3. Comprueba la conectividad a internet
4. Verifica las credenciales del sistema SICA
