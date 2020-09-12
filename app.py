from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder=".")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placed.db' #DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #DB
db = SQLAlchemy(app) #DB

class PlaceDB(db.Model): #DB
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(150), unique=True, nullable=False)
    rating_masks = db.Column(db.Float, unique=False, nullable=False)
    rating_distancing = db.Column(db.Float, unique=False, nullable=False)
    rating_sanitisation = db.Column(db.Float, unique=False, nullable=False)
    rating_avg = db.Column(db.Float, unique=False, nullable=False)
    count_rev = db.Column(db.Integer, unique=False, nullable=False)
    

def add_to_DB(placeID, rt1, rt2, rt3): #DB
	aveg= (rt1+rt2+rt3)/3.0
	plc = PlaceDB(place_id=placeID, rating_masks=rt1, rating_distancing =rt2, rating_sanitisation= rt3, rating_avg=aveg, count_rev=1 )
	db.session.add(plc)
	db.session.commit()
	

def updateDB(placeID, rt1, rt2, rt3): #DB
	plc = PlaceDB.query.filter_by(place_id=placeID).first()
	if plc is None:
		add_to_DB(placeID, rt1, rt2, rt3)
	else:
		plc.count_rev += 1
		plc.rating_masks = (plc.rating_masks*(plc.count_rev-1) + rt1)/float(plc.count_rev)
		plc.rating_distancing = (plc.rating_masks*(plc.count_rev-1) + rt1)/float(plc.count_rev)
		plc.rating_sanitisation = (plc.rating_masks*(plc.count_rev-1) + rt1)/float(plc.count_rev)
		plc.rating_avg = (plc.rating_masks + plc.rating_distancing + plc.rating_sanitisation)/3.0
		db.session.commit()

@app.route("/")
def index():
	return render_template("index.html")

if __name__ == "__main__":
	app.run(debug=True)
