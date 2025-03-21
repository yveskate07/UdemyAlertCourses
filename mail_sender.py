import smtplib
from email.mime.multipart import MIMEMultipart
from  email.mime.text import MIMEText
from environ import environ
from logs_writer import log_writer
import os
from email.message import EmailMessage

# env variable
env = environ.Env()

# script_path
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
# log_path
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs','logs.log')

# retrieving env variables
env.read_env(env_file=env_path)


# function to clear all logs messages
def clear_log_file():
    """Efface le contenu du fichier .log"""
    with open(log_path, 'w') as file:
        pass  # Ouvre le fichier en mode écriture et le vide

# function to retrieve all logs messages
def read_log_file():
    """Retourne le contenu du fichier .log"""
    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Fichier introuvable."
    except Exception as e:
        return f"Erreur : {e}"

# function to update an env variable
def update_env_variable(key, new_value):

    with open(env_path, "r") as file:
        lines = file.readlines()

    # Vérifier si la clé existe et la mettre à jour
    updated = False
    with open(env_path, "w") as file:
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={new_value}\n")
                updated = True
            else:
                file.write(line)

        # Si la clé n'existe pas, on l'ajoute
        if not updated:
            file.write(f"{key}={new_value}\n")


# function to generate a html table code out of a dataframe given
def generate_html_table(df):

    table_html = """
    <table border="1" style="border-collapse: collapse; width: 100%; text-align: left;">
        <thead>
            <tr>
                <th style='text-align: center;'>Cours</th>
                <th style='text-align: center;'>Description</th>
                <th style='text-align: center;'>Prix</th>
                <th style='text-align: center;'>Voir</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in df.iterrows():
        course_name = row['Name']
        price = row['Price']
        link = row["Course url"]
        image_url = row["Image"]

        table_html += f"""
            <tr>
                <td>
                    <div style='display: flex; align-items: center;'>
                        <img src='{image_url}' alt='Image de {course_name}' style='width:50px; height:50px; margin-right: 10px;'>
                        <p style='margin: 0;'>{course_name}</p>
                    </div>
                </td>
                <td>{row['Description']}</td>
                <td style='text-align: center;'>{price}</td>
                <td style='text-align: center;'><a href="{link}">Voir</a></td>
            </tr>
        """

    table_html += """
        </tbody>
    </table>
    """

    return table_html


# function to send alert mail containing all course informations i'm interested with
def send_alert_mails(df, receiver="kateyveschadrac@gmail.com"): # you can change receiver if needed

    if env.bool("MAIL_SENT"):
        return

    template_html = generate_html_table(df)

    # Création du message
    message = MIMEMultipart("alternative")
    message["Subject"] = "You got some discounts on your wishlist"
    message["From"] = env("SENDER")
    message["To"] = receiver

    # Ajout du contenu HTML
    html_part = MIMEText(template_html, "html")
    message.attach(html_part)

    # Envoi de l'email
    with smtplib.SMTP(env("SMTP_SERVER"), env("SMTP_PORT")) as server:
        server.starttls()  # Chiffrement TLS
        server.login(env("SENDER"), env("PASSWORD"))
        server.sendmail(env("SENDER"), receiver, message.as_string())
        log_writer("✅ Email d'alerte envoyé avec succès !")
        update_env_variable('MAIL_SENT', 'True')


# function to send mails containing log file if there are some log files
def send_log_mails():
    # Configuration
    EMAIL_ADDRESS = env("SENDER")  # Remplacez par votre email
    EMAIL_PASSWORD = env("PASSWORD")  # Remplacez par votre mot de passe (ou App Password)
    DESTINATAIRE = "kateyveschadrac@gmail.com"  # Remplacez par l'email du destinataire

    log_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'txt', 'logs.txt')


    # Création du message
    msg = EmailMessage()
    msg["Subject"] = "Rapport de logs"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = DESTINATAIRE
    msg.set_content("Bonjour,\n\nVeuillez trouver ci-joint le fichier de logs.\n\nCordialement.")

    # Ajout du fichier en pièce jointe
    if os.path.exists(log_txt_path):
        with open(log_txt_path, "rb") as file:
            msg.add_attachment(file.read(), maintype="application", subtype="octet-stream", filename=log_txt_path)
    else:
        return log_writer(f"⚠️ Fichier '{log_txt_path}' non trouvé. Aucune pièce jointe envoyée.", 'error')

    # Envoi du mail via SMTP
    try:
        with smtplib.SMTP(env("SMTP_SERVER"), env("SMTP_PORT")) as server:  # Adapter l'hôte SMTP si nécessaire
            server.starttls()  # Sécuriser la connexion
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            log_writer("✅ Email de logs envoyé avec succès !")
            clear_log_file()
    except Exception as e:
        log_writer(f"❌ Erreur lors de l'envoi de l'email : {e}", 'error')
