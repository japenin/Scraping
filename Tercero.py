import requests
import base64
from urllib.parse import urljoin
import json
import time

# Configuración
BASE_URL = "http://192.168.44.3"
LOGIN_URL = urljoin(BASE_URL, "/")
DASHBOARD_URL = urljoin(BASE_URL, "/userRpm/Index.htm")
API_URL = urljoin(BASE_URL, "/admin/powerline?form=plc_device")

def get_plc_stats(username="1234", password="Murdock4"):
    """Obtiene las estadísticas PLC con manejo completo de sesión"""
    session = requests.Session()
    
    # Configurar headers como navegador
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": urljoin(BASE_URL, "/userRpm/powerlineNetwork.htm"),
    }
    
    try:
        # 1. Autenticación inicial
        auth_str = base64.b64encode(f"{username}:{password}".encode()).decode()
        session.headers.update(headers)
        session.cookies.set("Authorization", f"Basic {auth_str}")
        
        # 2. Navegar al dashboard primero (simular flujo del navegador)
        print("🔑 Iniciando sesión...")
        session.get(LOGIN_URL, timeout=5)
        time.sleep(1)  # Pequeño delay para simular navegador
        
        print("🚀 Accediendo al panel...")
        session.get(DASHBOARD_URL, timeout=5)
        time.sleep(1)
        
        # 3. Solicitar datos PLC con Referer correcto
        print("📡 Obteniendo estadísticas PLC...")
        api_response = session.post(
            API_URL,
            data="operation=load",
            timeout=10,
            headers={"Referer": urljoin(BASE_URL, "/userRpm/powerlineNetwork.htm")}
        )
        
        # 4. Verificar respuesta
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                if data.get('success'):
                    return data['data'][0]  # Devuelve el primer dispositivo
                raise Exception("La API no devolvié success=True")
            except json.JSONDecodeError:
                # Guardar respuesta para diagnóstico
                with open("api_response.txt", "w", encoding="utf-8") as f:
                    f.write(api_response.text)
                raise Exception("Respuesta no es JSON válido. Ver api_response.txt")
        else:
            raise Exception(f"Error HTTP {api_response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        return None

# Ejecución principal
if __name__ == "__main__":
    print("🔌 Iniciando monitor PLC...")
    
    stats = get_plc_stats()
    if stats:
        print("\n✅ Datos PLC obtenidos correctamente:")
        print(f"MAC: {stats.get('device_mac', 'N/A')}")
        print(f"Velocidad RX: {stats.get('rx_rate', 'N/A')} Mbps")
        print(f"Velocidad TX: {stats.get('tx_rate', 'N/A')} Mbps")
    else:
        print("\n❌ Fallo al obtener datos. Soluciones:")
        print("1. Verifica que las credenciales sean correctas")
        print("2. Comprueba que puedas acceder manualmente a la interfaz")
        print("3. Revisa el archivo api_response.txt para diagnóstico")