from flask import Flask, request, jsonify
from redis import RedisError

from src.redis_client import connect_to_redis, add_new_pair, get_pair, delete_pair, get_multiple_pairs
from src.models import Ingredient
from flask_cors import CORS
app = Flask(__name__)
CORS(app) 

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/ingredient/<ingredient_name>', methods=['GET'])
def get_ingredient(ingredient_name: str):
    try:
        ingredient = get_pair(connect_to_redis(), ingredient_name)
    except RedisError as e:
        return jsonify({'error': str(e)}), 404
    return jsonify(ingredient.__dict__), 200


@app.route('/ingredient/<ingredient_name>', methods=['DELETE'])
def delete_ingredient(ingredient_name: str):
    connection = connect_to_redis()
    try:
        delete_pair(connection, ingredient_name)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({'success': 'Ingredient was deleted from Database'}), 200


@app.route('/ingredient', methods=['POST'])
def add_ingredient():
    new_ingredient = Ingredient.from_json(request.json)
    try:
        connection = connect_to_redis()
        add_new_pair(connection, new_ingredient)
    except RedisError as e:
        return jsonify({'error': str(e)}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({'success': 'Ingredient was added to Database'}), 200




@app.route('/ingredient', methods=['GET'])
def get_multiple_ingredients():
    # Example: /ingredient?ingredient_names=a&ingredient_names=sea
    # keys will be ['a', 'sea']
    keys = request.args.getlist('ingredient_names')
    
    try:
        # Let's assume get_multiple_pairs returns a list, which may contain
        # Ingredient objects or None for keys that were not found.
        # e.g., [Ingredient('a', '...'), Ingredient('sea', '...')]
        ingredient_objects = get_multiple_pairs(connect_to_redis(), keys)

        # --- THIS IS THE CRITICAL FIX ---
        # We now create an empty dictionary that will be sent as JSON.
        response_dictionary = {}

        # We loop through the Ingredient objects we got from the database.
        for ingredient in ingredient_objects:
            # We must check if the ingredient is a valid object and not None.
            if ingredient and hasattr(ingredient, 'ingredient_name'):
                # We build the dictionary in the format the frontend wants: { "word": "definition" }
                response_dictionary[ingredient.ingredient_name] = ingredient.ingredient_definition
        
        # Now, we pass the simple, serializable dictionary to jsonify.
        return jsonify(response_dictionary), 200

    except RedisError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        # This will catch the 'not JSON serializable' error and others.
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500



if __name__ == '__main__':
    app.run()
