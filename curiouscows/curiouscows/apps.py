from django.apps import AppConfig
from gensim.models import Word2Vec

class YourAppConfig(AppConfig):
    name = 'curiouscows'
    model = None

    def ready(self):
        self.model = Word2Vec.load("curiouscows/recipe_word2vec.model")