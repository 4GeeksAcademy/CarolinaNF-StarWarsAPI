"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

CURRENT_USER_ID = 1


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route("/")
def sitemap():
    return generate_sitemap(app)


@app.route("/people", methods=["GET"])
def get_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_one_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Person not found"}), 404
    return jsonify(person.serialize()), 200



@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    user = User.query.get(CURRENT_USER_ID)
    if user is None:
        return jsonify({"msg": "Current user not found"}), 404

    favorites = {
        "people": [person.serialize() for person in user.favorite_people],
        "planets": [planet.serialize() for planet in user.favorite_planets]
    }
    return jsonify(favorites), 200


@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    user = User.query.get(CURRENT_USER_ID)
    planet = Planet.query.get(planet_id)

    if user is None:
        return jsonify({"msg": "Current user not found"}), 404

    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    if planet in user.favorite_planets:
        return jsonify({"msg": "Planet already in favorites"}), 400

    user.favorite_planets.append(planet)
    db.session.commit()

    return jsonify({"msg": "Favorite planet added successfully"}), 201


@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    user = User.query.get(CURRENT_USER_ID)
    planet = Planet.query.get(planet_id)

    if user is None:
        return jsonify({"msg": "Current user not found"}), 404

    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    if planet not in user.favorite_planets:
        return jsonify({"msg": "Planet is not in favorites"}), 404

    user.favorite_planets.remove(planet)
    db.session.commit()

    return jsonify({"msg": "Favorite planet deleted successfully"}), 200


@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_people(people_id):
    user = User.query.get(CURRENT_USER_ID)
    person = People.query.get(people_id)

    if user is None:
        return jsonify({"msg": "Current user not found"}), 404

    if person is None:
        return jsonify({"msg": "Person not found"}), 404

    if person in user.favorite_people:
        return jsonify({"msg": "Person already in favorites"}), 400

    user.favorite_people.append(person)
    db.session.commit()

    return jsonify({"msg": "Favorite person added successfully"}), 201


@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    user = User.query.get(CURRENT_USER_ID)
    person = People.query.get(people_id)

    if user is None:
        return jsonify({"msg": "Current user not found"}), 404

    if person is None:
        return jsonify({"msg": "Person not found"}), 404

    if person not in user.favorite_people:
        return jsonify({"msg": "Person is not in favorites"}), 404

    user.favorite_people.remove(person)
    db.session.commit()

    return jsonify({"msg": "Favorite person deleted successfully"}), 200


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=True)
