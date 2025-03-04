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

env.read_env(env_file=env_path)


def send_alert_mails(df):
    html_rows = ""
    num_of_html_rows = {0:len(df)/3}.get(len(df)%3,round(len(df)/3))
    for i in range(num_of_html_rows):
        row1, row2, row3 = df.iloc[1+3*i].to_dict(), df.iloc[2+3*i].to_dict(), df.iloc[3+3*i].to_dict()
        html_rows += f"""
        <div class='row justify-content-center'>
            <div class='col-md-4 col-sm-4 p-2' style="max-width: 28%;">
                <a href='{row1['Course url']}'>
                    <div style="height: 65%;">
                        <img style="width: 100%;" src='{row1['Image']}' alt="Vignette du cours">
                    </div>
                    <div style="height: 35%;">
                        <h1 >'{row1['Name']}'</h1>
                        <h3 class="pb-5">'{row1['Description']}'</h3>
                        <h4 class="badge bg-warning float-start">'{row1['Price']}'</h4>
                    </div>
                </a>
            </div>
            <div class='col-md-4 col-sm-4 p-2' style="max-width: 28%;">
                <a href='{row2['Course url']}'>
                    <div style="height: 65%;">
                        <img style="width: 100%;" src='{row2['Image']}' alt="Vignette du cours">
                    </div>
                    <div style="height: 35%;">
                        <h1 >'{row2['Name']}'</h1>
                        <h3 class="pb-5">'{row2['Description']}'</h3>
                        <h4 class="badge bg-warning float-start">'{row2['Price']}'</h4>
                    </div>
                </a>
            </div>
            <div class='col-md-4 col-sm-4 p-2' style="max-width: 28%;">
                <a href='{row3['Course url']}'>
                    <div style="height: 65%;">
                        <img style="width: 100%;" src='{row3['Image']}' alt="Vignette du cours">
                    </div>
                    <div style="height: 35%;">
                        <h1 >'{row3['Name']}'</h1>
                        <h3 class="pb-5">'{row3['Description']}'</h3>
                        <h4 class="badge bg-warning float-start">'{row3['Price']}'</h4>
                    </div>
                </a>
            </div>
        </div>"""


    template_html = f"""
        <!DOCTYPE html>
        <html lang='en'>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css' rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
            <title>Document</title>
        </head>
        <body>
            <div class="container">
                <h1 class="text-center text-primary">Vos cours en promotion</h1>
                { html_rows }
            </div>
        </body>
        </html>
        """

    # Création du message
    message = MIMEMultipart("alternative")
    message["Subject"] = "You got some discounts on your wishlist"
    message["From"] = env("SENDER")
    message["To"] = "kateyveschadrac@gmail.com"

    # Ajout du contenu HTML
    html_part = MIMEText(template_html, "html")
    message.attach(html_part)

    # Envoi de l'email
    with smtplib.SMTP(env("SMTP_SERVER"), env("SMTP_PORT")) as server:
        server.starttls()  # Chiffrement TLS
        server.login(env("SENDER"), env("PASSWORD"))
        server.sendmail(env("SENDER"), "kateyveschadrac@gmail.com", message.as_string())
        log_writer("✅ Email d'alerte envoyé avec succès !")


def send_log_mails(FICHIER_LOG = "logs\\logs.log"):
    # Configuration
    EMAIL_ADDRESS = env("SENDER")  # Remplacez par votre email
    EMAIL_PASSWORD = env("PASSWORD")  # Remplacez par votre mot de passe (ou App Password)
    DESTINATAIRE = "kateyveschadrac@gmail.com"  # Remplacez par l'email du destinataire


    # Création du message
    msg = EmailMessage()
    msg["Subject"] = "Rapport de logs"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = DESTINATAIRE
    msg.set_content("Bonjour,\n\nVeuillez trouver ci-joint le fichier de logs.\n\nCordialement.")

    # Ajout du fichier en pièce jointe
    if os.path.exists(FICHIER_LOG):
        with open(FICHIER_LOG, "rb") as file:
            msg.add_attachment(file.read(), maintype="application", subtype="octet-stream", filename=FICHIER_LOG)
    else:
        return log_writer(f"⚠️ Fichier '{FICHIER_LOG}' non trouvé. Aucune pièce jointe envoyée.", 'error')

    # Envoi du mail via SMTP
    try:
        with smtplib.SMTP(env("SMTP_SERVER"), env("SMTP_PORT")) as server:  # Adapter l'hôte SMTP si nécessaire
            server.starttls()  # Sécuriser la connexion
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            log_writer("✅ Email de logs envoyé avec succès !")
            os.remove(FICHIER_LOG)
    except Exception as e:
        log_writer(f"❌ Erreur lors de l'envoi de l'email : {e}", 'error')
