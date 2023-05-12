import random as rnd
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
app.app_context().push()    
db.create_all()
@app.route("/")
def home():
    return render_template("index.html")

## HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def random():
    cafes = db.session.query(Cafe).all()
    random_cafe = rnd.choice(cafes)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })

@app.route("/all", methods=["GET"])
def all():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes = [cafe.to_dict() for cafe in cafes])

@app.route("/search")
def search():
    query_location = request.args.get("location")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe = cafe.to_dict())
    else:
        return jsonify(error = {"Not Found": "Sorry,we don't have a cafe at that location"})
    
## HTTP POST - Create Record
@app.route("/add", methods=["POST", "GET"])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})    

## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = db.session.query(Cafe).get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response= {"success": "Successfully Updated The Price."})
    else:
        return jsonify(error = {"Not Found": "Sorry a cafe with that id was not found in database."})
    
## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    api_key = request.args.get("api_key")
    cafe_to_delete = db.session.query(Cafe).get(cafe_id)
    if cafe_to_delete:
        if api_key == "TopSecretAPIKey":
            db.session.delete(cafe_to_delete)
            return jsonify(response = {"success": "Successfully deleted the cafe."})
        else:
            return jsonify(error= {"error": "Sorry, thats not allowed. Make sure you have the correct api key!"})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in database."})    


if __name__ == '__main__':
    app.run(debug=True)
