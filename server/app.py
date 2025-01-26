#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurant = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
        return make_response(restaurant, 200)

api.add_resource(Restaurants, '/restaurants')

class RestaurantsId(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        
        
        restaurant_pizzas = [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza_id": rp.pizza_id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients,
                } if rp.pizza else None,
            }
            for rp in restaurant.restaurant_pizzas
        ]

        response_data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": restaurant_pizzas,
        }

        return make_response(response_data, 200)

api.add_resource(RestaurantsId, '/restaurants/<int:id>')

class RestaurantsDelete(Resource):
    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        
        db.session.delete(restaurant)
        db.session.commit()

        return "", 204

api.add_resource(RestaurantsDelete, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
        return make_response(pizzas, 200)

api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        
        if not pizza_id or not restaurant_id or price is None:
            return make_response({"errors": ["Missing required fields"]}, 400)

        
        if price < 1 or price > 30:
            return make_response({"errors": ["validation errors"]}, 400)

        
        pizza = db.session.get(Pizza, pizza_id)
        restaurant = db.session.get(Restaurant, restaurant_id)

        if not pizza or not restaurant:
            return make_response({"errors": ["Pizza or Restaurant not found"]}, 404)

        
        new_restaurant_pizza = RestaurantPizza(
            pizza_id=pizza_id,
            restaurant_id=restaurant_id,
            price=price
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        
        response = {
            "id": new_restaurant_pizza.id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "pizza_id": pizza.id,
            "price": new_restaurant_pizza.price,
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            },
            "restaurant_id": restaurant.id
        }

        return make_response(response, 201)

api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
