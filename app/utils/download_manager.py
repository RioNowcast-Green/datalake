import os
import time
import zipfile

class DownloadManager:
    
    def __init__(self):
        self.download_dir = self.get_download_dir()

    def get_download_dir(self):
        datalake_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "..",
            "data",
        )
        download_dir = os.path.join(datalake_dir, "raw")
        os.makedirs(download_dir, exist_ok=True)

        return download_dir
    
    def wait_for_download(self, directory, timeout=300):
        seconds = 0

        while seconds < timeout:
            files = os.listdir(directory)

            if not any(file.endswith(".part") for file in files):
                return True

            time.sleep(1)
            seconds += 1

        raise TimeoutError("Download não finalizou dentro do tempo limite")


    def unzip_files(self, file):
        zip_path = os.path.join(self.download_dir, file)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(zip_path.replace(".zip", ""))

        os.remove(zip_path)