from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, result_tuple
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

API_KEY = "TopSecretAPIKey"

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    # return jsonify(cafe={"id": random_cafe.id,
    #                "name": random_cafe.name,
    #                "map_url": random_cafe.map_url,
    #                "img_url": random_cafe.img_url,
    #                "location": random_cafe.location,
    #                "seat": random_cafe.seats,
    #                "has_toilet": random_cafe.has_toilet,
    #                "has_wifi": random_cafe.has_wifi,
    #                "has_sockets": random_cafe.has_sockets,
    #                "can_take_calls": random_cafe.can_take_calls,
    #                "coffee_price": random_cafe.coffee_price})
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    cafes = [cafe.to_dict() for cafe in all_cafes]
    return jsonify(cafes=cafes)

@app.route('/search')
def search_cafes():
    cafe_location=request.args.get('loc')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == cafe_location))
    cafes = result.scalars().all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not found": "Sorry, we don't have a cafe in that location."})

# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
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


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("price")
    # cafe = db.get_or_404(Cafe, cafe_id) # Nie pozwala wyświetlić json z errorem
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar() # Pozwala wyświetlić json z errorem
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success='Successfully updated the price.'), 200
    else:
        return jsonify(error={'Not found': "There is no cafe with this id"}), 404

# HTTP DELETE - Delete Record
@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key = request.args.get('api-key')
    if api_key == API_KEY:
        cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success="Successfully deleted the cafe"), 200
        else:
            return jsonify(error={'Not found': "There is no cafe with this id"}), 404
    else:
        return jsonify(error={'Not authorized': 'You are not authorized to perform this request. Check if you have the '
                                                'valid API Key.'}), 403


if __name__ == '__main__':
    app.run(debug=True)
