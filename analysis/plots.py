import matplotlib.pyplot as plt
import pandas as pd

dataframe_path = file_path = r'C:\Users\danie\PycharmProjects\WikiSpark\analyzer\tanc2_pubmed_abstracts_2024-11-26_19.37.csv'
df = pd.read_csv(file_path)

# Histogram representation of TF-IDF
plt.figure()
df["tfidf_tanc2"].plot(kind='bar', color='lightblue', alpha=0.7)
plt.title('tanc2_TF-IDF')
plt.xlabel('Paper index')
plt.ylabel('TF-IDF')
plt.show()