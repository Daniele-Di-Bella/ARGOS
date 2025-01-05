import re
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
    """
    :param library_API_key:
    :param library_ID:
    :param keyword:
    :param library_type:
    :return:
    """
    # Initialize Zotero library with pyzotero
    library = zotero.Zotero(
        library_ID,  # The ID of the library to examine
        library_type,
        library_API_key  # Zotero's API key
    )

    items_key_title = []

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
                if parentItem and parentItem not in items_key_title:
                    # print(library.item(parentItem))
                    title = (library.item(parentItem)).get("data", {}).get("title", 0)
                    items_key_title.append((key, title))
                else:
                    title = (library.item(key)).get("data", {}).get("title", 0)
                    items_key_title.append((key, title))
                # print(element)
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

    # print(items_key_title)
    return items_key_title


def sanitize_filename(filename: str) -> str:
    """
    Removes or replaces invalid characters for file names on Windows.
    :param filename:
    :return:
    """
    return re.sub(r'[<>:"/\\|?*]', " ", filename)  # replaces prohibited characters with " "


def copy_zotero_files(
        zotero_storage_dir: Path,
        subdirs_to_check: list,
        file_extensions: set,
        output_dir: Path
):
    """
    :param zotero_storage_dir:
    :param subdirs_to_check:
    :param file_extensions:
    :param output_dir:
    :return:
    """
    # Check the existance of output directory. If not existent, it is created
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize a counter to keep track of some useful data
    already_present = 0
    subdir_not_found = 0

    # Iterate over subdirectories to check
    for subdir in subdirs_to_check:
        subdir_path = zotero_storage_dir / subdir[0]  # / is a Path's combination operator
        # remember that subdir is a (key, title) tuple, and the name of the subdir correspond to the first
        # element of this tuple
        if subdir_path.is_dir():
            for file_path in subdir_path.rglob("*"):  # "*" iterates over all the files in the subdir
                if file_path.suffix.lower() in file_extensions:
                    sanitized_title = sanitize_filename(subdir[1])
                    output_file_name = f"{sanitized_title}{file_path.suffix.lower()}"
                    output_file = output_dir / output_file_name
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
