import pandas as pd

@staticmethod
def get_sites():
    """
    Retourne un DataFrame avec le mapping site/plage/gmaps_url.
    """
    data = [
        {"site": "PLAGE DE LA BAIE DES CITRONS", "plage": "Plage de la baie des Citrons", "gmaps_url": "https://maps.app.goo.gl/P2SP3oWuQbxd1sCH9"},
        {"site": "PLAGE DE L'ANSE VATA", "plage": "Plage de l'Anse-Vata", "gmaps_url": "https://maps.app.goo.gl/xAUdky47DqEjSF4R8"},
        {"site": "PLAGE DE LA POINTE MAGNIN", "plage": "Plage de la pointe Magnin", "gmaps_url": "https://maps.app.goo.gl/Wf69LoGgc894MtQy6"},
        {"site": "PLAGE DE LA PROMENADE PIERRE VERNIER", "plage": "Plage de la promenade Pierre-Vernier", "gmaps_url": "https://maps.app.goo.gl/bNocZKVVMYk3HFYs9"},
        {"site": "PLAGE DE MAGENTA", "plage": "Plage de Magenta", "gmaps_url": "https://maps.app.goo.gl/yFwgG2BCV1sEtPWP6"},
        {"site": "PLAGE DU KUENDU BEACH", "plage": "Plage du Kuendu Beach", "gmaps_url": "https://maps.app.goo.gl/oGY6Hy4KCXJWxqfL9"},
    ]
    return pd.DataFrame(data)
def get_pdf_url():
    """
    Alias public pour obtenir l'URL du dernier PDF d'analyses détaillées.
    """
    return get_latest_pdf_url()

import pandas as pd
import tabula
import requests
import io
from bs4 import BeautifulSoup

# URL de la page officielle contenant le lien vers le PDF
PAGE_URL = "https://www.noumea.nc/noumea-pratique/salubrite-publique/qualite-eaux-baignade"


def get_latest_pdf_url():
    """
    Récupère dynamiquement l'URL du dernier PDF d'analyses détaillées depuis la page officielle.
    """
    print(f"🔗 Recherche du lien PDF sur {PAGE_URL} ...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    try:
        resp = requests.get(PAGE_URL, headers=headers)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Impossible de récupérer la page officielle : {e}")
        return None
    soup = BeautifulSoup(resp.text, "lxml")
    # Chercher le premier lien PDF dans la page
    link = soup.find("a", href=lambda h: h and h.endswith(".pdf"))
    if not link:
        print("❌ Aucun lien PDF trouvé sur la page.")
        return None
    pdf_url = link["href"]
    # Si le lien est relatif, le rendre absolu
    if pdf_url.startswith("/"):
        pdf_url = "https://www.noumea.nc" + pdf_url
    print(f"✅ Lien PDF trouvé : {pdf_url}")
    return pdf_url

def get_detailed_results():
    """
    Télécharge dynamiquement le PDF des résultats détaillés, en extrait le premier tableau
    et le retourne sous forme de DataFrame pandas.
    """
    pdf_url = get_latest_pdf_url()
    if not pdf_url:
        return None
    print(f"📥 Téléchargement du PDF depuis {pdf_url} ...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(pdf_url, headers=headers)
        response.raise_for_status()
        print("✅ Téléchargement terminé.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du téléchargement du fichier PDF : {e}")
        return None

    pdf_file = io.BytesIO(response.content)

    try:
        print("🔍 Extraction des tableaux du PDF...")
        tables = tabula.read_pdf(pdf_file, pages='1', stream=True)
    except Exception as e:
        print(f"❌ Une erreur est survenue lors de l'extraction des données du PDF.")
        print("ℹ️  Cela peut être dû à l'absence de Java sur votre système, qui est requis par la bibliothèque 'tabula-py'.")
        print(f"   Erreur originale : {e}")
        return None

    if not tables:
        print("❌ Aucun tableau n'a été trouvé dans le PDF.")
        return None

    print(f"✅ {len(tables)} tableau(x) trouvé(s). Affichage du premier.")
    df = tables[0]
    print("\n--- Aperçu du tableau extrait (toutes colonnes) ---")
    with pd.option_context('display.max_columns', None):
        print(df)
    print("\nColonnes:", list(df.columns))
    print("Shape:", df.shape)

    # Sélection dynamique des colonnes bactéries par nom
    # Recherche des colonnes contenant les mots-clés
    e_coli_col = next((col for col in df.columns if "Escherichia" in str(col) or "coli" in str(col)), None)
    entero_col = next((col for col in df.columns if "Entérocoques" in str(col)), None)

    if e_coli_col is None or entero_col is None:
        print(f"❌ Colonnes bactéries non trouvées dans le tableau extrait. Colonnes disponibles : {list(df.columns)}")
        return None

    # Sélectionne les 4 premières colonnes + colonnes bactéries trouvées
    selected_cols = [df.columns[0], df.columns[1], df.columns[2], df.columns[4], e_coli_col, entero_col]
    cleaned_df = df.loc[:, selected_cols].copy()
    cleaned_df.columns = [
        "site",
        "point_de_prelevement",
        "date",
        "heure",
        "e_coli_npp_100ml",
        "enterocoques_npp_100ml"
    ]

    # Ajoute deux colonnes issues du split de 'point_de_prelevement'
    split_points = cleaned_df["point_de_prelevement"].str.split(",", n=1, expand=True)
    cleaned_df["id_point_prelevement"] = split_points[0].str.strip()
    cleaned_df["desc_point_prelevement"] = split_points[1].str.strip() if split_points.shape[1] > 1 else ""

    # S'assurer que la colonne 'heure' est bien présente et de type string
    if "heure" in cleaned_df.columns:
        cleaned_df["heure"] = cleaned_df["heure"].astype(str)


    # Nettoyer et convertir les colonnes e_coli_npp_100ml et enterocoques_npp_100ml
    if "e_coli_npp_100ml" in cleaned_df.columns:
        cleaned_df["e_coli_npp_100ml"] = cleaned_df["e_coli_npp_100ml"].astype(str).str.replace(r"<\s*10", "10", regex=True)
        cleaned_df["e_coli_npp_100ml"] = pd.to_numeric(cleaned_df["e_coli_npp_100ml"], errors="coerce").astype('Int64')

    if "enterocoques_npp_100ml" in cleaned_df.columns:
        cleaned_df["enterocoques_npp_100ml"] = cleaned_df["enterocoques_npp_100ml"].astype(str).str.replace(r"<\s*10", "10", regex=True)
        cleaned_df["enterocoques_npp_100ml"] = pd.to_numeric(cleaned_df["enterocoques_npp_100ml"], errors="coerce").astype('Int64')

    # Convertir la colonne 'date' en datetime (format jour/mois/année)
    if "date" in cleaned_df.columns:
        cleaned_df["date"] = pd.to_datetime(cleaned_df["date"], format="%d/%m/%Y", errors="coerce")

    return cleaned_df

if __name__ == "__main__":
    # Obtenir le DataFrame des résultats détaillés
    detailed_df = get_detailed_results()

    # Afficher seulement les colonnes demandées
    if detailed_df is not None:
        print("\n📋 Détails synthétiques :")
        print(detailed_df[[
            "point_de_prelevement",
            "date",
            "e_coli_npp_100ml",
            "enterocoques_npp_100ml"
        ]])
