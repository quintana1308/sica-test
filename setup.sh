#!/bin/bash
# Script de configuración automática para SICA Bot
# Ejecutar con: bash setup.sh

echo "🤖 SICA Bot - Configuración Automática"
echo "======================================"

# Verificar si Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Crear entorno virtual
echo "🔄 Creando entorno virtual..."
python3 -m venv venv

# Verificar si se creó correctamente
if [ ! -d "venv" ]; then
    echo "❌ Error creando el entorno virtual"
    exit 1
fi

echo "✅ Entorno virtual creado"

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "🔄 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "🔄 Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "Para usar el bot:"
echo "1. Activar entorno virtual: source venv/bin/activate"
echo "2. Ejecutar bot: python3 sica_bot.py"
echo "3. Desactivar entorno: deactivate"
echo ""
echo "¿Quieres ejecutar el bot ahora? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🚀 Ejecutando SICA Bot..."
    python3 sica_bot.py
fi
