from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import matplotlib.pyplot as plt

# Create the TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words='english')  # Stop words are ignored

# Vectorize the corpus
dataframe_path = file_path = r'C:\Users\danie\PycharmProjects\WikiSpark\crawler\tanc2_pubmed_abstracts_2024-11-26_16.24.csv'
df = pd.read_csv(file_path)
corpus = df['Abstract']
M = vectorizer.fit_transform(corpus)

words = vectorizer.get_feature_names_out()

# Convert the TF-IDF matrix to a Pandas DataFrame for better handling
tfidf_matrix = pd.DataFrame(M.toarray(), columns=words)

# Extract the column of interest from he TF-IDF matrix and add it to the dataframe
df["tfidf_tanc2"] = tfidf_matrix["tanc2"]
df.to_csv(file_path, index=False)

# Small graphical representation
plt.figure()
df["tfidf_tanc2"].plot.hist(alpha=0.5)
plt.show()

