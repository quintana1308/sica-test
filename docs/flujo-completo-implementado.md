# FLUJO COMPLETO IMPLEMENTADO - SICA Bot

## 📋 Resumen del Proceso

El bot SICA ahora implementa un flujo completo de automatización para el registro de órdenes de despacho:

```
Login → Buscar Empresa → Seleccionar Empresa → Buscar Conductor → Seleccionar Conductor → Buscar Vehículo
```

## 🔄 Pasos Implementados

### 1. **Proceso de Login**
- ✅ Obtener página de login y token CSRF
- ✅ Realizar login con credenciales
- ✅ Extraer código de verificación
- ✅ Verificar dispositivo
- ✅ Obtener tokens del dashboard

### 2. **Búsqueda y Selección de Empresa**
- ✅ Input de código de empresa por consola
- ✅ Request de búsqueda con payload exacto
- ✅ Mostrar resultados encontrados
- ✅ Selección automática de empresa
- ✅ Guardado de datos en `empresa_seleccionada.json`

### 3. **Búsqueda y Selección de Conductor**
- ✅ Validación de empresa previamente seleccionada
- ✅ Input de cédula de conductor por consola
- ✅ Request de búsqueda con serverMemo actualizado
- ✅ Mostrar información del conductor encontrado
- ✅ Confirmación de selección por usuario
- ✅ Request de selección con payload exacto
- ✅ Guardado de datos en `conductor_seleccionado.json`

### 4. **Búsqueda de Vehículo** ⭐ **NUEVO**
- ✅ Validación de empresa y conductor previamente seleccionados
- ✅ Input de placa de vehículo por consola
- ✅ Request de búsqueda con payload exacto según documento
- ✅ Mostrar información del vehículo encontrado
- ✅ Guardado de datos en `vehiculo_encontrado.json`

## 📦 Requests Implementados

### Búsqueda de Vehículo (Nuevo)
```json
{
  "fingerprint": {
    "id": "KHVqzUwh2XF4DDsfeoZ6",
    "name": "eyJpdiI6IndjOStsenMwMUk1OFZ0YWtYd1JIakE9PSIs...",
    "locale": "es",
    "path": "despachos/registrar",
    "method": "GET",
    "v": "acj"
  },
  "serverMemo": {
    "children": {...},
    "errors": [],
    "htmlHash": "874c826e",
    "data": {
      "data": {...},
      "empresas": [...],
      "conductores": [...],
      "vehiculos": false,
      "rubros_": [],
      "anios_cuspal": [...],
      "meses_cuspal": [...]
    },
    "dataMeta": [],
    "checksum": "037101aa56ea3cff5e7d5be07211c032e62a96ab16c0f044492bbb40d1ab1026"
  },
  "updates": [
    {
      "type": "syncInput",
      "payload": {
        "id": "yd3m",
        "name": "data.bTBZOW5WRVUrRGdVZ1JlM05EQ1lsQT09",
        "value": "A22AK2C"
      }
    },
    {
      "type": "callMethod",
      "payload": {
        "id": "ty24",
        "method": "searchVehiculoPlaca",
        "params": []
      }
    }
  ]
}
```

## 🔧 Características Técnicas

### Manejo de Datos Dinámicos
- **Empresa**: Recupera datos de archivo o contexto actual
- **Conductor**: Mantiene información de selección previa
- **Vehículo**: Usa serverMemo actualizado con todos los pasos anteriores

### Validaciones Implementadas
- **Código de empresa**: Formato numérico 1-8 dígitos
- **Cédula de conductor**: Formato V-12345678 o similar
- **Placa de vehículo**: Formato alfanumérico 6-9 caracteres

### Logs y Debugging
- Logs detallados en cada paso
- Guardado de respuestas en archivos JSON
- Guardado de errores en archivos HTML
- Checksums y validaciones de integridad

## 📁 Archivos Generados

- `despachos_response.json` - Respuesta inicial del sistema
- `empresa_encontrada.json` - Resultado de búsqueda de empresa
- `empresa_seleccionada.json` - Empresa seleccionada completa
- `busqueda_conductor_request.json` - Request de búsqueda de conductor
- `conductor_encontrado.json` - Resultado de búsqueda de conductor
- `seleccion_conductor_response.json` - Respuesta de selección
- `conductor_seleccionado.json` - Conductor seleccionado completo
- `busqueda_vehiculo_response.json` - Respuesta de búsqueda de vehículo ⭐
- `vehiculo_encontrado.json` - Vehículo encontrado completo ⭐
- `payload_busqueda_vehiculo.json` - Payload de referencia ⭐

## 🎯 Estado Actual

El bot puede ejecutar completamente el flujo:

1. **Login automático** ✅
2. **Búsqueda de empresa por código** ✅
3. **Selección automática de empresa** ✅
4. **Búsqueda de conductor por cédula** ✅
5. **Selección de conductor con confirmación** ✅
6. **Búsqueda de vehículo por placa** ✅ **NUEVO**

## 🚀 Próximos Pasos Sugeridos

- Implementar selección de vehículo (si es necesaria)
- Agregar proceso de rubros
- Implementar generación de guía final
- Optimizar manejo de errores y reintentos

## 💡 Notas Técnicas

- Todos los requests replican exactamente los payloads documentados
- Se mantiene compatibilidad con datos dinámicos
- El sistema es robusto ante errores de red o servidor
- Los logs permiten debugging detallado de cualquier paso

---

**Última actualización**: 04 Sep 2025 - Implementación de búsqueda de vehículo completada
