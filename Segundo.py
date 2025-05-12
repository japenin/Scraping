import requests
import base64
from urllib.parse import urljoin
import json

# Configuración
base_url = "http://192.168.44.3"
login_url = urljoin(base_url, "/")
api_url = urljoin(base_url, "/admin/powerline?form=plc_device")

# Autenticación
username = "1234"
password = "Murdock4"
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Headers para simular completamente al navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": base_url,
    "Connection": "keep-alive",
    "Referer": urljoin(base_url, "/userRpm/powerlineNetwork.htm"),
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}

try:
    with requests.Session() as session:
        # 1. Primera solicitud para establecer cookies
        print("🔑 Iniciando sesión...")
        login_response = session.get(login_url, headers=headers, timeout=5)
        
        # 2. Configurar manualmente la cookie de autenticación
        session.cookies.set("Authorization", f"Basic {encoded_credentials}", domain="192.168.44.3")
        
        # 3. Hacer la petición a la API con todos los headers y cookies
        print("📡 Solicitando datos PLC...")
        api_response = session.post(
            api_url,
            headers=headers,
            data="operation=load",
            timeout=10
        )
        
        # Guardar respuesta completa para diagnóstico
        with open("api_response.txt", "w", encoding="utf-8") as f:
            f.write(f"Status Code: {api_response.status_code}\n")
            f.write(f"Headers: {api_response.headers}\n")
            f.write(f"Cookies: {session.cookies.get_dict()}\n")
            f.write("Body:\n")
            f.write(api_response.text)
        
        # 4. Procesar la respuesta
        if api_response.status_code == 200:
            try:
                plc_data = api_response.json()
                print("✅ Datos PLC obtenidos correctamente!")
                
                if 'data' in plc_data and plc_data['data']:
                    device = plc_data['data'][0]  # Primer dispositivo
                    print(f"\n📊 Estado PLC:")
                    print(f"MAC: {device.get('device_mac', 'N/A')}")
                    print(f"⬇️ RX: {device.get('rx_rate', 'N/A')} Mbps")
                    print(f"⬆️ TX: {device.get('tx_rate', 'N/A')} Mbps")
                    
                    # Guardar datos en JSON
                    with open("plc_data.json", "w") as f:
                        json.dump(plc_data, f, indent=2)
                else:
                    print("ℹ️ No se encontraron datos de dispositivos PLC")
            except ValueError:
                print("⚠️ La respuesta no es JSON válido")
                print(f"Contenido recibido: {api_response.text[:200]}...")
        else:
            print(f"❌ Error en la petición. Código: {api_response.status_code}")
            print(f"Respuesta: {api_response.text[:200]}...")

except requests.exceptions.RequestException as e:
    print(f"🚨 Error de conexión: {e}")
except Exception as e:
    print(f"⚠️ Error inesperado: {str(e)}")