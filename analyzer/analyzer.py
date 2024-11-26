from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import matplotlib.pyplot as plt

# Create the TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words='english')  # Stop words are ignored

# Vectorize the corpus
dataframe_path = file_path = r'C:\Users\danie\PycharmProjects\WikiSpark\analyzer\tanc2_pubmed_abstracts_2024-11-26_19.37.csv'
df = pd.read_csv(file_path)
corpus = df['Abstract']
M = vectorizer.fit_transform(corpus)

words = vectorizer.get_feature_names_out()

# Convert the TF-IDF matrix to a Pandas DataFrame for better handling
tfidf_matrix = pd.DataFrame(M.toarray(), columns=words)

# Extract the column of interest from he TF-IDF matrix and add it to the dataframe
df["tfidf_tanc2"] = tfidf_matrix["tanc2"]
# print(df["tfidf_tanc2"])
df.to_csv(file_path, index=True)

# Small graphical representation
plt.figure()
df["tfidf_tanc2"].plot(kind='bar', color='lightblue', alpha=0.7)
plt.title('tanc2_TF-IDF')
plt.xlabel('Paper index')
plt.ylabel('TF-IDF')
plt.show()

