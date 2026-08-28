import os
import sys
import smtplib
import requests
from email.mime.text import MIMEText
from datetime import datetime

URL_API = "https://padelspot.app/api/public/explore"

PARAMETRES = {
    "city": "paris",
    "date": "2026-08-29",
    "time": "20:00",
}

EMAIL_EXPEDITEUR = os.environ["EMAIL_EXPEDITEUR"]
MOT_DE_PASSE_APPLICATION = os.environ["MOT_DE_PASSE_APPLICATION"]
EMAIL_DESTINATAIRE = os.environ["EMAIL_DESTINATAIRE"]
SERVEUR_SMTP = "smtp.gmail.com"
PORT_SMTP = 587


def chercher_creneaux_exacts():
    reponse = requests.get(URL_API, params=PARAMETRES, timeout=15)
    reponse.raise_for_status()
    donnees = reponse.json()
    resultats = donnees.get("results", [])

    creneaux_exacts = [
        r for r in resultats if r.get("timeMatch") == "exact"
    ]
    return creneaux_exacts


def envoyer_email_alerte(creneaux):
    sujet = f"🎾 AlerteMoi Padel - {len(creneaux)} créneau(x) exact(s) détecté(s)"

    lignes = []
    for c in creneaux:
        club = c.get("club", {}).get("name", "Club inconnu")
        court = c.get("courtName", "")
        prix = c.get("price", {}).get("amount", "?")
        lien = c.get("links", {}).get("exactSlot", {}).get("url", "")
        lignes.append(f"- {club} ({court}) - {prix}€\n  {lien}")

    corps = (
        f"{len(creneaux)} créneau(x) disponible(s) à l'heure exacte demandée :\n\n"
        + "\n\n".join(lignes)
        + f"\n\nDétecté le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
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
        creneaux = chercher_creneaux_exacts()

        if creneaux:
            message = f"🎾 {len(creneaux)} créneau(x) exact(s) détecté(s) ! Email envoyé."
            envoyer_email_alerte(creneaux)
        else:
            message = "✅ Aucun créneau exact pour le moment."

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
