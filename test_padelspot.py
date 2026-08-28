import requests

URL_API = "https://padelspot.app/api/public/explore"


def verifier_disponibilites():
    parametres = {
        "city": "bordeaux",
        "date": "2026-08-29",
        "time": "20:00",
    }

    reponse = requests.get(
        URL_API,
        params=parametres,
        timeout=15
    )

    reponse.raise_for_status()

    donnees = reponse.json()

    resultats = donnees.get("results", [])

    if resultats:
        print(f"🚨 {len(resultats)} disponibilité(s) détectée(s) !")

        for resultat in resultats:
            print(resultat)

    else:
        print("✅ Aucune disponibilité détectée.")


if __name__ == "__main__":
    verifier_disponibilites()
