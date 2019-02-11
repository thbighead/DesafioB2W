from flask import Flask, request, jsonify, abort, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import swapi

# configurando/acessando base de dados
conn = MongoClient()
db = conn['desafiob2w']
collection = db['starwars']

def storePlanet(name, climate, terrain):
    allPlanets = swapi.get_all("planets")
    newPlanet = {"name": name,
        "climate": climate,
        "terrain": terrain,
        "films_counting": 0,
        "created_at": datetime.datetime.utcnow()}
    for planet in allPlanets.items:
        if planet.name == name:
            newPlanet['films_counting'] = len(planet.films)
            break
    return str(collection.insert_one(newPlanet).inserted_id)

def destroyPlanet(filterObject):
    return collection.delete_many(filterObject).raw_result

def indexPlanets():
    planets = []
    for planet in collection.find():
        planet['_id'] = str(planet['_id'])
        planets.append(planet)
    return planets

def findPlanetByName(name):
    planets = []
    for planet in collection.find({'name':name}):
        planet['_id'] = str(planet['_id'])
        planets.append(planet)
    return planets

def findPlanetById(objId):
    planet = collection.find_one({'_id':ObjectId(objId)})
    planet['_id'] = str(planet['_id'])
    return planet

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
def welcome():
    return 'Welcome to my solution of B2W challenge!'

@app.route('/planet', methods=['GET', 'POST', 'DELETE'])
def deal_with_it():
    if request.method == 'GET':
        return jsonify(indexPlanets())
    if request.method == 'POST':
        if not request.json:
            abort(400)
        requestedData = request.get_json()
        return jsonify(storePlanet(requestedData['name'], requestedData['climate'], requestedData['terrain']))
    if request.method == 'DELETE':
        return jsonify(destroyPlanet(request.get_json()))

@app.route('/planet/id/<string:objId>')
def deal_with_id(objId):
    return jsonify(findPlanetById(objId))

@app.route('/planet/name/<string:name>')
def deal_with_name(name):
    return jsonify(findPlanetByName(name))