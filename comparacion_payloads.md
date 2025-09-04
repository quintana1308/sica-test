# COMPARACIÓN DE PAYLOADS - BÚSQUEDA DE VEHÍCULO

## DOCUMENTADO (CORRECTO)
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
    "children": {
      "l2055706833-0": {"id": "xpDRdn5EGdtUFaLbJGFA", "tag": "div"},
      "l2055706833-1": {"id": "twiCOztJPCoLTLCdXZC6", "tag": "div"}
    },
    "errors": [],
    "htmlHash": "874c826e",
    "data": {...},
    "dataMeta": [],
    "checksum": "037101aa56ea3cff5e7d5be07211c032e62a96ab16c0f044492bbb40d1ab1026"
  }
}
```

## GENERADO (INCORRECTO)
```json
{
  "fingerprint": {
    "id": "OVUISGweda7tCFKNw4Gy",  // ❌ DIFERENTE
    "name": "eyJpdiI6InljL3VXMHpSaVE0aTBNL0s5cjNaVGc9PSIs...",  // ❌ DIFERENTE
    "locale": "es",
    "path": "despachos/registrar",
    "method": "GET", 
    "v": "acj"
  },
  "serverMemo": {
    "children": {},  // ❌ VACÍO - DEBERÍA TENER l2055706833-0 y l2055706833-1
    "errors": [],
    "htmlHash": "07279db0",  // ❌ DIFERENTE - DEBERÍA SER "874c826e"
    "data": {...},
    "dataMeta": [],
    "checksum": "ac909ed91ae1d1d8d6d6e2378c73f8950d842209241b2a9ffb049f844a1f46c9"  // ❌ DIFERENTE
  }
}
```

## DIFERENCIAS CRÍTICAS IDENTIFICADAS:

1. **fingerprint.id**: Diferente
2. **fingerprint.name**: Diferente  
3. **serverMemo.children**: Vacío vs con elementos específicos
4. **serverMemo.htmlHash**: "07279db0" vs "874c826e"
5. **serverMemo.checksum**: Completamente diferente

## PROBLEMA RAÍZ:
Estamos usando el component_data actual del flujo, pero necesitamos usar exactamente los mismos valores del documento de referencia para que el servidor reconozca el request como válido.
