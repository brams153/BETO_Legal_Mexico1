import json
import time
import traceback
import pandas as pd
from Beto.utils.config import BRONZE_DIR
from Beto.utils.client import obtener_cliente_http


class ExtraerSCJN:
    def __init__(self):
        # Corregido: Inicialización centralizada con formato estricto JSON para APIs
        self.session = obtener_cliente_http(es_api=True)

        self.output_path = BRONZE_DIR / "scjn" / "sentencias"
        self.output_path.mkdir(parents=True, exist_ok=True)

        self.pagina_n = 0
        self.params = {"page": self.pagina_n, "offset": 0, "limit": 1000}
        self.url_base = (
            "https://bicentenario.scjn.gob.mx/repositorio-scjn/api/v1/engroses/"
        )
        self.diccionario_completo = {}
        self.diccionario_ids_urls = {}

    def request_api_ids(self):
        API_URL = f"{self.url_base}ids"
        try:
            page = self.session.get(
                API_URL, params=self.params, verify=False, timeout=15
            )
            if page.status_code == 200:
                lista_ids = page.json()
                self.diccionario_ids_urls = {
                    id_val: f"{self.url_base}{id_val}" for id_val in lista_ids
                }
                print(
                    f"🔎 [Página {self.pagina_n}] IDs obtenidos: {len(self.diccionario_ids_urls)}",
                    flush=True,
                )
            else:
                print(f"❌ Error API SCJN: {page.status_code}")
        except Exception as e:
            print(f"❌ Error en request_api_ids: {e}")

    def obtener_urls_docx(self):
        filtros = ["urlInternet", "expediente"]
        resultados = {}

        for clave, valor in self.diccionario_ids_urls.items():
            try:
                r = self.session.get(valor, verify=False, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    resultados[clave] = {k: v for k, v in data.items() if k in filtros}
            except Exception:
                pass
        return resultados

    def iterar_paginas(self, max_paginas=1):
        print(
            f"🚀 Iniciando extracción masiva de SCJN en: {self.output_path}\n",
            flush=True,
        )
        for _ in range(max_paginas):
            self.pagina_n += 1
            self.params["page"] = self.pagina_n

            self.request_api_ids()
            nuevos_datos = self.obtener_urls_docx()
            if nuevos_datos:
                self.diccionario_completo.update(nuevos_datos)
                print(
                    f"✨ Página {self.pagina_n} terminada. Total: {len(self.diccionario_completo)}"
                )
            time.sleep(1.5)

    def guardar_resultados(self):
        if not self.diccionario_completo:
            print("⚠️ No hay datos para almacenar.")
            return

        ruta_json = self.output_path / "scjn_sentencias.json"
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(self.diccionario_completo, f, ensure_ascii=False, indent=4)
        print(f"💾 JSON guardado en: {ruta_json}")

        # Corregido: Usamos el método nativo de asignación from_dict
        ruta_csv = self.output_path / "scjn_sentencias.csv"
        df = pd.DataFrame.from_dict(self.diccionario_completo, orient="index")
        df.to_csv(ruta_csv, index_label="id_scjn")
        print(f"Csv guardado en: {ruta_csv}")


if __name__ == "__main__":
    try:
        procesador = ExtraerSCJN()
        procesador.iterar_paginas(max_paginas=1)
        procesador.guardar_resultados()
    except Exception:
        print("Falla crítica en el flujo principal:")
        traceback.print_exc()
