# -*- coding: utf-8 -*-
"""ShampYou.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1t33Adt-KWqnvfyNxCWXk73HIymYCBWMn

# Analysis
"""

!pip install streamlit



!pip install vaderSentiment

!pip install --upgrade nltk

!python -m spacy download en_core_web_md

!pip install deep-translator

!pip install nltk

#we have to translate all german, chinese or reviews written in any other language into English - run just one - otherwise you might have to resyart the kernel
!pip install langdetect googletrans==4.0.0-rc1

import csv
import nltk
import re
import spacy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import normalize
from nltk.corpus import reuters, wordnet, stopwords
from sklearn.metrics.pairwise import cosine_similarity
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer

from google.colab import files
uploaded = files.upload()

reviews = pd.read_csv("Influenster Reviews.csv")
print("Number of rows : ",len(reviews))
reviews.head()

from google.colab import files
uploaded = files.upload()

products = pd.read_csv("Influenster Product Descriptions.csv")
print("Number of rows : ",len(products))
products.head()

from google.colab import files
uploaded = files.upload()

products_price = pd.read_csv("influenster_product_desc - Copy (1).csv")
print("Number of rows : ",len(products_price))
products_price.head()

df_1 = products.merge(products_price, left_on='Product Name', right_on='Product Name', how='left')
df_1.drop(columns = ['product_name', 'price', 'Similarity', 'quantity', 'URL'], inplace = True)
df_1.head(4) # Put this in slide 13(trusting the popularity) -- top three product names and #of reviews

df = reviews.merge(df_1, left_on='product_name', right_on='Product Name', how='left')
df.drop(columns = 'Product Name', inplace = True)
df.head()

"""# Data Cleaning"""

from deep_translator import GoogleTranslator
import pandas as pd
from langdetect import detect

# Initialize GoogleTranslator
translator = GoogleTranslator(source='auto', target='en')

# Function to detect language and translate to English using deep-translator
def detect_and_translate_deep(text):
    try:
        # Detect the language
        detected_lang = detect(text)
        # If it's not already English, translate it using deep-translator
        if detected_lang != 'en':
            return translator.translate(text)
        else:
            return text
    except Exception as e:
        return f"Error: {str(e)}"

# Apply the detect and translate function to the 'reviews' column
df['product_review'] = df['product_review'].apply(detect_and_translate_deep)

df.head()

#download stopwords and punctuations - get rid of these so that our word vectors are smaller
#get the frequency count of all main words in the reviews and find beer attributes that are generally talked about
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
# Function to remove stopwords and tokenize
def remove_stopwords_and_tokenize(text):
    # Handle non-string (float or NaN) values by converting them to empty strings
    if not isinstance(text, str):
        text = ''
    # Preprocess: Replace hyphens between words with underscores to preserve hyphenated words
    text = re.sub(r'\b(\w+)-(\w+)\b', r'\1_\2', text.lower())  # Convert text to lowercase and replace hyphenated words
    # Tokenize using regex to handle numbers followed by '%'
    tokens = re.findall(r'\b\d+%|\w+\b', text)  # Use regex to treat numbers with % as a single token
    # Remove stopwords and keep only relevant tokens
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return filtered_tokens

#let us try getting the unique words in every review and count their frequncy
df['filtered_words'] = df['product_review'].apply(remove_stopwords_and_tokenize)
df.head()

#long tail
plt.figure(figsize=(15, 6))
df_plot = df[['product_name','Average Rating','Number of Reviews']].drop_duplicates()
df_plot.plot(x='product_name', y='Number of Reviews', marker='None', linestyle='-')
plt.xlabel('Product Name', fontsize=12)
plt.ylabel('Number of Reviews', fontsize=12)
plt.title('Number of Reviews by Product', fontsize=14)
plt.xticks(rotation=270)

plt.show()

import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set(style="whitegrid")

# Long tail plot
plt.figure(figsize=(15, 6))
df_plot = df[['product_name', 'Average Rating', 'Number of Reviews']].drop_duplicates()
sns.lineplot(data=df_plot, x='product_name', y='Number of Reviews', marker='o', linestyle='-', color='b')

plt.xlabel('Product Name', fontsize=12)
plt.ylabel('Number of Reviews', fontsize=12)
plt.title('Number of Reviews by Product', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()  # Adjusts the plot to fit within the figure area
ticks = np.arange(len(df['product_name']))
plt.xticks(ticks, df['product_name'], rotation=45, ha='right', fontsize=10)
# Show only every 10th tick
plt.gca().set_xticklabels([name if i % 10 == 0 else '' for i, name in enumerate(df['product_name'])], rotation=45, ha='right', fontsize=10)
# Show grid lines
plt.grid(True)

# Show the plot
plt.show()

# Get all words into a single list - then going through this list to identify some important attributes
all_words = [word for words_list in df['filtered_words'] for word in words_list] # This is the list of all the words - this will be our main vector
# Get the overall word count
word_count = Counter(all_words)
word_count_df = pd.DataFrame(word_count.items(), columns=['word', 'count']).sort_values(by='count', ascending=False)
word_count_df[:5]
csv_file_path = 'unique_word_count_reviews.csv'
# The outout will have the number of times each word had appeared in the product reviews - multiple occuarances within a review is counted as one
word_count_df.to_csv(csv_file_path, index=False)
from google.colab import files
files.download(csv_file_path)

# A list of all reviews for all products
list_reviews = df['filtered_words'].tolist()
list_reviews[:2]

#get a list of top attributes from the count file and look at the lift values between attributes
from google.colab import files
uploaded = files.upload()

atr = pd.read_csv("attributes.csv",encoding='cp1252')
atr['attributes'].tolist()

#Calculate the lift between attributes
#find the co-mentions between attributes - do not have to look at the products for this
def co_mentions(s1,s2,list_reviews):
  c=0;
  for i in list_reviews:
    if s1 in i and s2 in i:
      c=c+1
  return c

def create_lift_matrix(l1,l2,list_reviews,word_count):
  n_tweets = len(list_reviews)
  lift_matrix = pd.DataFrame(np.zeros((len(l1), len(l2))), index=l1, columns=l2)
  for i in range(len(l1)):
        for j in range(len(l2)):
            if l1[i] == l2[j]:
                lift_matrix.loc[l1[i], l2[j]] = np.nan  # Use NaN for same attribute comparison
            else:
                # Make sure that word counts are not zero to avoid division by zero
                if word_count.get(l1[i], 0) > 0 and word_count.get(l2[j], 0) > 0:
                    co_men = co_mentions(l1[i], l2[j], list_reviews)
                    #print("Co mentions of ", l1[i],",",l2[j],"=",co_men)
                    lift_value = (n_tweets * co_men) / (word_count[l1[i]] * word_count[l2[j]])
                    lift_matrix.loc[l1[i], l2[j]] = lift_value
                else:
                    lift_matrix.loc[l1[i], l2[j]] = 0  # Assign 0 if word counts are zero or missing

  return lift_matrix

attribute_lift = create_lift_matrix(atr['attributes'].tolist(),atr['attributes'].tolist(),list_reviews,word_count)
attribute_lift

#output the beer attribute lift matrix to understand and pick 3 attributes with good lift
csv_file_path = 'attribute_lift.csv'
# The outout will have the number of times each word had appeared in the product reviews - multiple occuarances within a review is counted as one
attribute_lift.to_csv(csv_file_path, index=False)
from google.colab import files
files.download(csv_file_path)



#ask the user to select any 3 attributes of his/her choice
user_input = []
print("These are the general things people are using to talk about while discussing shampoos")
print(atr['attributes'].to_list())
print("Enter three important attributes from the above list you are looking for in your shampoo and we will help you find your perfect shampoo")
for i in range(3):
  attribute = input("Enter the attribute and hit enter to proceed ")
  user_input.append(attribute)
user_input

#add this to the main dataframe
new_row=pd.DataFrame({'product_name': 'attributes' , 'product_review': ' '.join(user_input) ,'user_rating':5, 'filtered_words': [user_input]})
#df= pd.concat([new_row, df], ignore_index=True)
#df
new_row

df_new= pd.concat([new_row, df], ignore_index=True)

list_reviews_new = df_new['filtered_words'].tolist()
list_reviews_str = [' '.join(words_list) for words_list in list_reviews_new]
print(list_reviews_str)

"""# Task C : Cosine Similarity between the first row - with just the attributes and the rest of the rows (normlized)"""

vectorizer = CountVectorizer()
# Fit and transform the documents
word_matrix = vectorizer.fit_transform(list_reviews_str)
# Convert the matrix to an array
word_matrix_array = word_matrix.toarray()
# Get feature (word) names
feature_names = vectorizer.get_feature_names_out()
# Convert to a DataFrame
df_word_matrix = pd.DataFrame(word_matrix_array, columns=feature_names)
df_word_matrix_normalized = pd.DataFrame(normalize(df_word_matrix, norm='l1', axis=1), columns=feature_names)
df_word_matrix_normalized.head()

#cosine similarity
# Calculate cosine similarity of the first row with all rows
cosine_similarities = cosine_similarity(df_word_matrix_normalized.iloc[0:1], df_word_matrix_normalized)

# Convert the result to a DataFrame for better visualization
cosine_similarity_df = pd.DataFrame(cosine_similarities.flatten(), columns=['Cosine Similarity'])

# Display the result
df_new['cosine_sim'] = cosine_similarity_df['Cosine Similarity']
df_new.head()

import copy
from copy import deepcopy
df_similarity = copy.deepcopy(df_new.drop(columns = ['user_rating','filtered_words']))
df_similarity.head()

"""# Task D : Vader similarity"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#sentiment analysis using vader
analyzer = SentimentIntensityAnalyzer()
# Function to calculate sentiment using VADER
def vader_sentiment(text):
    return analyzer.polarity_scores(text)['compound']

# Apply the VADER sentiment function to the DataFrame
df_new['vader_sentiment'] = df_new['product_review'].apply(vader_sentiment)

# Display the DataFrame with VADER sentiment scores
df_new.head()

"""# Task E : Overall Evaluation Score"""

#combine similarity and sentiment scores to get the final score per review - then avergae it out by grouping at a product level
df_new['overall_score']=df_new['cosine_sim']*df_new['vader_sentiment']
df_new.head()

average_scores = df_new.groupby('product_name')[['overall_score','vader_sentiment','cosine_sim']].mean().sort_values( by = 'overall_score', ascending=False)
average_scores

"""# Beer Recommendations based on Vader sentiment and Cosine similarity

# Task F : Spacy Similarity & Vader sentiment : Comparision with cosine + vader
"""

#spacy similarity
nlp = spacy.load("en_core_web_md")
# Get the first review
first_review = df_new['product_review'].iloc[0]
# Process the first review
first_doc = nlp(first_review)
# Calculate similarity with all other reviews
similarity_scores = []
# Calculate similarity with all other reviews
for review in df_new['product_review']:
    doc = nlp(review)
    similarity = first_doc.similarity(doc)
    #print(similarity)
    similarity_scores.append(similarity)
# Add similarity scores to the DataFrame
df_new['spacy_similarity'] = similarity_scores

# Display the DataFrame with similarity scores
df_new.head()

#calculating the overall score based on the vader sentiment and the spacy similarity
df_new['spacy_overall_score']= df_new['spacy_similarity']*df_new['vader_sentiment']
df_new.head()

average_scores_spacy = df_new.groupby('product_name')['spacy_overall_score'].mean().sort_values(ascending=False)
average_scores_spacy.head()

"""# Task G : Receommendation just on the basis of the average ratings"""

# Get the top recommendations just based on average rating
average_rating = df_new.groupby('product_name')['Average Rating'].mean().sort_values(ascending=False)
average_rating.head()

# Top 3 beers for the given attributes beased on cosine similarity and vader sentiment analysis
average_scores[:3]

# Top 3 Beers based on spacy similarity and vader sentiment
average_scores_spacy[:3]

#on the basis of average ratings
average_rating[1:4]

shampoos = reviews['product_name'].unique()

#lift matrix with all the initial attributes
n= len(df_new)
print("total length =",n)
sh_oc = {}
new_at = atr['attributes'].to_list()
at_oc = {}
for i in shampoos:
  sh_oc[i]=len(df_new[df_new['product_name']==i])
  #print(i," ",beer_oc[i])
for i in new_at:
  at_oc[i]= word_count[i]
  #print(i," ",word_count[i])
# Function to count reviews containing the word
def count_reviews_containing_word(df, word):
    count = df['product_review'].str.contains(fr'\b{word}\b', case=False, na=False).sum()
    return count
shampoo_lift = pd.DataFrame(np.zeros((len(sh_oc), len(at_oc))), index=sh_oc, columns=at_oc)
for i in shampoos:
  temp_df = df_new[df_new['product_name']==i]
  for j in new_at:
    c=count_reviews_containing_word(temp_df,j)
    #print("Co mentions of ", i,",",i,"=",c)
    lift_value = (n * c) / ( sh_oc[i]* at_oc[j])
    if lift_value==0 or np.isnan(lift_value):
      shampoo_lift.loc[i, j] = 0.001
    else:
      if lift_value <= 0.05:
        shampoo_lift.loc[i, j] = 0.05
      else:
        shampoo_lift.loc[i, j] = lift_value
    c=0
shampoo_lift

shampoo_lift.replace([np.inf, -np.inf], np.nan, inplace=True)
# Fill NaN values with a small value (e.g., 0.001)
shampoo_lift.fillna(0.001, inplace=True)
# Now, calculate cosine similarity between all rows
cosine_sim = cosine_similarity(shampoo_lift)
# Output the cosine similarity matrix
print(cosine_sim)

# Calculate cosine similarity between all rows
cosine_sim = cosine_similarity(shampoo_lift)

cosine_sim_df = pd.DataFrame(cosine_sim, index=shampoo_lift.index, columns=shampoo_lift.index)

reviews_df = df[['product_name', 'Number of Reviews']].drop_duplicates()
reviews_df['Ranking'] = reviews_df['Number of Reviews'].rank(ascending=False).astype(int)
reviews_df.sort_values(by = 'Ranking', ascending = True, inplace = True)
reviews_df

from sklearn.manifold import MDS
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
rankings = reviews_df[['product_name', 'Ranking']].set_index('product_name').sort_values('Ranking')
# Step 3: Apply MDS
mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
mds_coords = mds.fit_transform(1 - cosine_sim_df)

# Step 4: Apply KMeans++ clustering on MDS coordinates
kmeans = KMeans(n_clusters=6, init='k-means++', random_state=42)
labels = kmeans.fit_predict(mds_coords)

# Step 5: Plot the MDS map with KMeans clustering
plt.figure(figsize=(10, 6))

# Plot the MDS points with cluster colors and numerical labels based on ranking
for i, coord in enumerate(mds_coords):
    product_name = rankings.index[i]  # Get the product name based on the ranking
    ranking_value = rankings.loc[product_name, 'Ranking']  # Get the ranking value
    plt.scatter(coord[0], coord[1], c=f'C{labels[i]}', s=100, cmap='viridis', edgecolor='k')
    plt.text(coord[0], coord[1], str(ranking_value), fontsize=9, ha='center', va='center')

plt.title('MDS Map with KMeans++ Clustering and Product Rankings', fontsize=14)
plt.xlabel('MDS Dimension 1')
plt.ylabel('MDS Dimension 2')
plt.grid(True)

# Step 6: Create a separate legend table with more spacing
fig_legend, ax_legend = plt.subplots(figsize=(12, 5))

# Splitting legend into columns with controlled text size and alignment
rows_per_col = 50  # Adjust this based on the number of shampoos
n_cols = (len(rankings.index) // rows_per_col) + 1
col_width = 0.7  # Adjust this value to add space between columns

# Display legend as multiple columns with increased spacing
legend_labels = [f"Rank {row['Ranking']}: {row.name}" for _, row in rankings.iterrows()]
for i in range(n_cols):
    col_data = legend_labels[i * rows_per_col:(i + 1) * rows_per_col]
    ax_legend.text(i * col_width, 1, "\n".join(col_data), fontsize=8, va='top', ha='left')

# Remove axes for the legend figure
ax_legend.axis("off")

plt.tight_layout()
plt.show()

#find the most similar substitute
cosine_sim_df.head()

new = input('Enter the name of the shampoo you want to find  a substitute for ')

cosine_sim_df[new].sort_values(ascending=False)[:10]



!pip install gensim
!pip install nltk

# Add cluster labels to the rankings DataFrame
rankings['Cluster'] = labels

grouped = rankings.groupby('Cluster')

reviews_with_clusters = df_new.merge(rankings[['Cluster']], left_on='product_name', right_index=True)
reviews_with_clusters

import nltk
nltk.download('punkt')

from nltk.corpus import stopwords
  from nltk.tokenize import word_tokenize
  from gensim import corpora
  from gensim.models import LdaModel

  # Get reviews per cluster
  for cluster_id, group in grouped:

      cluster_reviews = reviews_with_clusters[reviews_with_clusters['Cluster']== cluster_id]['product_review']
      # Preprocess each review
      processed_reviews = [remove_stopwords_and_tokenize(review) for review in cluster_reviews]
      if cluster_reviews.empty:
        print(f"No reviews found for cluster {cluster_id}")

      # Create dictionary and corpus for LDA
      dictionary = corpora.Dictionary(processed_reviews)
      corpus = [dictionary.doc2bow(review) for review in processed_reviews]

      # Apply LDA
      lda_model = LdaModel(corpus, num_topics=2, id2word=dictionary, passes=10, random_state=42)

      # Display topics
      print(f"Cluster {cluster_id} Topics:")
      for idx, topic in lda_model.print_topics(-1):
          print(f"Topic {idx}: {topic}")
      print("\n")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim import corpora
from gensim.models import LdaModel
from sklearn.cluster import KMeans
import numpy as np


# Define a preprocessing function
def preprocess_reviews(reviews):
    unwanted_words = {'good','great','product','really','love','use','scalp', 'shampoo', 'hair'}
    processed = []
    for review in reviews:

        words = word_tokenize(review.lower())
        filtered = [word for word in words if word.isalnum() and word not in stopwords.words('english') and word not in unwanted_words]
        processed.append(filtered)
    return processed

# Get reviews for topic modeling
reviews = reviews_with_clusters['product_review'].tolist()
processed_reviews = preprocess_reviews(reviews)

# Create dictionary and corpus for LDA
dictionary = corpora.Dictionary(processed_reviews)
corpus = [dictionary.doc2bow(review) for review in processed_reviews]

# Apply LDA
num_topics = 5
lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10, random_state=42)

# Get topic distributions for each review
topic_distributions = [lda_model.get_document_topics(bow) for bow in corpus]
topic_matrix = np.zeros((len(topic_distributions), num_topics))

for i, topics in enumerate(topic_distributions):
    for topic_id, prob in topics:
        topic_matrix[i, topic_id] = prob

# Perform KMeans clustering on topic distributions
num_clusters = 6
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(topic_matrix)

# Add cluster labels to the original reviews DataFrame
reviews_with_clusters['Cluster'] = kmeans.labels_

# Print cluster topics
for cluster_id in range(num_clusters):
    print(f"\nCluster {cluster_id} reviews:")
    print(reviews_with_clusters[reviews_with_clusters['Cluster'] == cluster_id]['product_review'])

#Keep colab up while you are away
import time
while True:
    print("Keeping session alive...")
    time.sleep(60)