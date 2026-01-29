from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from app.config.selenium_config import SeleniumConfig

import os
import shutil
from typing import Literal

from app.utils.download_manager import DownloadManager

class AlertaRio:

    def __init__(self):
        self.download_manager = DownloadManager()
        self.download_dir = self.download_manager.get_download_dir()
    
    def scrap_pluv(self, year):
        
        selenium_cfg = SeleniumConfig(
            headless=False, 
        )

        self.driver = selenium_cfg.create_driver()
        
        self.driver.get("http://websempre.rio.rj.gov.br/dados/pluviometricos/plv/")

        # Mudar o ano para todas as seleções
        select_element = Select(
            self.driver.find_element(By.ID, "all_choice")
        )

        select_element.select_by_value(year)

        # Seleciona todas as estações pluviométricas
        self.driver.find_element(By.XPATH, "/html/body/div/form/table/tbody/tr[34]/td[3]").click()

        # Baixar os arquivos de cada estação
        self.driver.find_element(
            By.XPATH, "//input[@type='submit' and @value='Download']"
        ).click()

        self.download_manager.wait_for_download(self.download_dir)

        self.driver.quit()

        self.download_manager.unzip_files("DadosPluviometricos.zip")

        self._organize_files(type="pluv")


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
