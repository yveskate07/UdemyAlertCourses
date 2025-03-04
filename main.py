import json
import os
import time
import pandas as pd
from requests import get
from bs4 import BeautifulSoup as bs
from logs_writer import log_writer
from mail_sender import send_alert_mails, send_log_mails
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


subject_of_interest = "django"
# WebDriver Configuration
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def get_urls(filepath):
    # Test the filepath to ensure it exists
    if os.path.exists(filepath):
        f = open(filepath, "r")
        urls = json.load(f)
        f.close()
        return urls

    else:
        log_writer("Erreur, le fichier n'existe pas.", 'error')
        return ImportError

if __name__ == "__main__":
    while True:
        try:
            urls = get_urls(os.path.join(os.path.dirname(os.path.abspath(__file__)), "urls.json")) # retrieving my urls from urls.json

        except Exception as e:
            log_writer(f"Erreur lors de l'obtention des urls. Details: {e}", 'error')

        else:
            data = []
            for subject in urls.keys():
                for url in urls[subject]:
                    driver.get(url)
                    try:

                        time.sleep(3)

                        res = get(url) # retrieving the html code of the page
                        soup = bs(res.text, 'html.parser')

                        course_name = driver.find_element(By.CLASS_NAME, 'ud-heading-xxl clp-lead__title clp-lead__title--small').text # course's name
                        description = driver.find_element(By.CLASS_NAME, "ud-text-lg clp-lead__headline").text # description
                        price = driver.find_element(By.CLASS_NAME, "base-price-text-module--price-part---xQlz ud-clp-discount-price ud-heading-xl").text # price
                        devise = "Euro (€)" if "€" in price else "USD ($)" # currency
                        price = price.strip(" $US").strip("$") if devise == "USD ($)" else price.strip("€") # cleaning price
                        next_topic = subject == subject_of_interest # if the subject related will be the next one that I will study
                        img_link = driver.find_element(By.TAG_NAME, "img").get_attribute("src") # image link
                        course_url = url # course link
                        dic = {"Name": course_name, "Description":description,"Price": float(price), "Currency": devise, "Interested": next_topic, 'Image':img_link, 'Course url':url}
                        data.append(dic)

                    except Exception as e:
                        log_writer(f"Erreur lors du scrapping du cours: {url}. Details: {e}",'error')

            # close driver
            driver.quit()

            # storing datas in a DataFrame
            df = pd.DataFrame(data)

            courses_to_be_notified = df[df['Price']<=13.99] # filtering the courses that are discounted
            if not courses_to_be_notified.empty:
                log_writer("Des reductions sur vos cours ont été trouvées, envoi des mails...")
                send_alert_mails(courses_to_be_notified)

            log_writer("Sauvegarde des données dans un fichier csv.")
            df.to_csv("csv\\courses_tracked_prices.csv", index=False) # storing the datas in a csv-file

        send_log_mails() # sending the log file if there is one

        time.sleep(1800)