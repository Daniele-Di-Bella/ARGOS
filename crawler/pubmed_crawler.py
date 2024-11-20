import requests
import time
from xml.etree import ElementTree

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


# Search papers on PubMed
def search_pubmed(protein, max_results=10000):
    params = {
        'db': 'pubmed',
        'term': protein,
        'retmax': max_results,
        'retmode': 'xml'
    }
    response = requests.get(BASE_URL + "esearch.fcgi", params=params)

    # Basic error handling
    if response.status_code == 200:
        return response.text
    print(f"Error while searching PubMed: {response.status_code}")
    return None


# Abstract extraction with PubMed ID
def fetch_abstract(pmid):
    params = {
        'db': 'pubmed',
        'id': pmid,
        'retmode': 'xml'
    }
    response = requests.get(BASE_URL + "efetch.fcgi", params=params)

    # Basic error handling
    if response.status_code == 200:
        return response.text
    print(f"Error while fetching abstract: {response.status_code}")
    return None


# Parse search results and get PubMed IDs (PMIDs)
def parse_search_results(xml_data):
    root = ElementTree.fromstring(xml_data)
    pmids = [id_tag.text for id_tag in root.findall(".//IdList/Id")]
    total_results = int(root.find(".//Count").text)
    return pmids, total_results


# Parse abstracts and return them
def parse_abstract(xml_data):
    root = ElementTree.fromstring(xml_data)
    paragraphs = root.findall(".//PubmedArticle/MedlineCitation/Article/Abstract/AbstractText")
    return " ".join([para.text for para in paragraphs if para.text]) or None


# Main function to perform search and collect abstracts
def main():
    term = "tanc2"  # Search term, for us, the name of a Tdark protein
    retmax = 10000  # Max results per request (PubMed max)
    retstart = 0  # Starting point for iterative search
    all_pmids = []

    while True:
        print(f"Fetching results starting from {retstart}...")
        search_results = search_pubmed(term, max_results=retmax)
        if search_results:
            pmids, total_results = parse_search_results(search_results)
            all_pmids.extend(pmids)

            if len(all_pmids) >= total_results:
                print(f"Retrieved all {total_results} results.")
                break
            retstart += retmax
        else:
            break

        time.sleep(1 / 3)  # Pause between requests

    print(f"Total PMIDs collected: {len(all_pmids)}")

    # Now collect abstracts for each PMID
    for pmid in all_pmids:
        print(f"Fetching abstract for PMID: {pmid}")
        abstract_data = fetch_abstract(pmid)
        if abstract_data:
            abstract = parse_abstract(abstract_data)
            if abstract:
                print(f"Abstract for {pmid}: {abstract}")
            else:
                print(f"No abstract found for PMID {pmid}")
            print("-" * 80)

        time.sleep(1 / 3)  # Pause between requests


if __name__ == "__main__":
    main()
