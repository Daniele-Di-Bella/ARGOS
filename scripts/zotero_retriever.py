import time
import shutil

from pathlib import Path
from pyzotero import zotero, zotero_errors
from API_keys import TDarkRAG_Zotero_API_key, Zotero_library_ID


def extract_zotero_items_keys(
        library_API_key: str,
        library_ID: str,
        keyword: str,
        library_type="user"
):
    # Initialize Zotero library with pyzotero
    library = zotero.Zotero(
        library_ID,  # The ID of the library to examine
        library_type,
        library_API_key  # Zotero's API key
    )

    item_keys = []

    # Retry mechanism for rate limiting
    retry_attempts = 5
    backoff_factor = 2

    for attempt in range(retry_attempts):
        try:
            # Select items according to a specific keyword and extract their key
            items = library.items(q=keyword, qmode="everything")
            for element in items:
                key = element.get("key", 0)
                parentItem = element.get("data", {}).get("parentItem", 0)
                # print(key, parentItem)
                if parentItem and parentItem not in item_keys:
                    item_keys.append(parentItem)
                else:
                    item_keys.append(key)
            break  # exits the cycle if the request is successful

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

        # Handle unexpected errors
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying...")

        time.sleep(backoff_factor ** attempt)  # exponential backoff

    # print(len(item_keys), item_keys)
    return item_keys


def copy_zotero_files(
        zotero_storage_dir: Path,
        subdirs_to_check: list,
        file_extensions: set,
        output_dir: Path
):
    # Check the existance of output directory. If not existent, it is created
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize a counter to keep track of some useful data
    already_present = 0
    subdir_not_found = 0

    # Iterate over subdirectories to check
    for subdir_name in subdirs_to_check:
        subdir_path = zotero_storage_dir / subdir_name  # / is a Path's combination operator
        if subdir_path.is_dir():
            for file_path in subdir_path.rglob("*"):  # "*" iterates over all the files in the subdir
                if file_path.suffix.lower() in file_extensions:
                    output_file = output_dir / file_path.name.strip()
                    if not output_file.exists():
                        shutil.copy2(file_path, output_file)
                    else:
                        already_present += 1
        else:
            print(f'Subdirectory not found: {subdir_path}')
            subdir_not_found += 1

    print(f"Subdirs to ckeck: {len(subdirs_to_check)}; not found: {subdir_not_found}; content already "
          f"copied: {already_present}")


if __name__ == "__main__":
    copy_zotero_files(
        zotero_storage_dir=Path(r"C:\Users\danie\Zotero\storage"),
        subdirs_to_check=extract_zotero_items_keys(TDarkRAG_Zotero_API_key, Zotero_library_ID, "diatoms"),
        file_extensions={".pdf", ".html"},
        output_dir=Path(r"C:\Users\danie\PycharmProjects\TDarkRAG\data")
    )
