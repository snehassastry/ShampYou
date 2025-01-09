# ShampYou
Discover the Perfect Shampoo for Your Needs
Choosing the right shampoo can be challenging. With countless options on the market, it's easy to feel overwhelmed by trial and error. Many products are lost in the "long tail," and the most popular options may not always address your specific concerns.

ShampYou is designed to bridge this gap by analyzing customer reviews and offering personalized shampoo recommendations tailored to individual preferences.

## Project Overview
This project comprises two main parts:

### Part 1: Web Scraping:
Objective: Extract customer reviews and descriptions for 200 shampoos from Influenster.

Reasoning: Limiting the dataset to 200 shampoos ensures manageable data processing, even when using CSV files.

### Part 2: Analysis and Recommendation
Goal: Understand key attributes discussed in reviews and provide tailored shampoo recommendations.

Process:
Analyze frequently co-discussed attributes -> Users specify the three attributes that matter most to them ->Implement three recommendation methods:
Cosine Similarity + VADER Sentiment Score: Calculates similarity between user preferences and reviews, factoring in sentiment.

SpaCy Similarity + VADER Sentiment Score: Leverages SpaCy embeddings combined with sentiment analysis.

Popularity-Based Ranking: Highlights the most-reviewed shampoos.

### Observation: The Cosine Similarity method with VADER scores delivered superior results, as user preferences aligned well with explicit review mentions.

## Extension: Long Tail Analysis
Created an MDS (Multidimensional Scaling) map to visualize shampoo attributes and explore long-tail behavior.
This visualization aids in understanding niche products that cater to unique needs.

## Results and Use Cases
The accompanying presentation showcases interesting use cases where the ShampYou code was tested. These examples highlight how the recommendation system effectively identifies products tailored to diverse user requirements.

### Disclaimer : This project was done as a part of the Term project for the Unstructured Data analytics course at UT Austin. This work is a term project and is not affiliated with Influenster or any shampoo brands.

### Collaborators : Twinkle Panda, Vishwa Patel, Dameli, Kimberly J Simmonds 
