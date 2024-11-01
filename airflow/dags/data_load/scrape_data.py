import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from data_load.data_storage_log import log_success, log_error
import time
import os

def scrape_pdf_links(driver, summary_page_link):
    """
    Extracts the PDF link from the summary page.
    """
    try:
        # Visit the summary page link
        driver.get(summary_page_link)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'content-asset--primary'))
        )

        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        parsed_content = BeautifulSoup(page_source, 'html.parser')

        # Find the PDF download link by class name and href
        pdf_element = parsed_content.find('a', class_='content-asset--primary')
        if pdf_element and pdf_element['href']:
            pdf_url = pdf_element['href']
            return pdf_url if pdf_url.startswith('http') else f"https://rpc.cfainstitute.org{pdf_url}"  # Handle relative URLs
        else:
            return None
    except Exception as e:
        log_error(f"Error extracting PDF link from {summary_page_link}: {e}")
        return None

def scrape_data(**kwargs):
    try:
        base_url = "https://rpc.cfainstitute.org/en/research-foundation/publications"
        # Set up headless Chrome web driver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--window-size=1920x1080')
        options.binary_location = "/usr/bin/chromium" 
        driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)

        # Initialize an empty DataFrame to store results
        df = pd.DataFrame(columns=['Title', 'Image_URL', 'Brief_Summary', 'Summary_Page_Link', 'PDF_Link'])

        # Load the base page to find pagination
        driver.get(base_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'CoveoResult')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract total number of pages from the pagination section using the updated selector
        pagination_container = soup.select_one('ul.coveo-pager-list')  # Adjusted selector
        if not pagination_container:
            log_error("Pagination container not found.")
            return df.to_dict()  # Return empty DataFrame if no pagination found

        # Get all page numbers from the pagination container
        page_links = pagination_container.find_all('li')
        page_numbers = [int(li.text) for li in page_links if li.text.isdigit()]
        total_pages = max(page_numbers) if page_numbers else 1  # Default to 1 if no pages are found

        log_success(f"Total pages to scrape: {total_pages}")

        # Iterate over all page numbers and scrape data
        for page_number in range(1, total_pages + 1):
            url = f"{base_url}#first={(page_number - 1) * 10}&sort=%40refreadingcurriculumyear%20descending"
            log_success(f"Scraping page {page_number} of {total_pages} - URL: {url}")
            
            # Navigate to the page
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'CoveoResult')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract each publication item on the page
            items = soup.find_all('div', class_='coveo-list-layout CoveoResult')
            if not items:
                log_success(f"No more items found on page {page_number}. Stopping.")
                break

            for div in items:
                try:
                    title_element = div.find('a', class_='CoveoResultLink')
                    title = title_element.text.strip() if title_element else ''
                    summary_page_link = title_element['href'] if title_element else ''
                    summary_page_link = f"{summary_page_link}" if summary_page_link else ''

                    image_url = div.find('img', class_='coveo-result-image')['src'] if div.find('img', class_='coveo-result-image') else ''
                    image_url = f'https://rpc.cfainstitute.org{image_url}' if image_url and not image_url.startswith('http') else image_url

                    brief_summary = div.find('div', class_='result-body').text.strip() if div.find('div', class_='result-body') else ''

                    # Use scrape_pdf_links to fetch the PDF link from the summary page
                    pdf_link = scrape_pdf_links(driver, summary_page_link) if summary_page_link else None

                    # Add the extracted data to the DataFrame
                    df.loc[len(df)] = {
                        'Title': title,
                        'Image_URL': image_url,
                        'Brief_Summary': brief_summary,
                        'Summary_Page_Link': summary_page_link,
                        'PDF_Link': pdf_link
                    }

                except Exception as e:
                    log_error(f"Error extracting data from item on page {page_number}: {e}")

            # Small delay to avoid overloading the server
            time.sleep(2)

        driver.quit()
        log_success("Data scraping completed.")

        # Define the file path for saving the CSV
        csv_file_path = "/opt/airflow/dags/output/cfa_publications.csv"
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
        
        # Save the DataFrame as a CSV file
        df.to_csv(csv_file_path, index=False)
        log_success(f"Data saved to CSV at {csv_file_path}.")

        # Print the DataFrame for verification

        # Push the DataFrame to XCom as a dictionary
        return df.to_dict()  # Convert DataFrame to dictionary before pushing

    except Exception as e:
        log_error(f"Error in scrape_data: {e}")
        raise e