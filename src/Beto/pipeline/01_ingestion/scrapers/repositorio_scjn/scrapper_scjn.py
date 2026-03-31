import json
import time
import requests
import pandas as pd
from pathlib import Path
import traceback
import urllib3
from Beto.utils.config import PROJECT_ROOT, BETO_ROOT

# Silenciar advertencias de certificados inseguros
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Extraer_scjn:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
        )

        # --- LÓGICA DE RUTAS ---
        # Subimos 3 niveles desde data/scripts_procesamiento/repositorio_scjn/ para llegar a BETO_LEGAL_MEXICO
        self.BASE_DIR = Path(__file__).resolve().parents[3]
        self.output_path = self.BASE_DIR / "data" / "bronze" / "scjn"
        self.output_path.mkdir(parents=True, exist_ok=True)

        self.pagina_n = 0
        self.params = {"page": self.pagina_n, "offset": 0, "limit": 1000}
        self.url_base = (
            "https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/engroses/"
        )
        self.diccionario_completo = {}

    def request_api_ids(self):
        API_URL = (
            "https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/engroses/ids"
        )
        try:
            page = self.session.get(
                API_URL, params=self.params, verify=False, timeout=15
            )
            if page.status_code == 200:
                lista_ids = page.json()
                self.diccionario_ids_urls = {
                    id_val: f"{self.url_base}{id_val}" for id_val in lista_ids
                }
                print(f"IDs obtenidos: {len(self.diccionario_ids_urls)}", flush=True)
            else:
                print(f"Error API: {page.status_code}")
        except Exception as e:
            print(f"Error en request_api_ids: {e}")

    def obtener_urls_docx(self):
        dic_apiurl = getattr(self, "diccionario_ids_urls", {})
        filtros = ["urlInternet", "expediente"]
        resultados = {}

        for clave, valor in dic_apiurl.items():
            try:
                r = self.session.get(valor, verify=False, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    resultados[clave] = {k: v for k, v in data.items() if k in filtros}
            except Exception as e:
                pass  # Errores individuales no detienen el proceso
        return resultados

    def iterar_paginas(self, max_paginas=5):
        print(f"Iniciando extracción masiva en: {self.output_path}", flush=True)
        for _ in range(max_paginas):
            self.pagina_n += 1
            self.params["page"] = self.pagina_n

            # Llamada al método
            self.request_api_ids()

            nuevos_datos = self.obtener_urls_docx()
            if nuevos_datos:
                self.diccionario_completo.update(nuevos_datos)
                print(
                    f"Página {self.pagina_n} terminada. Total: {len(self.diccionario_completo)}"
                )

            time.sleep(1)

    def guardar_resultados(self):
        # Guardar JSON
        ruta_json = self.output_path / "datos_limpios.json"
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(self.diccionario_completo, f, ensure_ascii=False, indent=4)
        print(f"JSON guardado en: {ruta_json}")

        # Guardar Excel
        ruta_excel = self.output_path / "scjn_api.xlsx"
        if self.diccionario_completo:
            df = pd.DataFrame.for_dict(self.diccionario_completo, orient="index")
            df.to_excel(ruta_excel, index_label="id_scjn")
            print(f"Excel guardado en: {ruta_excel}")


if __name__ == "__main__":
    try:
        procesador = Extraer_scjn()
        procesador.iterar_paginas(max_paginas=3)  # Prueba corta
        procesador.guardar_resultados()
    except Exception:
        traceback.print_exc()
