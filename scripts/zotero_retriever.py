import os
from pathlib import Path
from pyzotero import zotero
from API_keys import TDarkRAG_Zotero_API_key, Zotero_library_ID

# Load the Zotero library

output_path = Path(r"C:\Users\danie\PycharmProjects\TDarkRAG\data")


def load_library_items(library_API_key: str,
                       library_ID: str,
                       keyword: str,
                       library_type="user"):
    # Initialize Zotero library with pyzotero
    library = zotero.Zotero(
        library_ID,  # The ID of the library to examine
        library_type,
        library_API_key  # Zotero's API key
    )

    items = library.items(q=keyword)
    for element in items:
        download_items(element)


def download_items(item):
    try:
        # Extract URL or DOI
        url = item['data'].get('url') or item['data'].get('DOI')
        if not url:
            print(f"Nessun URL/DOI trovato per l'elemento: {item['data']['title']}")
            return

        # Se è un DOI, convertilo in un link
        if url.startswith("10."):
            url = f"https://doi.org/{url}"

        # Prova a scaricare il PDF
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Salva il file
            filename = item['data']['title'].replace(" ", "_") + ".pdf"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as pdf_file:
                pdf_file.write(response.content)
            print(f"Scaricato: {filepath}")
        else:
            print(f"Errore durante il download da {url}: {response.status_code}")
    except Exception as e:
        print(f"Errore per {item['data']['title']}: {e}")


if __name__ == "__main__":
