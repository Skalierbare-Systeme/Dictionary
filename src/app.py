from flask import Flask, request, jsonify
from redis import RedisError

from src.redis_client import connect_to_redis, add_new_pair, get_pair, delete_pair, get_multiple_pairs
from src.models import Ingredient

app = Flask(__name__)


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
    keys = request.args.getlist('ingredient_names')
    try:
        ingredient = get_multiple_pairs(connect_to_redis(), keys)

    except RedisError as e:
        return jsonify({'error': str(e)}), 404
    return jsonify(ingredient.__dict__), 200


if __name__ == '__main__':
    app.run()
