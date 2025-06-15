class Ingredient:
    ingredient_name: str
    ingredient_definition: str

    def __init__(self, ingredient_name: str, ingredient_definitions: str):
        self.ingredient_name = ingredient_name
        self.ingredient_definition = ingredient_definitions

    @classmethod
    def from_json(cls, json_data):
        # Proper field presence check
        if 'ingredient_name' not in json_data or 'ingredient_definition' not in json_data:
            raise ValueError('Missing required fields')
        return cls(
            ingredient_name=json_data['ingredient_name'],
            ingredient_definitions=json_data['ingredient_definition']
        )