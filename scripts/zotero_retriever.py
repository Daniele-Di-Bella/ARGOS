import os
import requests
import time
from goose3 import Goose
from pathlib import Path
from pyzotero import zotero, zotero_errors
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

    # Retry mechanism for rate limiting
    retry_attempts = 5

    for attempt in range(retry_attempts):
        try:
            # Select items according to a specific keyword and download them in the output directory
            items = library.items(q=keyword, qmode="everything", limit=2)
            for element in items:
                # Verify if the selected item has an attachment or *is* an attachment
                parentItem = element.get("data", {}).get("parentItem", 0)
                if parentItem:
                    parent = library.item(parentItem)
                    creator_summary = parent.get("meta", {}).get("creatorSummary", (element["key"] + "."))
                    # the item ID key can be used as an alternative for naming the output files relative to
                    # the Zotero items that do not possess a creators' summary

                    creator_summary = creator_summary.replace(" ", "-")
                    year = parent.get("meta", {}).get("parsedDate", "Unknown")
                else:
                    creator_summary = element.get("meta", {}).get("creatorSummary", (element["key"] + "."))
                    # the item ID key can be used as an alternative for naming the output files relative to
                    # the Zotero items that do not possess a creators' summary

                    creator_summary = creator_summary.replace(" ", "-")
                    year = element.get("meta", {}).get("parsedDate", "Unknown")

                file_name = f"{creator_summary}{year}"

                # print(f"Element {file_name}: {element}")  # for debugging

                download_items(library, output_dir, file_name, element, bool(parentItem))

            break  # Exit the retry loop if successful

        # Handle rate limiting and backoff
        except zotero_errors.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", 5))
                print(f"Rate limit hit. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            elif "Backoff" in e.response.headers:
                backoff_time = int(e.response.headers["Backoff"])
                print(f"Server is overloaded. Backing off for {backoff_time} seconds...")
                time.sleep(backoff_time)
            else:
                print(f"HTTP error: {e}. Retrying...")
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying...")

        time.sleep(2 ** attempt)  # Exponential backoff


def download_items(library: zotero.Zotero, output_dir: str, file_name: str, item: dict, isChild: bool):
    if isChild:
        download_key = item["key"]
    else:
        child = library.children(item["key"])
        download_key = child[0]["key"]

    # Try to download the attachment with Zotero.dump (it may not work if you're using the
    # free version of Zotero)
    try:
        pdf_filename = file_name + ".pdf"
        library.dump(download_key, pdf_filename, output_dir)
        print(f"{file_name}.pdf successfully downloaded")
        return  # go to the next attachment to download
    except Exception as e:
        print(f"Trying different download methods for {file_name}. Zotero.dump does not work "
              f"due to: {e}")

    # An alternative to Zotero.dump: (1) extract URL or DOI from item
    url = item['data'].get('url') or item['data'].get('DOI')
    if not url:
        print(f"No URL/DOI was found for: {file_name}. Can't download it.")
        return  # go to the next attachment to download

    # (2) Convert DOIs into URLs
    if url.startswith("10."):
        url = f"https://doi.org/{url}"

    # (3) Try to download a whole html file that contains the attachment
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, stream=True)  # stream=True gives us the response in chunks
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
