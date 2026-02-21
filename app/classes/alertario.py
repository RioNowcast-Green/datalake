from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from app.config.selenium_config import SeleniumConfig

import os
import shutil
import time
import zipfile
from tqdm import tqdm
from typing import Literal

from app.utils.download_manager import DownloadManager

import pandas as pd
from io import StringIO

class AlertaRio:

    def __init__(self):
        self.download_manager = DownloadManager()
        self.download_dir = self.download_manager.get_download_dir()
    
    def scrap_pluv(self, year):

        selenium_cfg = SeleniumConfig(headless=False)
        self.driver = selenium_cfg.create_driver()

        try:
            print(f"Iniciando download dos dados pluviométricos para o ano {year}...")
            self.driver.get("http://websempre.rio.rj.gov.br/dados/pluviometricos/plv/")

            select_element = Select(
                self.driver.find_element(By.ID, "all_choice")
            )
            select_element.select_by_value(year)

            self.driver.find_element(
                By.XPATH,
                "/html/body/div/form/table/tbody/tr[34]/td[3]"
            ).click()

            self.driver.find_element(
                By.XPATH,
                "//input[@type='submit' and @value='Download']"
            ).click()

            downloaded_file = self._wait_for_zip_download(timeout=60)

            if not downloaded_file:
                raise RuntimeError("Download não foi concluído.")

            if os.path.getsize(downloaded_file) == 0:
                raise RuntimeError("Arquivo ZIP está vazio.")

            if not zipfile.is_zipfile(downloaded_file):
                raise RuntimeError("Arquivo baixado não é um ZIP válido.")

            print(f"Download concluído")
        finally:
            self.driver.quit()

        self.download_manager.unzip_files(downloaded_file)
        self._organize_files(type="pluv")

    def _wait_for_zip_download(self, timeout=60):
        start_time = time.time()

        while time.time() - start_time < timeout:
            files = os.listdir(self.download_dir)

            zip_files = [
                f for f in files
                if f.endswith(".zip") and not f.endswith(".crdownload")
            ]

            if zip_files:
                return os.path.join(self.download_dir, zip_files[0])

            time.sleep(1)

        return None

    def _organize_files(self, type: Literal["met", "pluv"]):
        
        if type == "pluv":
          SOURCE_DIR = self.download_dir+"/DadosPluviometricos"
          TARGET_ROOT = self.download_dir+"/pluviometric/alertario"
        elif type == "met":
          SOURCE_DIR = self.download_dir+"/DadosMeteorologicos"
          TARGET_ROOT = self.download_dir+"/meteorological/alertario"
        else:
          raise ValueError("Tipo inválido. Use 'met' ou 'pluv'.")

        for filename in os.listdir(SOURCE_DIR):
            source_path = os.path.join(SOURCE_DIR, filename)

            if not os.path.isfile(source_path):
                continue

            try:
                parts = filename.split("_")

                city = "_".join(parts[:-2])
                year = parts[-2][:4]

                target_dir = os.path.join(TARGET_ROOT, city, year)
                os.makedirs(target_dir, exist_ok=True)

                shutil.move(
                    source_path,
                    os.path.join(target_dir, filename)
                )

            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")

        shutil.rmtree(SOURCE_DIR)

    def read_pluviometric_txt(self, file_path):
        rows = []

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        data_started = False

        for line in lines:
            if line.strip().startswith("Dia"):
                data_started = True
                continue

            if not data_started or not line.strip():
                continue

            parts = line.split()

            dia = parts[0]
            hora = parts[1]

            values = parts[2:]

            if len(values) == 5:
                hbv = None
                vals = values
            else:
                hbv = values[0]
                vals = values[1:]

            while len(vals) < 5:
                vals.append(None)

            rows.append([dia, hora, hbv] + vals)

        df = pd.DataFrame(
            rows,
            columns=["dia", "hora", "hbv", "station", "15min", "1h", "4h", "24h", "96h"]
        )

        return df


    def load_pluviometric_data(self, year_filter, station):
        BASE_PATH = self.download_dir + "/pluviometric/alertario"
        dfs = []

        station_path = os.path.join(BASE_PATH, station)
        if not os.path.isdir(station_path):
            raise ValueError(f"Estação '{station}' não encontrada em {BASE_PATH}")

        year_path = os.path.join(station_path, year_filter)
        if not os.path.exists(year_path):
            raise ValueError(f"Nenhum dado encontrado para estação={station}, ano={year_filter}")

        files = [f for f in os.listdir(year_path) if f.endswith(".txt")]

        for file in files:
            full_path = os.path.join(year_path, file)
            df = self.read_pluviometric_txt(full_path)

            if df is None or df.empty:
                continue

            df["station"] = station
            dfs.append(df)

        if not dfs:
            raise ValueError(f"Nenhum arquivo encontrado para estação={station}, ano={year_filter}")

        return (
            pd.concat(dfs, ignore_index=True)
            .sort_values(by=["station", "dia", "hora"])
        )
    
    def get_stations(self):
        
        return [
            "alto_da_boa_vista",
            "anchieta",
            "av_brasil_mendanha",
            "bangu",
            "barrinha",
            "campo_grande",
            "cidade_de_deus",
            "copacabana",
            "grajau",
            "grajau_jacarepagua",
            "grande_meier",
            "grota_funda",
            "guaratiba",
            "ilha_do_governador",
            "iraja",
            "jardim_botanico",
            "laranjeiras",
            "madureira",
            "penha",
            "piedade",
            "recreio",
            "riocentro",
            "rocinha",
            "santa_cruz",
            "santa_teresa",
            "sao_cristovao",
            "saude",
            "sepetiba",
            "tanque",
            "tijuca",
            "tijuca_muda",
            "urca",
            "vidigal",
        ]