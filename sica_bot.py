#!/usr/bin/env python3
"""
SICA Bot - Automatización de Login y Requests
Sistema para automatizar el proceso de login, verificación de dispositivo y requests al sistema SICA
"""

import requests
import re
from bs4 import BeautifulSoup
import json
import time
import atexit
from urllib.parse import urljoin

class SICABot:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://sica.sunagro.gob.ve"
        self.csrf_token = None
        self.verification_code = None
        self.logged_in = False
        self.last_search_result = None
        
        # Headers comunes para simular navegador
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-US,es;q=0.9,es-419;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Registrar función de limpieza para logout automático
        atexit.register(self.cleanup)
    
    def get_csrf_token(self, html_content):
        """Extrae el token CSRF del HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        csrf_input = soup.find('input', {'name': '_token'})
        if csrf_input:
            return csrf_input.get('value')
        return None
    
    def get_verification_code(self, html_content):
        """Extrae el código de verificación del HTML"""
        # Buscar el código en el texto (formato: 6 dígitos)
        code_match = re.search(r'\b(\d{6})\b', html_content)
        if code_match:
            return code_match.group(1)
        return None
    
    def step1_get_login_page(self):
        """Paso 1: Obtener la página de login y el token CSRF"""
        print("🔄 Paso 1: Obteniendo página de login...")
        
        try:
            response = self.session.get(f"{self.base_url}/login")
            response.raise_for_status()
            
            self.csrf_token = self.get_csrf_token(response.text)
            if not self.csrf_token:
                raise Exception("No se pudo obtener el token CSRF")
            
            print(f"✅ Token CSRF obtenido: {self.csrf_token[:20]}...")
            return True
            
        except Exception as e:
            print(f"❌ Error en paso 1: {e}")
            return False
    
    def step2_login(self, username, password):
        """Paso 2: Realizar login"""
        print("🔄 Paso 2: Realizando login...")
        
        try:
            login_data = {
                '_token': self.csrf_token,
                'name': username,
                'password': password
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Verificar si fuimos redirigidos a la página de verificación
            if 'dispositivo_no_vinculado' in response.url:
                print("✅ Login exitoso - Redirigido a verificación de dispositivo")
                return response.text
            else:
                print("❌ Login falló - No se redirigió correctamente")
                return None
                
        except Exception as e:
            print(f"❌ Error en paso 2: {e}")
            return None
    
    def step3_get_verification_code(self, html_content):
        """Paso 3: Extraer código de verificación"""
        print("🔄 Paso 3: Extrayendo código de verificación...")
        
        try:
            # Actualizar token CSRF
            self.csrf_token = self.get_csrf_token(html_content)
            
            # Extraer código de verificación
            self.verification_code = self.get_verification_code(html_content)
            
            if not self.verification_code:
                print("❌ No se pudo extraer el código de verificación")
                return False
            
            print(f"✅ Código de verificación encontrado: {self.verification_code}")
            return True
            
        except Exception as e:
            print(f"❌ Error en paso 3: {e}")
            return False
    
    def step4_verify_device(self):
        """Paso 4: Verificar dispositivo con el código"""
        print("🔄 Paso 4: Verificando dispositivo...")
        
        try:
            verify_data = {
                '_token': self.csrf_token,
                'codigo': self.verification_code
            }
            
            response = self.session.post(
                f"{self.base_url}/vincular_dispositivo",
                data=verify_data,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Verificar si la verificación fue exitosa
            if 'dispositivo_no_vinculado' not in response.url:
                print("✅ Dispositivo verificado exitosamente")
                return True
            else:
                print("❌ Error en verificación de dispositivo")
                return False
                
        except Exception as e:
            print(f"❌ Error en paso 4: {e}")
            return False
    
    def step5_get_dashboard_tokens(self):
        """Paso 5: Obtener tokens necesarios para requests autenticados"""
        print("🔄 Paso 5: Obteniendo tokens del dashboard...")
        
        try:
            # Ir a la página de despachos
            response = self.session.get(f"{self.base_url}/despachos")
            response.raise_for_status()
            
            # Extraer CSRF token actualizado
            self.csrf_token = self.get_csrf_token(response.text)
            
            # Buscar el token X-CSRF-TOKEN en meta tags
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            x_csrf_token = csrf_meta.get('content') if csrf_meta else self.csrf_token
            
            print(f"✅ Tokens obtenidos - CSRF: {self.csrf_token[:20]}...")
            
            return {
                'csrf_token': self.csrf_token,
                'x_csrf_token': x_csrf_token,
                'cookies': dict(self.session.cookies)
            }
            
        except Exception as e:
            print(f"❌ Error en paso 5: {e}")
            return None
    
    def navigate_to_despachos_registrar(self):
        """Navegar a la página de registro de despachos y extraer datos del componente"""
        print("🔄 Navegando a página de registro de despachos...")
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Intento {attempt + 1}/{max_retries}")
                
                response = self.session.get(f"{self.base_url}/despachos/registrar")
                response.raise_for_status()
                
                print(f"📊 Status Code: {response.status_code}")
                print(f"🌐 Final URL: {response.url}")
                print(f"📄 Response length: {len(response.text)} chars")
                
                # Verificar si la página contiene contenido real o solo loading
                if 'loading-top' in response.text and 'wire:id' not in response.text:
                    print("⚠️ Página de loading detectada, esperando...")
                    time.sleep(retry_delay)
                    continue
                
                # Debug: verificar si hay componentes Livewire en la página
                if 'wire:id' in response.text:
                    print("✅ Componentes Livewire detectados en la página")
                else:
                    print("⚠️ No se detectaron componentes Livewire en la página")
                
                if 'Livewire.start' in response.text:
                    print("✅ Scripts de Livewire detectados")
                else:
                    print("⚠️ No se detectaron scripts de Livewire")
                
                # Actualizar CSRF token
                self.csrf_token = self.get_csrf_token(response.text)
                
                # Extraer datos del componente Livewire
                component_data = self.extract_livewire_component_data(response.text)
                
                if component_data:
                    print("✅ Página de registro cargada exitosamente")
                    return component_data
                else:
                    print("⚠️ No se pudieron extraer datos completos del componente")
                    if attempt == max_retries - 1:
                        # Guardar HTML para debug solo en el último intento
                        with open('debug_registro_page.html', 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print("📄 HTML guardado en 'debug_registro_page.html' para análisis")
                    else:
                        time.sleep(retry_delay)
                        continue
                
            except Exception as e:
                print(f"❌ Error en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
        
        return None
    
    def extract_livewire_component_data(self, html_content):
        """Extraer datos del componente Livewire del HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Buscar específicamente el componente de registro de despachos
            # Primero buscar por ID específico conocido del formulario
            target_component = soup.find('div', {'wire:id': 'sHMG2QtFIfB6w2F4jVnH'})
            
            if not target_component:
                # Buscar componente que contenga "searchEmpresaCodigo" en wire:initial-data
                all_components = soup.find_all('div', {'wire:initial-data': True})
                for comp in all_components:
                    initial_data = comp.get('wire:initial-data', '')
                    if 'searchEmpresaCodigo' in initial_data or 'cWFjL1BPYjFSMHBuMWkxbi9PZ0dxdz09' in initial_data:
                        target_component = comp
                        break
            
            if not target_component:
                # Fallback: buscar cualquier div con wire:id que tenga clase componentRegistro
                target_component = soup.find('div', {'wire:id': True, 'class': lambda x: x and 'componentRegistro' in ' '.join(x) if x else False})
            
            if not target_component:
                print("❌ No se encontró el componente de registro de despachos")
                return None
            
            component_id = target_component.get('wire:id')
            print(f"🔍 Component ID encontrado: {component_id}")
            
            # Extraer datos de wire:initial-data
            initial_data_raw = target_component.get('wire:initial-data')
            if initial_data_raw:
                try:
                    # Decodificar HTML entities
                    import html
                    decoded_data = html.unescape(initial_data_raw)
                    livewire_data = json.loads(decoded_data)
                    print("✅ Datos Livewire extraídos de wire:initial-data")
                    
                    # Verificar que tenga los datos necesarios para búsqueda de empresa
                    if 'serverMemo' in livewire_data and 'data' in livewire_data['serverMemo']:
                        data_keys = livewire_data['serverMemo']['data'].get('data', {}).keys()
                        if 'cWFjL1BPYjFSMHBuMWkxbi9PZ0dxdz09' in data_keys:
                            print("✅ Componente de búsqueda de empresa confirmado")
                            return livewire_data
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Error decodificando wire:initial-data: {e}")
            
            # Si no se pudo extraer de wire:initial-data, crear estructura básica
            print("⚠️ Creando estructura básica para el componente")
            livewire_data = {
                "fingerprint": {
                    "id": component_id,
                    "name": "eyJpdiI6ImVMR0QwQ29KMHhIRDIzWCtVRzY5cFE9PSIsInZhbHVlIjoiQWw3eXlDTDlSRUhEYnZ1NnkzY3VMQkExY243UXdyZ2VHNkx5THJiUkgzYz0iLCJtYWMiOiI2NTE4YTgxZjc2MDRkOWIyZDliNjgyYTFiZWJlZTdhMmMyZjM4MDZjN2IxYzU1YWY2M2Y1YWQ5MjA1NzU4ZDQ0IiwidGFnIjoiIn0=",
                    "locale": "es",
                    "path": "despachos/registrar",
                    "method": "GET",
                    "v": "acj"
                },
                "serverMemo": {
                    "children": {},
                    "errors": [],
                    "htmlHash": "fd29f861",
                    "data": {
                        "data": {
                            "cWFjL1BPYjFSMHBuMWkxbi9PZ0dxdz09": ""  # Campo del código de empresa
                        },
                        "empresas": []
                    },
                    "dataMeta": [],
                    "checksum": "579252a065f9bc7a7488120addf459432f3e59e93007c7a98831849ffe1e98bc"
                }
            }
            
            return livewire_data
            
        except Exception as e:
            print(f"❌ Error extrayendo datos del componente: {e}")
            return None
    
    def search_empresa_by_codigo(self, codigo_empresa, component_data):
        """Buscar empresa por código usando Livewire"""
        print(f"🔍 Buscando empresa con código: {codigo_empresa}")
        
        try:
            # Headers específicos para el request
            headers = {
                'Accept': 'text/html, application/xhtml+xml',
                'Content-Type': 'application/json',
                'X-Livewire': 'true',
                'X-CSRF-TOKEN': self.csrf_token,
                'Referer': f"{self.base_url}/despachos/registrar",
                'Origin': self.base_url,
            }
            
            # Construir payload basado en el ejemplo
            payload = {
                "fingerprint": component_data["fingerprint"],
                "serverMemo": component_data["serverMemo"],
                "updates": [
                    {
                        "type": "syncInput",
                        "payload": {
                            "id": "ohmu",  # ID del input (puede ser dinámico)
                            "name": "data.cWFjL1BPYjFSMHBuMWkxbi9PZ0dxdz09",  # Campo del código
                            "value": str(codigo_empresa)
                        }
                    },
                    {
                        "type": "callMethod",
                        "payload": {
                            "id": "mvmr",  # ID del método (puede ser dinámico)
                            "method": "searchEmpresaCodigo",
                            "params": []
                        }
                    }
                ]
            }
            
            # Obtener component name del fingerprint
            component_name = component_data["fingerprint"].get("name", "")
            if not component_name:
                print("❌ No se pudo obtener component_name del fingerprint")
                return None
            
            print(f"🔧 Usando component_name: {component_name[:50]}...")
            
            # URL del endpoint
            url = f"{self.base_url}/api/app/{component_name}"
            
            print(f"🌐 Enviando request a: {url}")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, json=payload, headers=headers)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return None
            
            try:
                result = response.json()
                print(f"✅ Response JSON recibido: {json.dumps(result, indent=2)[:500]}...")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Response text: {response.text[:500]}...")
                return None
            
            # Extraer datos de la empresa de la respuesta
            empresas = result.get('serverMemo', {}).get('data', {}).get('empresas', [])
            
            if empresas:
                empresa = empresas[0]  # Tomar la primera empresa encontrada
                print("✅ Empresa encontrada:")
                print(f"   📋 Código: {empresa.get('codigo')}")
                print(f"   🏢 Razón Social: {empresa.get('razon_social')}")
                print(f"   📄 RIF: {empresa.get('rif')}")
                print(f"   🏷️ Tipo: {empresa.get('tipo_ente')}")
                print(f"   📊 Nivel: {empresa.get('nivel')}")
                
                # Guardar la información de búsqueda
                self.last_search_result = result
                
                # Guardar la información de la empresa para referencia
                with open('empresa_encontrada.json', 'w') as f:
                    json.dump(empresa, f, indent=2)
                print(f"💾 Datos de empresa guardados en 'empresa_encontrada.json'")
                
                return empresa
            else:
                print("❌ No se encontró empresa con ese código")
                return None
            
        except Exception as e:
            print(f"❌ Error buscando empresa: {e}")
            return None
    
    def select_empresa(self, empresa_id, component_data):
        """Seleccionar empresa después de la búsqueda"""
        print(f"✅ Seleccionando empresa con ID: {empresa_id}")
        
        try:
            # Headers específicos para el request
            headers = {
                'Accept': 'text/html, application/xhtml+xml',
                'Content-Type': 'application/json',
                'X-Livewire': 'true',
                'X-CSRF-TOKEN': self.csrf_token,
                'Referer': f"{self.base_url}/despachos/registrar",
                'Origin': self.base_url,
            }
            
            # Construir payload para selección basado en el ejemplo
            # IMPORTANTE: Usar exactamente la misma estructura que la petición exitosa
            payload = {
                "fingerprint": component_data["fingerprint"],
                "serverMemo": component_data["serverMemo"],
                "updates": [
                    {
                        "type": "callMethod",
                        "payload": {
                            "id": "dpftk",  # ID del método (puede ser dinámico)
                            "method": "__method",
                            "params": [
                                "LzN6OGVJbzFJNjBlSW5PRk9XOWVaQkMzNVZ0bGVrWmVzc3FlTmVnQzloVT0%3D",  # Token/método codificado
                                empresa_id  # ID de la empresa a seleccionar
                            ]
                        }
                    }
                ]
            }
            
            # Verificar que tenemos los datos críticos para evitar error 500
            server_memo = component_data.get("serverMemo", {})
            html_hash = server_memo.get("htmlHash")
            checksum = server_memo.get("checksum")
            
            if not html_hash or not checksum:
                print("❌ Error: faltan htmlHash o checksum en serverMemo")
                print(f"   htmlHash: {html_hash}")
                print(f"   checksum: {checksum}")
                return None
            
            print(f"🔧 Verificación serverMemo:")
            print(f"   htmlHash: {html_hash}")
            print(f"   checksum: {checksum[:20]}...")
            print(f"   empresas en data: {len(server_memo.get('data', {}).get('empresas', []))}")
            
            # Obtener component name del fingerprint
            component_name = component_data["fingerprint"].get("name", "")
            if not component_name:
                print("❌ No se pudo obtener component_name del fingerprint")
                return None
            
            print(f"🔧 Usando component_name: {component_name[:50]}...")
            
            # URL del endpoint
            url = f"{self.base_url}/api/app/{component_name}"
            
            print(f"🌐 Enviando request de selección a: {url}")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, json=payload, headers=headers)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return None
            
            try:
                result = response.json()
                print(f"✅ Response JSON recibido: {json.dumps(result, indent=2)[:500]}...")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Response text: {response.text[:500]}...")
                return None
            
            # Verificar si la selección fue exitosa
            effects = result.get('effects', {})
            emits = effects.get('emits', [])
            
            # Buscar el evento de éxito
            success_found = False
            for emit in emits:
                if emit.get('event') == 'alert' and len(emit.get('params', [])) >= 2:
                    if emit['params'][0] == 'success' and 'seleccionada' in emit['params'][1].lower():
                        success_found = True
                        print(f"✅ {emit['params'][1]}")
                        break
            
            if success_found:
                print("✅ Empresa seleccionada exitosamente")
                
                # Actualizar el component_data con la nueva información
                server_memo = result.get('serverMemo', {})
                if server_memo:
                    component_data['serverMemo'] = server_memo
                
                return result
            else:
                print("⚠️ Selección completada pero sin confirmación de éxito")
                return result
            
        except Exception as e:
            print(f"❌ Error seleccionando empresa: {e}")
            return None

    def proceso_busqueda_y_seleccion_empresa(self):
        """Proceso completo de búsqueda y selección de empresa"""
        print("🔍 Iniciando proceso de búsqueda y selección de empresa...")
        
        # Navegar a la página de registro
        component_data = self.navigate_to_despachos_registrar()
        if not component_data:
            return None
        
        # Pedir código de empresa por consola
        while True:
            try:
                codigo_empresa = input("🏢 Ingresa el código de la empresa: ").strip()
                if codigo_empresa.isdigit():
                    codigo_empresa = int(codigo_empresa)
                    break
                else:
                    print("❌ Por favor ingresa un código numérico válido")
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada")
                return None
        
        # Buscar empresa
        print(f"\n🔍 Buscando empresa con código: {codigo_empresa}")
        search_result = self.search_empresa_by_codigo(codigo_empresa, component_data)
        
        if not search_result:
            print("❌ No se encontró empresa o error en búsqueda")
            return None
        
        # Actualizar component_data con los resultados de búsqueda
        if self.last_search_result:
            # Es CRÍTICO usar el serverMemo actualizado de la respuesta de búsqueda
            # para que el checksum y htmlHash sean correctos
            updated_server_memo = self.last_search_result.get('serverMemo', {})
            if updated_server_memo:
                # CRÍTICO: Asegurar que el serverMemo tenga TODOS los campos requeridos
                # Comparando con la petición exitosa del documento
                
                # Obtener data actual y asegurar que tenga todos los campos requeridos
                current_data = updated_server_memo.get('data', {})
                
                # Asegurar que data tenga todos los campos que aparecen en la petición exitosa
                complete_data = current_data.copy()
                if 'conductores' not in complete_data:
                    complete_data['conductores'] = []
                if 'vehiculos' not in complete_data:
                    complete_data['vehiculos'] = []
                if 'rubros_' not in complete_data:
                    complete_data['rubros_'] = []
                if 'anios_cuspal' not in complete_data:
                    complete_data['anios_cuspal'] = ["2021","2022","2023","2024","2025"]
                if 'meses_cuspal' not in complete_data:
                    complete_data['meses_cuspal'] = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
                
                complete_server_memo = {
                    "children": updated_server_memo.get('children', {}),
                    "errors": updated_server_memo.get('errors', []),
                    "htmlHash": updated_server_memo.get('htmlHash'),
                    "data": complete_data,
                    "dataMeta": updated_server_memo.get('dataMeta', []),
                    "checksum": updated_server_memo.get('checksum')
                }
                
                component_data['serverMemo'] = complete_server_memo
                print(f"🔧 ServerMemo completo actualizado:")
                print(f"   htmlHash: {complete_server_memo.get('htmlHash', 'N/A')}")
                print(f"   checksum: {complete_server_memo.get('checksum', 'N/A')[:20]}...")
                print(f"   children: {len(complete_server_memo.get('children', {}))}")
                print(f"   errors: {len(complete_server_memo.get('errors', []))}")
                print(f"   dataMeta: {len(complete_server_memo.get('dataMeta', []))}")
        
        # Preguntar si desea seleccionar la empresa encontrada
        print(f"\n✅ Empresa encontrada:")
        print(f"   📋 Código: {search_result.get('codigo')}")
        print(f"   🏢 Razón Social: {search_result.get('razon_social')}")
        print(f"   📄 RIF: {search_result.get('rif')}")
        print(f"   🏷️ Tipo: {search_result.get('tipo_ente')}")
        print(f"   📊 Nivel: {search_result.get('nivel')}")
        
        while True:
            try:
                seleccionar = input("\n¿Deseas seleccionar esta empresa? (s/n): ").strip().lower()
                if seleccionar in ['s', 'si', 'sí', 'y', 'yes']:
                    break
                elif seleccionar in ['n', 'no']:
                    print("❌ Selección cancelada por el usuario")
                    return search_result
                else:
                    print("❌ Por favor responde 's' para sí o 'n' para no")
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada")
                return search_result
        
        # Seleccionar empresa
        print(f"\n✅ Seleccionando empresa...")
        empresa_id = search_result.get('id')
        if not empresa_id:
            print("❌ No se pudo obtener el ID de la empresa")
            return search_result
        
        selection_result = self.select_empresa(empresa_id, component_data)
        
        if selection_result:
            print("🎉 ¡Empresa seleccionada exitosamente!")
            
            # Guardar resultado completo
            complete_result = {
                'empresa': search_result,
                'selection_response': selection_result,
                'component_data': component_data
            }
            
            with open('empresa_seleccionada.json', 'w', encoding='utf-8') as f:
                json.dump(complete_result, f, indent=2, ensure_ascii=False)
            print("💾 Resultado completo guardado en 'empresa_seleccionada.json'")
            
            return complete_result
        else:
            print("❌ Error en la selección de empresa")
            return search_result

    def proceso_busqueda_empresa(self):
        """Proceso completo de búsqueda de empresa (solo búsqueda, sin selección)"""
        print("🔍 Iniciando proceso de búsqueda de empresa...")
        
        # Navegar a la página de registro
        component_data = self.navigate_to_despachos_registrar()
        if not component_data:
            return None
        
        # Pedir código de empresa por consola
        while True:
            try:
                codigo_empresa = input("🏢 Ingresa el código de la empresa: ").strip()
                if codigo_empresa.isdigit():
                    codigo_empresa = int(codigo_empresa)
                    break
                else:
                    print("❌ Por favor ingresa un código numérico válido")
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada")
                return None
        
        # Buscar empresa
        empresa = self.search_empresa_by_codigo(codigo_empresa, component_data)
        
        return empresa

    def search_conductor_by_cedula(self, cedula_conductor, component_data):
        """Buscar conductor por cédula usando Livewire"""
        print(f"🔍 Buscando conductor con cédula: {cedula_conductor}")
        
        try:
            # Headers específicos para el request
            headers = {
                'Accept': 'text/html, application/xhtml+xml',
                'Content-Type': 'application/json',
                'X-Livewire': 'true',
                'X-CSRF-TOKEN': self.csrf_token,
                'Referer': f"{self.base_url}/despachos/registrar",
                'Origin': self.base_url,
            }
            
            # Verificar que tenemos los datos críticos del component_data
            server_memo = component_data.get("serverMemo", {})
            html_hash = server_memo.get("htmlHash")
            checksum = server_memo.get("checksum")
            
            if not html_hash or not checksum:
                print("❌ Error: faltan htmlHash o checksum en serverMemo")
                print(f"   htmlHash: {html_hash}")
                print(f"   checksum: {checksum}")
                return None
            
            print(f"🔧 Verificación serverMemo para búsqueda de conductor:")
            print(f"   htmlHash: {html_hash}")
            print(f"   checksum: {checksum[:20]}...")
            
            # Verificar que la empresa esté seleccionada
            empresa_seleccionada = server_memo.get('data', {}).get('data', {}).get('THd2VHJ1QzNOWDVoUjlBRGZaSzIrZz09')
            if not empresa_seleccionada:
                print("❌ Error: No hay empresa seleccionada. Debe seleccionar empresa primero.")
                return None
            
            print(f"✅ Empresa seleccionada: {empresa_seleccionada}")
            
            # CRÍTICO: Asegurar que serverMemo.data tenga TODOS los campos requeridos
            # Basado en el request exitoso del documento
            server_memo_data = server_memo.get('data', {})
            
            # Verificar y completar estructura de data según el documento exitoso
            complete_data = server_memo_data.copy()
            
            # Asegurar que data.data tenga todos los campos del documento exitoso
            data_fields = complete_data.get('data', {})
            
            # CRÍTICO: Asegurar que empresas tenga los datos de la empresa seleccionada
            # El request exitoso muestra que empresas debe tener la información de la empresa
            empresas_data = server_memo_data.get('empresas', [])
            
            # Si empresas está vacío pero tenemos empresa seleccionada, necesitamos reconstruir
            if not empresas_data and empresa_seleccionada:
                print("⚠️ Array empresas vacío pero empresa seleccionada. Intentando reconstruir...")
                # Buscar en archivos guardados la información de la empresa
                try:
                    import os
                    if os.path.exists('empresa_seleccionada.json'):
                        with open('empresa_seleccionada.json', 'r', encoding='utf-8') as f:
                            empresa_data = json.load(f)
                            if 'empresa' in empresa_data:
                                empresa_info = empresa_data['empresa']
                                empresas_data = [{
                                    "id": empresa_info.get('id'),
                                    "codigo": empresa_info.get('codigo'),
                                    "rif": empresa_info.get('rif'),
                                    "razon_social": empresa_info.get('razon_social'),
                                    "tipo_ente": empresa_info.get('tipo_ente'),
                                    "nivel": empresa_info.get('nivel')
                                }]
                                print(f"✅ Información de empresa reconstruida: {empresa_info.get('razon_social')}")
                except Exception as e:
                    print(f"⚠️ No se pudo reconstruir información de empresa: {e}")
            
            # Asegurar que existan todos los arrays requeridos según el documento
            if 'empresas' not in complete_data:
                complete_data['empresas'] = empresas_data
            else:
                # Actualizar con datos reconstruidos si es necesario
                if not complete_data['empresas'] and empresas_data:
                    complete_data['empresas'] = empresas_data
                    
            if 'conductores' not in complete_data:
                complete_data['conductores'] = server_memo_data.get('conductores', [])
            if 'vehiculos' not in complete_data:
                complete_data['vehiculos'] = server_memo_data.get('vehiculos', [])
            if 'rubros_' not in complete_data:
                complete_data['rubros_'] = server_memo_data.get('rubros_', [])
            if 'anios_cuspal' not in complete_data:
                complete_data['anios_cuspal'] = ["2021","2022","2023","2024","2025"]
            if 'meses_cuspal' not in complete_data:
                complete_data['meses_cuspal'] = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
            
            print(f"🔧 Estructura serverMemo.data completada:")
            print(f"   empresas: {len(complete_data.get('empresas', []))}")
            print(f"   conductores: {len(complete_data.get('conductores', []))}")
            print(f"   vehiculos: {len(complete_data.get('vehiculos', []))}")
            print(f"   rubros_: {len(complete_data.get('rubros_', []))}")
            print(f"   anios_cuspal: {len(complete_data.get('anios_cuspal', []))}")
            print(f"   meses_cuspal: {len(complete_data.get('meses_cuspal', []))}")
            
            # Crear serverMemo completo con la estructura correcta
            complete_server_memo = {
                "children": server_memo.get('children', {}),
                "errors": server_memo.get('errors', []),
                "htmlHash": server_memo.get('htmlHash'),
                "data": complete_data,
                "dataMeta": server_memo.get('dataMeta', []),
                "checksum": server_memo.get('checksum')
            }
            
            # Construir payload basado en el ejemplo del documento
            payload = {
                "fingerprint": component_data["fingerprint"],
                "serverMemo": complete_server_memo,
                "updates": [
                    {
                        "type": "syncInput",
                        "payload": {
                            "id": "b3k7",  # ID del input según el documento
                            "name": "data.dFZpVGlDZU1rK2xmOE5GYTB2UTF2dz09",  # Campo de la cédula
                            "value": str(cedula_conductor)
                        }
                    },
                    {
                        "type": "callMethod",
                        "payload": {
                            "id": "2rps",  # ID del método según el documento
                            "method": "searchConductorCedula",
                            "params": []
                        }
                    }
                ]
            }
            
            # Obtener component name del fingerprint
            component_name = component_data["fingerprint"].get("name", "")
            if not component_name:
                print("❌ No se pudo obtener component_name del fingerprint")
                return None
            
            print(f"🔧 Usando component_name: {component_name[:50]}...")
            
            # URL del endpoint
            url = f"{self.base_url}/api/app/{component_name}"
            
            print(f"🌐 Enviando request de búsqueda de conductor a: {url}")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, json=payload, headers=headers)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return None
            
            try:
                result = response.json()
                print(f"✅ Response JSON recibido: {json.dumps(result, indent=2)[:500]}...")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Response text: {response.text[:500]}...")
                return None
            
            # Extraer datos del conductor de la respuesta
            conductores = result.get('serverMemo', {}).get('data', {}).get('conductores', [])
            
            if conductores:
                conductor = conductores[0]  # Tomar el primer conductor encontrado
                print("✅ Conductor encontrado:")
                print(f"   🆔 ID: {conductor.get('id')}")
                print(f"   📄 Cédula: {conductor.get('cedula')}")
                print(f"   👤 Nombre: {conductor.get('nombre')}")
                print(f"   👤 Apellido: {conductor.get('apellido')}")
                
                # Actualizar component_data con la nueva información
                if 'serverMemo' in result:
                    component_data['serverMemo'] = result['serverMemo']
                
                # Guardar la información del conductor para referencia
                with open('conductor_encontrado.json', 'w', encoding='utf-8') as f:
                    json.dump(conductor, f, indent=2, ensure_ascii=False)
                print(f"💾 Datos de conductor guardados en 'conductor_encontrado.json'")
                
                return conductor
            else:
                print("❌ No se encontró conductor con esa cédula")
                return None
            
        except Exception as e:
            print(f"❌ Error buscando conductor: {e}")
            return None

    def select_conductor(self, conductor_id, component_data):
        """Seleccionar un conductor específico por su ID"""
        print(f"🎯 Seleccionando conductor con ID: {conductor_id}")
        
        try:
            # Headers específicos para Livewire
            headers = {
                'Accept': 'text/html, application/xhtml+xml',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'es-ES,es;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Host': 'sica.sunagro.gob.ve',
                'Origin': 'https://sica.sunagro.gob.ve',
                'Referer': 'https://sica.sunagro.gob.ve/despachos/registrar',
                'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Gpc': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
                'X-Csrf-Token': self.csrf_token,
                'X-Livewire': 'true'
            }
            
            # CONSTRUIR SERVERMEMO COMPLETO SEGÚN EL DOCUMENTO
            original_server_memo = component_data.get("serverMemo", {})
            
            # Construir serverMemo COMPLETO con estructura exacta del documento
            original_data = original_server_memo.get("data", {})
            
            # Construir data COMPLETO con todas las secciones del documento
            # CRÍTICO: Las empresas DEBEN existir para que funcione la selección
            empresas_dinamicas = original_data.get("empresas", [])
            if not empresas_dinamicas:
                # Si no hay empresas en el contexto, usar la empresa del estado actual del bot
                if hasattr(self, 'empresa_seleccionada') and self.empresa_seleccionada:
                    empresas_dinamicas = [self.empresa_seleccionada]
                else:
                    # Fallback: buscar información completa de empresa previamente seleccionada
                    try:
                        import os
                        if os.path.exists('empresa_seleccionada.json'):
                            with open('empresa_seleccionada.json', 'r', encoding='utf-8') as f:
                                empresa_data = json.load(f)
                                if 'empresa' in empresa_data:
                                    empresas_dinamicas = [empresa_data['empresa']]
                                    print("✅ Empresa recuperada de archivo guardado")
                        
                        # Si no se pudo recuperar del archivo, intentar reconstruir mínimamente
                        if not empresas_dinamicas:
                            data_section = original_data.get("data", {})
                            empresa_id = data_section.get("THd2VHJ1QzNOWDVoUjlBRGZaSzIrZz09", "")
                            codigo_empresa = data_section.get("cWFjL1BPYjFSMHBuMWkxbi9PZ0dxdz09", "")
                            if empresa_id and codigo_empresa:
                                print("⚠️ No se encontró información completa de empresa. Usando datos mínimos.")
                                empresas_dinamicas = [{
                                    "id": empresa_id,
                                    "codigo": int(codigo_empresa) if codigo_empresa.isdigit() else None
                                }]
                    except Exception as e:
                        print(f"⚠️ Error al recuperar información de empresa: {e}")
                        # Como último recurso, usar array vacío y que el servidor maneje el error
                        empresas_dinamicas = []
            
            complete_data = {
                "data": original_data.get("data", {}),  # Usar data dinámico actual
                "empresas": empresas_dinamicas,  # Empresas dinámicas con fallback inteligente
                "conductores": original_data.get("conductores", []),  # Usar conductores dinámicos
                "vehiculos": original_data.get("vehiculos", []),  # Usar vehiculos dinámicos
                "rubros_": original_data.get("rubros_", []),  # Usar rubros dinámicos
                "anios_cuspal": original_data.get("anios_cuspal", ["2021", "2022", "2023", "2024", "2025"]),  # Dinámico con fallback
                "meses_cuspal": original_data.get("meses_cuspal", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])  # Dinámico con fallback
            }
            
            complete_server_memo = {
                "children": {
                    "l2055706833-0": {"id": "n2S5ZGS8lqe7yGG1IHXD", "tag": "div"},
                    "l2055706833-1": {"id": "M9IKeJCPxiKwtaJTOnQv", "tag": "div"}
                },
                "errors": [],
                "htmlHash": "859bb9ac",  # Hash exacto del documento
                "data": complete_data,  # Data COMPLETO con todas las secciones
                "dataMeta": [],
                "checksum": "2294cb9befc40c44c863f3cc4694ec453508a98ebc44580e5297413b42bcd423"  # Checksum exacto
            }
            
            print(f"🔧 ServerMemo original checksum: {original_server_memo.get('checksum', 'N/A')}")
            print(f"🔧 ServerMemo COMPLETO checksum: {complete_server_memo.get('checksum')}")
            print(f"🔧 Conductor ID a seleccionar: {conductor_id}")
            
            # Construir payload con fingerprint y serverMemo EXACTOS del documento
            payload = {
                "fingerprint": {
                    "id": "uzayRnVAtIeEl6rcrPxw",  # ID exacto del documento
                    "name": "eyJpdiI6IkFoWmpPNE9XUEJHWlZlZ3FycVllS3c9PSIsInZhbHVlIjoiTVd2QUVLUjZMNWszNElkbFFWWUxPQXZMNUMyTHdRVCsrSm00akRZVklqbz0iLCJtYWMiOiI5MGJiNDJlNjE1NmM0MGJiMjdjZDc0ZjVlOGZkZWE3MTI2NjJhODljZDRhMDlhYmI1NzIyOWFiOGQ2ZmVlOWY5IiwidGFnIjoiIn0=",
                    "locale": "es",
                    "path": "despachos/registrar", 
                    "method": "GET",
                    "v": "acj"
                },
                "serverMemo": complete_server_memo,  # ServerMemo completo con children y errors
                "updates": [
                    {
                        "type": "callMethod",
                        "payload": {
                            "id": "zkm8",
                            "method": "__method",
                            "params": [
                                "YTJnWEJUbmZ4UVR1NWtydHdXZWtGM1hxVGIwQ2xlTXVzNTlZcllCL0xVYz0%3D",
                                conductor_id
                            ]
                        }
                    }
                ]
            }
            
            # Usar component name EXACTO del documento
            component_name = "eyJpdiI6IkFoWmpPNE9XUEJHWlZlZ3FycVllS3c9PSIsInZhbHVlIjoiTVd2QUVLUjZMNWszNElkbFFWWUxPQXZMNUMyTHdRVCsrSm00akRZVklqbz0iLCJtYWMiOiI5MGJiNDJlNjE1NmM0MGJiMjdjZDc0ZjVlOGZkZWE3MTI2NjJhODljZDRhMDlhYmI1NzIyOWFiOGQ2ZmVlOWY5IiwidGFnIjoiIn0="
            
            print(f"🔧 Usando component_name EXACTO del documento: {component_name[:50]}...")
            
            # URL del endpoint
            url = f"{self.base_url}/api/app/{component_name}"
            
            print(f"🌐 Enviando request de selección de conductor a: {url}")
            print(f"📦 Payload de selección EXACTO: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, json=payload, headers=headers)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                # Guardar respuesta de error para análisis
                with open('error_seleccion_conductor.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("💾 Respuesta de error guardada en 'error_seleccion_conductor.html'")
                return None
            
            try:
                result = response.json()
                print(f"✅ Response JSON recibido: {json.dumps(result, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Response text: {response.text[:500]}...")
                return None
            
            # Verificar si la selección fue exitosa
            effects = result.get('effects', {})
            emits = effects.get('emits', [])
            
            # Buscar mensaje de éxito
            success_found = False
            for emit in emits:
                if emit.get('event') == 'alert' and 'success' in emit.get('params', []):
                    success_found = True
                    print("✅ Conductor seleccionado exitosamente!")
                    print(f"   📢 Mensaje: {emit.get('params', [])[1] if len(emit.get('params', [])) > 1 else 'N/A'}")
                    break
            
            if not success_found:
                print("⚠️ No se encontró confirmación de éxito en la respuesta")
            
            # Actualizar component_data con la nueva información del serverMemo
            if 'serverMemo' in result:
                component_data['serverMemo'] = result['serverMemo']
                print("🔄 ServerMemo actualizado con nueva información")
            
            # Guardar respuesta completa para análisis
            with open('seleccion_conductor_response.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print("💾 Respuesta de selección guardada en 'seleccion_conductor_response.json'")
            
            return result
            
        except Exception as e:
            print(f"❌ Error seleccionando conductor: {e}")
            return None

    def proceso_busqueda_y_seleccion_conductor(self, component_data):
        """Proceso completo de búsqueda y selección de conductor (requiere empresa ya seleccionada)"""
        print("🔍 Iniciando proceso de búsqueda y selección de conductor...")
        
        # Verificar que component_data tenga empresa seleccionada
        if not component_data:
            print("❌ Error: No se proporcionó component_data")
            return None
        
        server_memo = component_data.get("serverMemo", {})
        empresa_seleccionada = server_memo.get('data', {}).get('data', {}).get('THd2VHJ1QzNOWDVoUjlBRGZaSzIrZz09')
        
        if not empresa_seleccionada:
            print("❌ Error: Debe seleccionar una empresa antes de buscar conductor")
            return None
        
        print(f"✅ Empresa seleccionada verificada: {empresa_seleccionada}")
        
        # Pedir cédula de conductor por consola
        while True:
            try:
                cedula_input = input("👤 Ingresa el número de documento del conductor (ej: V-25526479): ").strip()
                
                # Validar formato básico de cédula venezolana
                if cedula_input:
                    # Permitir formatos como V-12345678, V12345678, 12345678
                    cedula_clean = cedula_input.upper().replace('-', '').replace(' ', '')
                    
                    # Si no tiene letra, agregar V por defecto
                    if cedula_clean.isdigit():
                        cedula_formatted = f"V-{cedula_clean}"
                    elif cedula_clean.startswith(('V', 'E', 'J', 'G', 'P')):
                        # Formatear con guión si no lo tiene
                        if '-' not in cedula_input:
                            cedula_formatted = f"{cedula_clean[0]}-{cedula_clean[1:]}"
                        else:
                            cedula_formatted = cedula_input.upper()
                    else:
                        print("❌ Formato de cédula inválido. Use formato: V-12345678")
                        continue
                    
                    print(f"🔧 Cédula formateada: {cedula_formatted}")
                    break
                else:
                    print("❌ Por favor ingresa una cédula válida")
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada")
                return None
        
        # Buscar conductor
        print(f"\n🔍 Buscando conductor con cédula: {cedula_formatted}")
        conductor_result = self.search_conductor_by_cedula(cedula_formatted, component_data)
        
        if conductor_result:
            print("🎉 ¡Conductor encontrado exitosamente!")
            
            # Preguntar si desea seleccionar el conductor encontrado
            print(f"\n📋 Conductor encontrado:")
            print(f"   🆔 ID: {conductor_result.get('id')}")
            print(f"   📄 Cédula: {conductor_result.get('cedula')}")
            print(f"   👤 Nombre: {conductor_result.get('nombre')} {conductor_result.get('apellido')}")
            
            while True:
                try:
                    seleccionar = input("\n¿Desea seleccionar este conductor? (s/n): ").strip().lower()
                    if seleccionar in ['s', 'si', 'sí', 'y', 'yes']:
                        # Seleccionar el conductor
                        print(f"\n🎯 Seleccionando conductor...")
                        selection_result = self.select_conductor(conductor_result.get('id'), component_data)
                        
                        if selection_result:
                            print("✅ ¡Conductor seleccionado exitosamente!")
                            
                            # Guardar resultado completo
                            complete_result = {
                                'conductor': conductor_result,
                                'selection_response': selection_result,
                                'component_data': component_data,
                                'cedula_buscada': cedula_formatted,
                                'estado': 'SELECCIONADO'
                            }
                            
                            with open('conductor_seleccionado.json', 'w', encoding='utf-8') as f:
                                json.dump(complete_result, f, indent=2, ensure_ascii=False)
                            print("💾 Resultado completo guardado en 'conductor_seleccionado.json'")
                            
                            return complete_result
                        else:
                            print("❌ Error al seleccionar conductor")
                            return None
                        
                    elif seleccionar in ['n', 'no']:
                        print("⚠️ Conductor no seleccionado")
                        # Guardar resultado solo de búsqueda
                        search_result = {
                            'conductor': conductor_result,
                            'component_data': component_data,
                            'cedula_buscada': cedula_formatted,
                            'estado': 'ENCONTRADO_NO_SELECCIONADO'
                        }
                        
                        with open('conductor_encontrado.json', 'w', encoding='utf-8') as f:
                            json.dump(search_result, f, indent=2, ensure_ascii=False)
                        print("💾 Resultado de búsqueda guardado en 'conductor_encontrado.json'")
                        
                        return search_result
                    else:
                        print("❌ Por favor responda 's' para sí o 'n' para no")
                        continue
                    break
                except KeyboardInterrupt:
                    print("\n❌ Operación cancelada")
                    return None
        else:
            print("❌ No se encontró conductor o error en búsqueda")
            return None

    def proceso_busqueda_conductor(self, component_data):
        """Proceso de solo búsqueda de conductor (sin selección automática)"""
        return self.proceso_busqueda_y_seleccion_conductor(component_data)
        
    
    def make_livewire_request(self, component_name, method_params="cTZRVCtiWmwrSVlGMGpOa3FMZFBjQT09"):
        """Realizar request de Livewire al sistema"""
        print("🔄 Realizando request de Livewire...")
        
        try:
            # Headers específicos para Livewire
            headers = {
                'Accept': 'text/html, application/xhtml+xml',
                'Content-Type': 'application/json',
                'X-Livewire': 'true',
                'X-CSRF-TOKEN': self.csrf_token,
                'Referer': f"{self.base_url}/despachos",
                'Origin': self.base_url,
            }
            
            # Payload de Livewire
            payload = {
                "fingerprint": {
                    "id": "Gu3XT86SVG7q3uARkXP6",
                    "name": component_name,
                    "locale": "es",
                    "path": "despachos",
                    "method": "GET",
                    "v": "acj"
                },
                "serverMemo": {
                    "children": [],
                    "errors": [],
                    "htmlHash": "dba7adc7",
                    "data": {
                        "paginate": 10,
                        "readyToLoad": False,
                        "filtros": False,
                        "page": 1,
                        "paginators": {"page": 1}
                    },
                    "dataMeta": [],
                    "checksum": "b5279f415ace27fa4609ed4fe4708cc4eefc62693126978552057888f10c5f92"
                },
                "updates": [{
                    "type": "callMethod",
                    "payload": {
                        "id": "u9qy",
                        "method": "__method",
                        "params": [method_params]
                    }
                }]
            }
            
            # URL del endpoint
            url = f"{self.base_url}/api/app/{component_name}"
            
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            print("✅ Request de Livewire exitoso")
            return response.json()
            
        except Exception as e:
            print(f"❌ Error en request de Livewire: {e}")
            return None
    
    def full_login_process(self, username, password):
        """Proceso completo de login"""
        print("🚀 Iniciando proceso completo de login...")
        
        # Paso 1: Obtener página de login
        if not self.step1_get_login_page():
            return False
        
        # Paso 2: Realizar login
        verification_page = self.step2_login(username, password)
        if not verification_page:
            return False
        
        # Paso 3: Extraer código de verificación
        if not self.step3_get_verification_code(verification_page):
            return False
        
        # Paso 4: Verificar dispositivo
        if not self.step4_verify_device():
            return False
        
        # Paso 5: Obtener tokens del dashboard
        tokens = self.step5_get_dashboard_tokens()
        if not tokens:
            return False
        
        # Marcar como logueado exitosamente
        self.logged_in = True
        print("🎉 ¡Proceso de login completado exitosamente!")
        return tokens
    
    def logout(self):
        """Cerrar sesión en el sistema SICA"""
        if not self.logged_in:
            return True
            
        print("🔄 Cerrando sesión...")
        
        try:
            # Obtener token CSRF actual
            if not self.csrf_token:
                # Intentar obtener token de cualquier página
                try:
                    response = self.session.get(f"{self.base_url}/despachos")
                    self.csrf_token = self.get_csrf_token(response.text)
                except:
                    pass
            
            # Datos para el logout
            logout_data = {
                '_token': self.csrf_token or ''
            }
            
            # Realizar logout
            response = self.session.post(
                f"{self.base_url}/logout",
                data=logout_data,
                allow_redirects=True
            )
            
            # Verificar si el logout fue exitoso
            if 'login' in response.url or response.status_code == 200:
                print("✅ Sesión cerrada exitosamente")
                self.logged_in = False
                return True
            else:
                print("⚠️ Logout completado (verificación incierta)")
                self.logged_in = False
                return True
                
        except Exception as e:
            print(f"⚠️ Error en logout (continuando): {e}")
            self.logged_in = False
            return False
    
    def cleanup(self):
        """Función de limpieza automática"""
        if self.logged_in:
            print("\n🧹 Limpieza automática: cerrando sesión...")
            self.logout()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - garantiza logout"""
        self.logout()
        if exc_type:
            print(f"❌ Error durante ejecución: {exc_val}")
        return False  # No suprimir excepciones
    
    def get_despachos_data(self):
        """Obtener datos de despachos usando el request que analizamos"""
        component_name = "eyJpdiI6InJoYmlpMDJOeFBOVS9qaENVMGZ5cUE9PSIsInZhbHVlIjoiZWxDTkd6WkkxN1NxeDByN29IMEJzbTJIaGNBNzlZQ2cvdWVsVG10Ykk5dz0iLCJtYWMiOiI5NjVjMWE2ZmU2MmRhOWMwNmRiNjliNjI1YzFhOTA3MjJkOWE0YjMxY2UwYzMwNTZkM2Q5Y2RjNTRkNWMyMzM4IiwidGFnIjoiIn0="
        
        return self.make_livewire_request(component_name)


def main():
    """Función principal de ejemplo"""
    print("=" * 60)
    print("🤖 SICA Bot - Automatización de Login")
    print("=" * 60)
    
    # Usar context manager para garantizar logout automático
    try:
        with SICABot() as bot:
            # Credenciales por defecto
            username = "CBULLON"
            password = "Cb17985096."
            print(f"👤 Usuario: {username}")
            print(f"🔒 Contraseña: {password}")
            
            # Proceso completo de login
            tokens = bot.full_login_process(username, password)
            
            if tokens:
                print("\n📊 Tokens obtenidos:")
                print(f"CSRF Token: {tokens['csrf_token'][:20]}...")
                print(f"Cookies: {len(tokens['cookies'])} cookies")
                
                # Hacer request de ejemplo
                print("\n🔍 Obteniendo datos de despachos...")
                despachos_data = bot.get_despachos_data()
                
                if despachos_data:
                    print("✅ Datos obtenidos exitosamente")
                    
                    # Guardar respuesta en archivo
                    with open('despachos_response.json', 'w', encoding='utf-8') as f:
                        json.dump(despachos_data, f, indent=2, ensure_ascii=False)
                    print("💾 Respuesta guardada en 'despachos_response.json'")
                else:
                    print("❌ Error obteniendo datos de despachos")
                
                # Proceso de búsqueda y selección de empresa
                print("\n" + "="*50)
                print("🔍 BÚSQUEDA Y SELECCIÓN DE EMPRESA")
                print("="*50)
                
                resultado = bot.proceso_busqueda_y_seleccion_empresa()
                
                if resultado:
                    if isinstance(resultado, dict) and 'empresa' in resultado:
                        # Resultado completo con selección
                        empresa = resultado['empresa']
                        print("\n🎉 Proceso completo exitoso:")
                        print(f"   📋 Código: {empresa.get('codigo')}")
                        print(f"   🏢 Razón Social: {empresa.get('razon_social')}")
                        print(f"   📄 RIF: {empresa.get('rif')}")
                        print(f"   🏷️ Tipo: {empresa.get('tipo_ente')}")
                        print(f"   📊 Nivel: {empresa.get('nivel')}")
                        print("   ✅ Estado: SELECCIONADA")
                        
                        print("\n✅ Búsqueda y selección completadas exitosamente")
                        
                        # Proceso de búsqueda y selección de conductor (después de seleccionar empresa)
                        print("\n" + "="*50)
                        print("👤 BÚSQUEDA Y SELECCIÓN DE CONDUCTOR")
                        print("="*50)
                        
                        component_data = resultado.get('component_data')
                        if component_data:
                            resultado_conductor = bot.proceso_busqueda_y_seleccion_conductor(component_data)
                            
                            if resultado_conductor:
                                conductor = resultado_conductor['conductor']
                                estado = resultado_conductor.get('estado', 'DESCONOCIDO')
                                
                                print(f"\n🎉 Proceso de conductor exitoso:")
                                print(f"   🆔 ID: {conductor.get('id')}")
                                print(f"   📄 Cédula: {conductor.get('cedula')}")
                                print(f"   👤 Nombre: {conductor.get('nombre')}")
                                print(f"   👤 Apellido: {conductor.get('apellido')}")
                                print(f"   ✅ Estado: {estado}")
                                
                                if estado == 'SELECCIONADO':
                                    print("\n🎯 ¡Conductor seleccionado exitosamente!")
                                    print("   📋 El conductor está listo para el siguiente paso del proceso")
                                elif estado == 'ENCONTRADO_NO_SELECCIONADO':
                                    print("\n⚠️ Conductor encontrado pero no seleccionado")
                                    print("   📋 Para continuar, deberá seleccionar un conductor")
                                
                                print(f"\n✅ Proceso de conductor completado - Estado: {estado}")
                            else:
                                print("❌ No se encontró conductor o error en búsqueda")
                        else:
                            print("❌ Error: No se pudo obtener component_data para búsqueda de conductor")
                    else:
                        # Solo búsqueda, sin selección
                        print("\n✅ Empresa encontrada (sin seleccionar):")
                        print(f"   📋 Código: {resultado.get('codigo')}")
                        print(f"   🏢 Razón Social: {resultado.get('razon_social')}")
                        print(f"   📄 RIF: {resultado.get('rif')}")
                        print(f"   🏷️ Tipo: {resultado.get('tipo_ente')}")
                        print(f"   📊 Nivel: {resultado.get('nivel')}")
                        
                        print("\n✅ Búsqueda completada exitosamente")
                        print("⚠️ Nota: Para buscar conductor, debe seleccionar la empresa primero")
                else:
                    print("❌ No se encontró empresa o error en búsqueda")
            else:
                print("❌ Error en el proceso de login")
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        print("\n🏁 Proceso finalizado")


if __name__ == "__main__":
    main()
