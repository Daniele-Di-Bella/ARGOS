import os
import requests
import time
from pathlib import Path
from pyzotero import zotero
from API_keys import TDarkRAG_Zotero_API_key, Zotero_library_ID


def load_library_items(library_API_key: str,
                       library_ID: str,
                       keyword: str,
                       output_dir: str,
                       library_type="user"):
    # Initialize Zotero library with pyzotero
    library = zotero.Zotero(
        library_ID,  # The ID of the library to examine
        library_type,
        library_API_key  # Zotero's API key
    )

    # Verify the existence of the output directory
    os.makedirs(output_dir, exist_ok=True)

    # Select items according to a specific keyword and download them in the output directory
    items = library.items(q=keyword)
    for element in items:
        creator_summary = element["meta"]["creatorSummary"]
        year = element["meta"]["parsedDate"]
        file_name = f"{creator_summary}_{year}"

        # Verify if the selected item has an attachment to download
        if not element["meta"]["numChildren"]:  # aka, if numChildren=0
            print(f"Can't find an attachment to download for {file_name}")
            continue  # go to the next element in the cycle

        download_items(library, output_dir, file_name, element)
        time.sleep(2)


def download_items(library: zotero.Zotero, output_dir: str, file_name: str, item: dict):
    item_key = item["key"]

    # Try to download the attachment with Zotero.dump
    try:
        pdf_filename = file_name + ".pdf"
        library.dump(item_key, pdf_filename, output_dir)
        print(f"{file_name}.pdf successfully downloaded")
        return  # go to the next attachment to download
    except Exception as e:
        print(f"Trying different download methods for {file_name}. Zotero.dump does not work "
              f"due to: {e}")

    # An alternative to Zotero.dump
    attachment = library.children[item_key]

    # Extract URL or DOI
    url = attachment['data'].get('url') or attachment['data'].get('DOI')
    if not url:
        print(f"No URL/DOI was found for: {file_name}. Can't download it.")
        return  # go to the next attachment to download

    # Convert DOIs into URLs
    if url.startswith("10."):
        url = f"https://doi.org/{url}"

    response = requests.get(url, stream=True)  # stream=True gives us the response in chunks
    if response.status_code == 200:  # aka, if there are no errors
        # Save the file
        filepath = os.path.join(output_dir, file_name, ".html")
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"{file_name}.html successfully downloaded")
    else:
        print(f"Error during {file_name} download from {url}: {response.status_code}\n\n"
              f"Trying one last time for {file_name}.")
        g = Goose()






if __name__ == "__main__":
    output_path = Path(r"C:\Users\danie\PycharmProjects\TDarkRAG\data")
    load_library_items(TDarkRAG_Zotero_API_key, Zotero_library_ID, "diatoms", output_path)
