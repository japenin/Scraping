import requests
import base64
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuración
base_url = "http://192.168.44.3"
login_url = urljoin(base_url, "/")
dashboard_url = urljoin(base_url, "/userRpm/Index.htm")
plc_url = urljoin(base_url, "/userRpm/pages/userrpm/powerlineNetwork.html")

# Autenticación
username = "1234"
password = "Murdock4"
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Headers mejorados
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
    "Cookie": f"Authorization=Basic {encoded_credentials}",
    "Referer": login_url
}

try:
    with requests.Session() as session:
        # Configuración de la sesión
        session.headers.update(headers)
        
        # 1. Acceso inicial para establecer cookies
        print("🔑 Iniciando sesión...")
        response = session.get(login_url, timeout=10)
        response.raise_for_status()
        
        # 2. Acceder al dashboard
        print("🚀 Navegando al panel...")
        dashboard = session.get(dashboard_url, timeout=10)
        dashboard.raise_for_status()
        
        # 3. Acceder a la página PLC
        print("🔍 Buscando datos PLC...")
        plc_page = session.get(plc_url, timeout=10)
        plc_page.raise_for_status()
        
        # Guardar contenido para diagnóstico (modo binario para evitar problemas de codificación)
        with open("plc_debug.html", "wb") as f:
            f.write(plc_page.content)
        print("💾 HTML guardado en plc_debug.html")
        
        # 4. Extraer datos (versión mejorada)
        soup = BeautifulSoup(plc_page.text, 'html.parser')
        
        # Opción 1: Buscar por texto RX/TX
        rx, tx = None, None
        for elem in soup.find_all(string=lambda t: t and ("RX:" in t or "TX:" in t)):
            text = elem.strip()
            if "RX:" in text:
                rx = text.split("RX:")[1].split()[0]  # Ej: "RX:311Mbps" -> "311Mbps"
            elif "TX:" in text:
                tx = text.split("TX:")[1].split()[0]
        
        # Opción 2: Si no se encuentran, buscar en tablas
        if not rx or not tx:
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:  # Asumiendo RX/TX están en celdas
                        for cell in cells:
                            text = cell.get_text(strip=True)
                            if "RX:" in text:
                                rx = text.split("RX:")[1].split()[0]
                            elif "TX:" in text:
                                tx = text.split("TX:")[1].split()[0]
        
        # Resultado
        if rx and tx:
            print(f"\n✅ Datos PLC encontrados:")
            print(f"⬇️ RX: {rx}")
            print(f"⬆️ TX: {tx}")
        else:
            print("\n❌ No se encontraron datos RX/TX en la página")
            print("ℹ️ Por favor revisa el archivo plc_debug.html manualmente")

except requests.exceptions.RequestException as e:
    print(f"🚨 Error de conexión: {e}")
except Exception as e:
    print(f"⚠️ Error inesperado: {str(e)}")