import os
import sys
import smtplib
import requests
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import datetime

URL_A_SURVEILLER = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

TEXTES_INDISPONIBILITE = [
    "out of stock",
]

EMAIL_EXPEDITEUR = os.environ["EMAIL_EXPEDITEUR"]
MOT_DE_PASSE_APPLICATION = os.environ["MOT_DE_PASSE_APPLICATION"]
EMAIL_DESTINATAIRE = os.environ["EMAIL_DESTINATAIRE"]
SERVEUR_SMTP = "smtp.gmail.com"
PORT_SMTP = 587


def verifier_disponibilite(url):
    headers = {"User-Agent": "AlerteMoi-Prototype/1.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(reponse.text, "html.parser")
    texte_page = soup.get_text(separator=" ", strip=True).lower()

    for texte_indispo in TEXTES_INDISPONIBILITE:
        if texte_indispo in texte_page:
            return False
    return True


def envoyer_email_alerte(url):
    sujet = "🚨 AlerteMoi - Disponibilité potentielle détectée"
    corps = (
        f"Une disponibilité a potentiellement été détectée.\n\n"
        f"Lien : {url}\n\n"
        f"Détecté le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
    )
    message = MIMEText(corps, "plain", "utf-8")
    message["Subject"] = sujet
    message["From"] = EMAIL_EXPEDITEUR
    message["To"] = EMAIL_DESTINATAIRE

    with smtplib.SMTP(SERVEUR_SMTP, PORT_SMTP) as serveur:
        serveur.starttls()
        serveur.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_APPLICATION)
        serveur.sendmail(EMAIL_EXPEDITEUR, EMAIL_DESTINATAIRE, message.as_string())


if __name__ == "__main__":
    resume = os.environ.get("GITHUB_STEP_SUMMARY")

    try:
        if verifier_disponibilite(URL_A_SURVEILLER):
            message = "🚨 Disponibilité potentielle détectée ! Email envoyé."
            envoyer_email_alerte(URL_A_SURVEILLER)
        else:
            message = "✅ Aucune disponibilité pour le moment."

        print(message)
        if resume:
            with open(resume, "a") as f:
                f.write(f"## Résultat de la vérification\n\n{message}\n")

    except requests.RequestException as erreur:
        message = f"❌ Erreur : {erreur}"
        print(message)
        if resume:
            with open(resume, "a") as f:
                f.write(f"## Résultat de la vérification\n\n{message}\n")
        sys.exit(1)
