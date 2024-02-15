import os
import gdown
import pandas as pd
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import yaml

def load_config(config_path="config.yaml"):
    '''
    Load configuration parameters from a YAML file.
    Parameters:
    - config_path (str): Path of config.yaml file
    Returns:
    - dict: A dictionary containing the configuration parameters.
    '''
    
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    return config


def offload_from_google_drive(config):
    """
    Offload a file from Google Drive to a local directory with a specified file name.

    Parameters:
    - file_id (str): Google Drive file ID.
    - output_directory (str): Local directory path to save the downloaded file.
    - local_file_name (str): Local file name for the downloaded file.
    - overwrite (bool): Whether to overwrite the file if it already exists (default: False).
    """
    
    file_id = config["google_drive"]["file_id"]
    output_directory = config["google_drive"]["output_directory"]
    local_file_name = config["google_drive"]["local_file_name"]
    overwrite = config["google_drive"]["overwrite"]
    
    # Authenticate with Google Drive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    # Create GoogleDrive instance with authenticated GoogleAuth instance
    drive = GoogleDrive(gauth)

    # Get the file with the provided file ID
    file = drive.CreateFile({'id': file_id})

    # Set the local destination path
    destination_path = output_directory + "/" + local_file_name

    # Check if the file already exists locally
    if not overwrite and os.path.exists(destination_path):
        print(f"File '{destination_path}' already exists. Set 'overwrite=True' to replace it.")
        return

    # Download the file
    file.GetContentFile(destination_path)

    print(f"File '{file['title']}' has been offloaded to '{destination_path}'.")


def load_dictionary(file_path,config_path):
    '''
    Load a dictionary from a file.
    Parameters:
    - file_path (str): Path to the file to load.
    - config_path (str): Path of config.yaml file
    Returns:
    - set: Set of words in the dictionary.
    '''
    
    config = load_config(config_path)
    encodings = config["dictionary"]["encodings"]
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                words = [line.strip() for line in file]
            return set(words)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to decode file {file_path} with specified encodings: {encodings}")


def scrapper(config):
    """
    Scrape text content from a specified element on a webpage.

    Parameters:
    - url (str): The URL of the webpage to scrape.
    - headers (dict): Optional headers to include in the request.
    - parser (str): The HTML parser to use (default: 'html.parser').
    - element (str): HTML element to search for (default: 'div').
    - class_name (str): Class name of the HTML element (default: None).
    - strip (bool): Whether to strip leading and trailing whitespaces from the text (default: True).

    Returns:
    - str: The scraped text content.
    """
    
    url = config["web_scraper"]["url"]
    headers = config["web_scraper"]["headers"]
    parser = config["web_scraper"]["parser"]
    element = config["web_scraper"]["element"]
    class_name = config["web_scraper"]["class_name"]
    strip = config["web_scraper"]["strip"]
    
    # Make the request to the webpage
    webpage = requests.get(url, headers=headers).text

    # Parse the webpage content with BeautifulSoup
    soup = BeautifulSoup(webpage, parser)

    # Find the specified HTML element with the provided class name
    if class_name:
        element_content = soup.find(element, class_=class_name)
    else:
        element_content = soup.find(element)

    # Get the text content and optionally strip whitespaces
    text = element_content.get_text(strip=strip) if element_content else None

    return text
