import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

class SeleniumConfig:

    def __init__(
        self,
        headless: bool = False,
        mime_types: str = (
            "application/pdf,"
            "application/zip,"
            "text/csv,"
            "application/octet-stream"
        ),
    ):
        self.headless = headless
        self.mime_types = mime_types

        self.datalake_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "..",
            "data",
        )
        self.download_dir = os.path.join(self.datalake_dir, "raw")

        os.makedirs(self.download_dir, exist_ok=True)

    def _firefox_options(self) -> Options:
        options = Options()

        if self.headless:
            options.add_argument("-headless")

        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", self.download_dir)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            self.mime_types,
        )
        options.set_preference("pdfjs.disabled", True)
        options.set_preference(
            "browser.download.manager.showWhenStarting", False
        )

        return options

    def create_driver(self) -> webdriver.Firefox:
        service = Service(GeckoDriverManager().install())
        options = self._firefox_options()
        return webdriver.Firefox(service=service, options=options)
