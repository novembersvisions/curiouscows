from django.shortcuts import render
from django.http import HttpResponse, request
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from django.conf import settings
from .model import recommend_ingredients_single, recommend_ingredients_multiple
from gensim.models import Word2Vec
from django.apps import apps

@csrf_exempt
def index(request):
    if request.POST:
        ingredients = request.POST['ingredients'].strip()
        style = request.POST['style'].strip() # type of dish: entree, appetizer, dessert, snack
        flavor = request.POST['flavor'].strip() # flavor profile
        diet = request.POST['diet'].strip() # diet preferences: high fiber, vegetarian, etc
        budget = request.POST['budget'].strip()

        # send information to model, then Gemini wrapper

        if ingredients == '':
            context = {
            'ingredient_feedback': '',
            'sticky_style': style,
            'sticky_flavor': flavor,
            'sticky_diet': diet,
            'sticky_budget': budget,
            'display_form': '',
            'display_confirm': 'hidden',
            }
        else:
            model = apps.get_app_config('curiouscows').model

            if "," in ingredients:
              multiple_ing = ingredients.split(",")
              ingredient_list = recommend_ingredients_multiple(multiple_ing,model,True)
            else:
              ingredient_list = recommend_ingredients_single(ingredients,model,True)

            ingredient_str = ingredients + ", "
            for i in range(len(ingredient_list)):
              ingredient_str += ingredient_list[i][0]
              if i != len(ingredient_list)-1:
                ingredient_str += ", "
               
            recipe = generate_ai_response(ingredient_str, style, flavor, diet, budget)

          
            # formatted_recipe = recipe.replace("**", "").replace("", "")
            # formatted_recipe = recipe.replace("**", " ")
            formatted_recipe = ""
            for s in recipe:
               if s != "*":
                  formatted_recipe+=s
               else:
                  formatted_recipe+=""
            formatted_recipe = formatted_recipe.replace("#","")

            context = {
            'display_form': 'hidden',
            'display_confirm': '',
            'recipe': formatted_recipe,
            'ingredients': ingredient_str,
            'style': style,
            'ingredient_feedback': 'hidden'
            }
            render(request, 'index.html', context)
    else:
      context = {
      'display_form': '',
      'display_confirm': 'hidden',
      'ingredient_feedback': 'hidden',
      }
    return render(request, 'index.html', context)

def generate_ai_response(ingredients, style, flavor, diet, budget):
    prompt = "Generate a recipe with "+ingredients
    for i in [("style",style),("flavor",flavor),("diet",diet),("budget",budget)]:
        if i[1]:
            prompt += " and "+i[0]+" "+i[1]
            
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def error404(request):
    return render(request, '404.html')