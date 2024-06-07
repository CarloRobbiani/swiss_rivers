import zipfile
import os

#method to find folders with files that have prefix
def find_folders_with_files(directory, prefix):
    matching_folders = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith(prefix):
                matching_folders.append(root)
                break  # Stop after finding the first matching file in this folder

    return matching_folders

#method that extracts the model files from downloads
def extract_zip():
    files = [f for f in os.listdir("C:/Users/carlo/Downloads/WT_Models")]

    for file in files:
        with zipfile.ZipFile(f"C:/Users\carlo/Downloads/WT_Models/{file}","r") as zip_ref:
            station = file[0:4]
            dir = f"models/{station}"
            zip_ref.extractall(dir)

#method that creates folders in predictions corresponding to the model files
def create_folders():
    files = os.listdir("models")

    for f in files:
        if not os.path.exists(f"predictions/{f}"):
            os.mkdir(f"predictions/{f}")

if __name__ == "__main__":
    #create_folders()
    extract_zip()
    #print(find_folders_with_files("models", "Jun05"))