import requests
import time
import csv

# webbrowser is needed for debugging. Do not optimize imports.
import webbrowser

from xml.etree import ElementTree
from datetime import datetime

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


# Search papers on PubMed
def search_pubmed(protein, max_results=10000, restart=0):
    params = {
        'db': 'pubmed',
        'term': protein,
        'retmax': max_results,
        "restart": restart,
        'retmode': 'xml'
    }
    response = requests.get(BASE_URL + "esearch.fcgi", params=params)

    # Basic error handling
    if response.status_code == 200:
        return response.text
    print(f"Error while searching PubMed: {response.status_code}")
    return None


# Abstract extraction with PubMed ID
def fetch_paper(pmid):
    params = {
        'db': 'pubmed',
        'id': pmid,
        'retmode': 'xml'
    }
    response = requests.get(BASE_URL + "efetch.fcgi", params=params)

    # Basic error handling
    if response.status_code == 200:
        return response.text
    print(f"Error while fetching paper: {response.status_code}")
    return None


# Parse search results and get PubMed IDs (PMIDs)
def parse_search_results(xml_data):
    root = ElementTree.fromstring(xml_data)
    pmids = [id_tag.text for id_tag in root.findall(".//IdList/Id")]
    total_results = int(root.find(".//Count").text)
    return pmids, total_results


# Parse abstracts and return them
def parse_result(xml_data, abstract=True):
    root = ElementTree.fromstring(xml_data)

    # Two different alternatives if only the abstract is desired or the full text
    if abstract:
        paragraphs = root.findall(".//PubmedArticle/MedlineCitation/Article/Abstract/AbstractText")
        raw_text = " ".join([para.text for para in paragraphs if para.text])
    else:
        paragraphs = []
        # Search for paragraphs under <body> node
        for section in root.findall(".//body//sec"):
            for paragraph in section.findall(".//p"):
                paragraphs.append(paragraph.text)
        raw_text = "\n".join(paragraphs)

    # Substitution of all NBSP characters with normal spaces
    cleaned_text = raw_text.replace("\u00A0", " ")  # '\u00A0' is the Unicode code for NBSP

    return cleaned_text or None


# Main function to perform search and collect abstracts
def main(term: str, abstract=True):  # Search term, for us (DarkLab) is the name of a Tdark protein
    retmax = 10000  # Max results per request (PubMed max)
    restart = 0  # Starting point for iterative search
    all_pmids = []
    now = datetime.now().strftime("%Y-%m-%d_%H.%M")
    output_file_path = f"data/{term}_pubmed_{now}.csv"

    with open(output_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Link", "Abstract"])

    while True:
        print(f"Fetching results starting from {restart}...")
        search_results = search_pubmed(term, max_results=retmax, restart=restart)
        if search_results:
            pmids, total_results = parse_search_results(search_results)
            all_pmids.extend(pmids)

            if len(all_pmids) >= total_results:
                print(f"Retrieved all {total_results} results.")
                break
            restart += retmax
        else:
            break

        time.sleep(1 / 3)  # Pause between requests

    print(f"Total PMIDs collected: {len(all_pmids)}")

    # Now collect abstracts for each PMID
    for pmid in all_pmids:
        print(f"Fetching content for PMID: {pmid}")
        data = fetch_paper(pmid)
        if data:
            if abstract:
                text = parse_result(data)
            else:
                text = parse_result(data, abstract=False)

            if text:
                link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                with open(output_file_path, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([link, text])
            else:
                print(f"No text content found for PMID {pmid}")
                # webbrowser.open(f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")

        time.sleep(1 / 3)  # Pause between requests


if __name__ == "__main__":
    main("tmem138", abstract=False)
