from goose3 import Goose
import requests

# URL dell'articolo
url = "https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2020.540607/full"

# Inizializza Goose
g = Goose()

# Estrai l'articolo
articolo = g.extract(url=url)

# Ottieni il testo dell'articolo
testo_articolo = articolo.cleaned_text

# Salva il testo in un file
with open(r'C:\Users\danie\PycharmProjects\TDarkRAG\data\articolo.txt', 'w', encoding='utf-8') as file:
    file.write(testo_articolo)

print('Il testo dell\'articolo è stato estratto e salvato in "articolo.txt".')
