import os
from pyzotero import zotero

zot = zotero.Zotero(
    os.environ.get("Zotero_library_ID"),  # The ID of the library to examine
    "user",
    os.environ.get("TDarkRAG_Zotero_API_key")  # Zotero's API key
)

if __name__ == "__main__":
    items = zot.top(limit=1)
    for item in items:
        child = zot.fulltext_item(item["key"])
        print(f"{child}\n\n----------------\n")