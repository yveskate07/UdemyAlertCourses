import json
import os
import time
import pandas as pd
from requests import get
from bs4 import BeautifulSoup as bs
from logs_writer import log_writer
from mail_sender import send_alert_mails, send_log_mails, update_env_variable, read_log_file

# subject I'm interested with
subject_of_interest = "django"

# function for retrieving urls from urls.json
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

    # loop of scrapping: occurs every hour
    while True:

        try:
            urls = get_urls(os.path.join(os.path.dirname(os.path.abspath(__file__)), "urls.json")) # retrieving my urls from urls.json

        except Exception as e:
            log_writer(f"Erreur lors de l'obtention des urls. Details: {e}", 'error')

        else:
            data = []
            for subject in urls.keys():
                for url in urls[subject]:
                    try:
                        res = get(url) # retrieving the html code of the page
                        soup = bs(res.text, 'html.parser')

                        course_name = soup.find('h1', class_='ud-heading-xxl clp-lead__title clp-lead__title--small').text # course's name
                        description = soup.find('div', class_="ud-text-lg clp-lead__headline").text # description

                        json_str = soup.find("script", {"type": "application/ld+json"}).text
                        my_json_data = json.loads(json_str)

                        price = my_json_data['@graph'][0]['offers'][0]['price'] # price

                        devise = my_json_data['@graph'][0]['offers'][0]['priceCurrency'] # currency

                        next_topic = subject == subject_of_interest # if the subject related will be the next one that I will study
                        img_link = soup.find('span', class_="intro-asset--img-aspect--3gluH").find('img')['src'] # image link

                        dic = {"Name": course_name, "Description":description,"Price": float(price), "Currency": devise, "Interested": next_topic, 'Image':img_link, 'Course url':url}
                        data.append(dic)

                    except Exception as e:
                        log_writer(f"Erreur lors du scrapping du cours: {url}. Details: {e}",'error')


            # storing datas in a DataFrame
            df = pd.DataFrame(data)

            log_writer("Sauvegarde des données dans un fichier csv.")
            df.to_csv(os.path.join("csv","courses_tracked_prices.csv"), index=False)  # storing the datas in a csv-file

            courses_to_be_notified = df[(df['Price']<=13.99) & (df["Interested"] == True)] # filtering the courses that are discounted and i'm interesyted with
            if not courses_to_be_notified.empty:
                log_writer("Des reductions sur vos cours ont été trouvées, envoi des mails...")
                send_alert_mails(courses_to_be_notified)

            else: # if no course is discounted, then we update the variable MAIL_SENT in the .env file
                update_env_variable('MAIL_SENT','False')


        if read_log_file()!="": # if there are some logs in the log file
            send_log_mails() # sending the log file if there is one

        time.sleep(3600) # next scrapping is in the next hour

