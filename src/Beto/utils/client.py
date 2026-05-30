import requests
import urllib3


def obtener_cliente_http(es_api=False) -> requests.Session:
    """
    Fabrica y retorna una sesión de requests configurada de forma centralizada.
    Apaga de forma segura las advertencias de SSL para los sitios de gobierno.
    """
    # Desactivar advertencias de SSL una sola vez a nivel global
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    session = requests.Session()

    # Cabeceras base comunes para simular un navegador real en Lubuntu
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    # Ajuste dinámico dependiendo de si vas a scrapear HTML o a consumir un JSON de API
    if es_api:
        headers["Accept"] = "application/json"
    else:
        headers["Accept"] = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        )

    session.headers.update(headers)

    # Opcional: Aquí podrías agregar lógica global de reintentos (Retries)
    # si un servidor de la SCJN o UNAM se cae momentáneamente.

    return session
