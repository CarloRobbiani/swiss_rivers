import zipfile
import os


def extract_zip():
    files = [f for f in os.listdir("C:/Users/carlo/Downloads/WT_Models")]

    for file in files:
        with zipfile.ZipFile(f"C:/Users\carlo/Downloads/WT_Models/{file}","r") as zip_ref:
            station = file[0:4]
            dir = f"models/{station}"
            zip_ref.extractall(dir)

def create_folders():
    files = os.listdir("models")

    for f in files:
        os.mkdir(f"predictions/{f}")

if __name__ == "__main__":
    create_folders()