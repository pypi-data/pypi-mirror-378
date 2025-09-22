"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
class DownloadLibraries():
    def download(self):
        from os import listdir, path, makedirs
        from requests import get
        def download_libraries(repository_url='https://api.github.com/repos/sapiens-technology/Libs/contents/', destination_directory='./'):
            def download_file(url, local_path):
                response = get(url)
                with open(local_path, "wb") as file: file.write(response.content)
            def download_repository(url, destination_directory):
                response = get(url)
                if response.status_code == 200:
                    contents = response.json()
                    for content in contents:
                        if content["type"] == "file": download_file(content["download_url"], path.join(destination_directory, content["name"]))
                        elif content["type"] == "dir":
                            new_directory = path.join(destination_directory, content["name"])
                            makedirs(new_directory, exist_ok=True)
                            download_repository(content["url"], new_directory)
            makedirs(destination_directory, exist_ok=True)
            download_repository(repository_url, destination_directory)
        def check_so_files(directory: str) -> bool:
            try: return len([file for file in listdir(directory) if file.endswith('.so')]) >= 21
            except: return False
        installation_directory = path.dirname(__file__)
        if not check_so_files(directory=installation_directory): download_libraries(destination_directory=installation_directory)
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library for optimizing the Artificial Intelligence models of Sapiens Technology®, and its disclosure, distribution, #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
