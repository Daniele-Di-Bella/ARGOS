import os
import requests
import time
from goose3 import Goose
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
    items = library.items(q=keyword, qmode="everything")
    for element in items:
        creator_summary = element.get("meta", {}).get("creatorSummary", (element["key"]+"."))
        # the item ID key can be used as an alternative for naming the output files relative to the Zotero
        # items that do not possess a creators' summary

        creator_summary = creator_summary.replace(" ", "-")
        year = element.get("meta", {}).get("parsedDate", "Unknown")
        file_name = f"{creator_summary}{year}"

        # Verify if the selected item has an attachment to download
        num_children = element.get("meta", {}).get("numChildren", 0)
        if not num_children:  # aka, if numChildren=0
            print(f"Can't find an attachment to download for {file_name}")
            continue  # go to the next element in the cycle

        download_items(library, output_dir, file_name, element)
        time.sleep(2)


def download_items(library: zotero.Zotero, output_dir: str, file_name: str, item: dict):
    item_key = item["key"]
    child = library.children(item_key)
    child_key = child[0]["key"]  # useful for Zotero.dump

    # Try to download the attachment with Zotero.dump (it may not work if you're using the
    # free version of Zotero)
    try:
        pdf_filename = file_name + ".pdf"
        library.dump(child_key, pdf_filename, output_dir)
        print(f"{file_name}.pdf successfully downloaded")
        return  # go to the next attachment to download
    except Exception as e:
        print(f"Trying different download methods for {file_name}. Zotero.dump does not work "
              f"due to: {e}")

    # An alternative to Zotero.dump: (1) extract URL or DOI from item
    # print(item)

    url = item['data'].get('url') or item['data'].get('DOI')
    if not url:
        print(f"No URL/DOI was found for: {file_name}. Can't download it.")
        return  # go to the next attachment to download

    # (2) Convert DOIs into URLs
    if url.startswith("10."):
        url = f"https://doi.org/{url}"

    # (3) Try to download a whole html file that contains the attachment
    response = requests.get(url, stream=True)  # stream=True gives us the response in chunks
    if response.status_code == 200:  # aka, if there are no errors
        # Save the file
        filepath = os.path.join(output_dir, (file_name + ".html"))
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"{file_name}.html successfully downloaded")
    else:
        print(f"Error during {file_name} download from {url}: {response.status_code}\n\n"
              f"Trying one last time for {file_name}.")

        # If downloading the html file is, for some reason, not possible, a last resort could be
        # trying to use the library goose3 to create a text file for the attachment that couldn't be
        # downloaded in .pdf or .html
        try:
            g = Goose()  # initialize goose3

            paper = g.extract(url=url)
            paper_text = paper.cleaned_text

            filepath = os.path.join(output_dir, file_name, ".txt")
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(paper_text)
            print(f"{file_name}.txt successfully saved")
        except Exception as e:
            print(f"The retrieving of the text from {file_name} failed due to: {e}")


if __name__ == "__main__":
    output_path = Path(r"C:\Users\danie\PycharmProjects\TDarkRAG\data")
    load_library_items(TDarkRAG_Zotero_API_key, Zotero_library_ID, "diatoms", output_path)
