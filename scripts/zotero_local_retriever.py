import shutil
import os
from pyzolocal.sqls import gets as g

# Get all the items that are related to the chosen keyword
keyword = "diatoms"

items = g.get_items_info()
filtered_items = [
    item for item in items
    if any(keyword in data.value.lower() for data in item.itemDatas)
]  # The item objects are instances of the Item class defined in the pyzolocal.beans.types module

# Get the attachments
attachments = []
for item in filtered_items:
    item_attachments = g.get_attachments_by_parentid(item.itemID)
    attachments.extend(item_attachments)

# Copy the attachments in the output path
output_dir = r"C:\Users\danie\PycharmProjects\TDarkRAG\data"
os.makedirs(output_dir, exist_ok=True)
zotero_base_path = r"C:\Users\danie\Zotero"  # path for the local Zotero folder (base path)

for attachment in attachments:
    if attachment.relpath:  # verify that the relative path is valid
        source_path = os.path.join(zotero_base_path, attachment.relpath)
        destination_path = os.path.join(output_dir, os.path.basename(attachment.relpath))
        try:
            shutil.copy(source_path, destination_path)
            print(f"Copied file: {source_path} -> {destination_path}")
        except FileNotFoundError:
            print(f"File not found in: {source_path}")
        except Exception as e:
            print(f"Error copying {source_path}: {e}")
