## Hacer una conexion a una URL, introducir usuario y contraseña y usar BeautifulSoup para extraer informacion de la pagina
import requests
from bs4 import BeautifulSoup

url = "http://192.168.44.3"

## Hacer un POST con el usuario y contraseña
payload = {'userName': '1234', 'password': 'Murdock4'}
r = requests.post(url, data=payload)

## Acceder a la URL que tiene la indformacion
url = "http://192.168.44.3/admin/powerline?form=plc_device"  

r = requests.post(url)
htmlContent = r.content
soup = BeautifulSoup(htmlContent, 'html.parser')
print(soup.prettify())