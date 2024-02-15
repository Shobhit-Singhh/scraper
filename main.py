import requests
from bs4 import BeautifulSoup
from utility_functions import load_config
from custom_parameters import calculate_metrics
import logging
import pandas as pd

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

def process_url(url_id, url, headers, parser, element, class_name, strip, results_df=None):
    '''
    Process a single URL and update the results DataFrame in real-time.
    Parameters:
    - url_id (int): The ID of the URL.
    - url (str): The URL to process.
    - headers (dict): Optional headers to include in the request.
    - parser (str): The HTML parser to use (default: 'html.parser').
    - element (str): HTML element to search for (default: 'div').
    - class_name (str): Class name of the HTML element (default: None).
    - strip (bool): Whether to strip leading and trailing whitespaces from the text (default: True).
    - results_df (DataFrame): The DataFrame to update with the results (default: None).
    Returns:
    - DataFrame: The updated DataFrame.
    '''
    
    # Make the request to the webpage
    webpage = requests.get(url, headers=headers, verify=True)
    if webpage.status_code != 404:
        logging.info(f"Webpage request successful for {url}")

        webpage = requests.get(url, headers=headers, verify=True).text
        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(webpage,'lxml')
        soup = BeautifulSoup(soup.prettify(), parser)

        # Extract text content from a specific div
        text = soup.find(element, class_= class_name).get_text(strip=strip)
        logging.info(f"Text extraction successful for {url}")

        # Calculate custom parameters
        metrics = calculate_metrics(text)

        # If results_df is not provided, create an empty DataFrame
        if results_df is None:
            results_df = pd.DataFrame(columns=['URL_ID','URL'])

        # Add the results to the DataFrame
        result_dict = {'URL_ID': url_id,'URL':url, **metrics}
        results_df = pd.concat([results_df, pd.DataFrame([result_dict])], ignore_index=True)

        # Save the updated DataFrame to a new Excel file (optional)
        results_df.to_excel("realtime_sheet.xlsx", index=False)
    else:
        logging.warning(f"Failed to fetch webpage for URL_ID {url_id} and URL {url}. Status code: {webpage.status_code}")

        # Handle the failure, mark the entire row with "ERROR 404"
        if results_df is None:
            results_df = pd.DataFrame(columns=['URL_ID',"URL"])
        result_dict = {'URL_ID': url_id,"URL":url, **{col: "ERROR 404" for col in results_df.columns[2:]}}
        results_df = pd.concat([results_df, pd.DataFrame([result_dict])], ignore_index=True)

        
    return results_df



def main():
    '''
    Main function.
    '''
    # Load the main configuration from config.yaml
    config_path_main = "config.yaml"
    config_main = load_config(config_path_main)
    logging.info("Config loaded successfully")

    # Load configuration for web scraping
    headers = config_main["web_scraper"]["headers"]
    parser = config_main["web_scraper"]["parser"]
    element = config_main["web_scraper"]["element"]
    class_name = config_main["web_scraper"]["class_name"]
    strip = config_main["web_scraper"]["strip"]
    logging.info("Web scraping configuration loaded successfully")

    # Read URLs from Excel sheet using pandas
    excel_path = "data/Input.xlsx"  # Update with your Excel file path
    df = pd.read_excel(excel_path)

    # Create an empty DataFrame to store the results
    results_df = pd.DataFrame(columns=['URL_ID'])

    # Process each URL and update the results DataFrame in real-time
    for index, row in df.iterrows():
        url_id = row['URL_ID']  
        url = row['URL']
        results_df = process_url(url_id, url, headers, parser, element, class_name, strip, results_df)

    # Save the final results DataFrame to a new Excel file
    results_df.to_excel("output.xlsx", index=False)

if __name__ == "__main__":
    main()