from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Create the TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words='english')  # Stop words are ignored

# Vectorize the corpus
dataframe_path = file_path = r'C:\Users\danie\PycharmProjects\WikiSpark\analyzer\tanc2_pubmed_abstracts_2024-11-26_19.37.csv'
df = pd.read_csv(file_path)
corpus = df['Abstract']
M = vectorizer.fit_transform(corpus)

# Cosine similarity computation
similarity_matrix = cosine_similarity(M)
# print(similarity_matrix)

# # Convert the TF-IDF matrix to a Pandas DataFrame for better handling
# words = vectorizer.get_feature_names_out()
# tfidf_matrix = pd.DataFrame(M.toarray(), columns=words)
#
# # Extract the column of interest from he TF-IDF matrix and add it to the dataframe
# df["tfidf_tanc2"] = tfidf_matrix["tanc2"]
# # print(df["tfidf_tanc2"])
# df.to_csv(file_path, index=True)

plt.figure(figsize=(10, 8))
sns.heatmap(similarity_matrix, annot=False, cmap='viridis', cbar=True, square=True,
            xticklabels=corpus.index, yticklabels=corpus.index)

plt.title("Cosine Similarity Matrix")
plt.xlabel("Abstract Index")
plt.ylabel("Abstract Index")

plt.xticks(rotation=90)
plt.yticks(rotation=0)

plt.show()
