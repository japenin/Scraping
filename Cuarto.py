import requests
import base64
from urllib.parse import urljoin
import json
import os
from cryptography.fernet import Fernet

# Configuración de archivos
CONFIG_FILE = "plc_config.json"
KEY_FILE = "plc_key.key"

# 1. Gestión de claves de encriptación
def ensure_key_exists():
    """Garantiza que existe una clave de encriptación"""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)

def get_encryption_key():
    """Obtiene la clave de encriptación"""
    with open(KEY_FILE, "rb") as f:
        return f.read()

# 2. Funciones de encriptación
def encrypt_string(text, key):
    """Encripta un string usando la clave proporcionada"""
    fernet = Fernet(key)
    return fernet.encrypt(text.encode()).decode()

def decrypt_string(encrypted_text, key):
    """Desencripta un string usando la clave proporcionada"""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text.encode()).decode()

# 3. Gestión del archivo de configuración
def load_config():
    """Carga la configuración y encripta la contraseña si está en claro"""
    ensure_key_exists()
    key = get_encryption_key()
    
    # Leer archivo de configuración
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    
    # Si la contraseña está en texto plano, encriptarla y guardar
    if not config.get("password_encrypted", False):
        config["password"] = encrypt_string(config["password"], key)
        config["password_encrypted"] = True
        save_config(config)
    
    # Desencriptar para uso en el programa
    config["decrypted_password"] = decrypt_string(config["password"], key)
    return config

def save_config(config):
    """Guarda la configuración en el archivo"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# 4. Función principal para obtener estadísticas PLC
def get_plc_stats():
    """Obtiene las estadísticas del PLC usando la configuración"""
    config = load_config()
    
    # Configuración de la solicitud
    base_url = config["base_url"]
    api_url = urljoin(base_url, "/admin/powerline?form=plc_device")
    auth_str = base64.b64encode(f"{config['username']}:{config['decrypted_password']}".encode()).decode()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": urljoin(base_url, "/userRpm/powerlineNetwork.htm"),
    }
    
    try:
        with requests.Session() as session:
            # Configurar autenticación
            session.cookies.set("Authorization", f"Basic {auth_str}", domain=base_url.split('//')[-1])
            
            # Obtener datos
            response = session.post(
                api_url,
                headers=headers,
                data="operation=load",
                timeout=10
            )
            
            if response.status_code == 200:
                plc_data = response.json()
                if plc_data.get('success', False):
                    device = plc_data['data'][0]
                    print("\n✅ Datos PLC obtenidos:")
                    print(f"MAC: {device.get('device_mac', 'N/A')}")
                    print(f"RX: {device.get('rx_rate', 'N/A')} Mbps")
                    print(f"TX: {device.get('tx_rate', 'N/A')} Mbps")
                    return True
            
            print("❌ Error al obtener datos PLC")
            return False
            
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Verificar que el archivo de configuración existe
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: El archivo de configuración {CONFIG_FILE} no existe")
        print("Por favor crea el archivo con este formato:")
        print(json.dumps({
            "base_url": "http://192.168.44.3",
            "username": "1234",
            "password": "TuContraseñaEnTextoPlano",
            "password_encrypted": False
        }, indent=2))
        exit(1)
    
    # Ejecutar
    get_plc_stats()