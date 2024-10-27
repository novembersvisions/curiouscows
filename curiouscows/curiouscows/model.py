import pandas as pd
import numpy as np
from itertools import combinations
from gensim.models import Word2Vec
from tqdm import tqdm
import ast
import random

# data = pd.read_csv('dataset/full_dataset.csv')
# data = data[data['source'] == 'Recipes1M']
# data['NER'] = data['NER'].apply(ast.literal_eval)

# training_pairs = []
# for ingredients in tqdm(data['NER'], desc="Creating pairs"):
#     pairs = list(combinations(ingredients, 2))
#     training_pairs.extend(pairs)

# model = Word2Vec(sentences=tqdm(training_pairs, desc="Training model"), vector_size=100, window=1, sg=1, min_count=5)
# model.save("recipe_word2vec.model")

def recommend_ingredients_single(ingredient, model, rand=True, min_similarity=0.5, max_similarity=0.7):
    if ingredient not in model.wv:
        return []

    candidate_recommendations = model.wv.most_similar(ingredient, topn=100000)
    
    filtered_candidates = [
        (ing, score) for ing, score in candidate_recommendations
        if ingredient not in ing and min_similarity <= score <= max_similarity
    ]
    
    n = random.randint(5,len(filtered_candidates)) if rand else 5
    return filtered_candidates[n-5:n]

def recommend_ingredients_multiple(ingredients, model, rand=True, min_similarity=0.5, max_similarity=0.7):
    valid_ingredients = [ing for ing in ingredients if ing in model.wv]
    if not valid_ingredients:
        return []

    mean_vector = np.mean([model.wv[ing] for ing in valid_ingredients], axis=0)
    candidate_recommendations = model.wv.similar_by_vector(mean_vector, topn=100000)
    
    filtered_candidates = [
        (ing, score) for ing, score in candidate_recommendations
        if all(original_ing not in ing for original_ing in valid_ingredients) and min_similarity <= score <= max_similarity
    ]
    
    n = random.randint(5,len(filtered_candidates)) if rand else 5
    return filtered_candidates[n-5:n]

# print("Single ingredient recommendation for 'apple':", recommend_ingredients_single("apple", model))
# print("Multiple ingredient recommendation for ['apple', 'cinnamon']:", recommend_ingredients_multiple(['apple', 'cinnamon'], model))