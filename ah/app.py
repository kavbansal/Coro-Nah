from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import googlemaps
import time

##FLASK INITIALIZATION
app = Flask(__name__, template_folder=".")

##DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placed.db' #DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #DB
db = SQLAlchemy(app) #DB

##DATABASE HELPER METHODS
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
		plc.rating_distancing = (plc.rating_distancing*(plc.count_rev-1) + rt1)/float(plc.count_rev)
		plc.rating_sanitisation = (plc.rating_sanitisation*(plc.count_rev-1) + rt1)/float(plc.count_rev)
		plc.rating_avg = (plc.rating_masks + plc.rating_distancing + plc.rating_sanitisation)/3.0
		db.session.commit()


##GOOGLE API
def NearbySearch(location, radius, type):
    # Define our search and initialize the search(using Nearby Search)
    result = gmaps.places_nearby(location=location, radius=radius, open_now=False, type=type)
    # Every time 20 results in total
    return result

def NearbySearch2nd(places_result):
    # Wait for second search (Must)
    time.sleep(2)
    # Store the next page of search
    result = gmaps.places_nearby(page_token=places_result['next_page_token'])
    return result

def StorePlaces(places_result):
    dict = {}  # The key is (place_id, name); the value is [vicinity, types, rate, number of reviews, lat, lng]
    # Loop the places in response results
    for place in places_result['results']:
        # Define place ID
        place_id = place['place_id']  # A unique ID for a place, required
        name = place['name']  # Name, required
        vicinity = place['vicinity']  # Address, if needed
        types = place['types']  # Types of this place (more than the searched type), if needed
        rate = 0
        num_of_reviews = 0
        lat = place['geometry']['location']['lat']
        lng = place['geometry']['location']['lng']
        dict[(place_id, name)] = [vicinity, types, rate, num_of_reviews, lat, lng]
    return dict

# Define api key (automatically get or filled by yourself, see below)
# from GoogleMapsAPIKey import get_my_key
# API_Key = get_my_key()

# ==========================================================
# ==========================================================
# Fill YOUR key get from Google (might change in the future)
API_Key = 'AIzaSyCceg_U0TSY0sASEeVcPV3WXw0NDYHL0j4'
# ==========================================================
# ==========================================================

# Define our client
gmaps = googlemaps.Client(key=API_Key)

# Locate the region (we "FIXED" 40km around JHU here)
location = '39.3299013,-76.6227064'  # coordinate of Johns Hopkins University, Homewood Campus
radius = 40000  # units: meters

# Initialize a set to store types supported by Google Places API
# See documentations in this link (https://developers.google.com/places/web-service/supported_types)
types_set = {"accounting", "airport", "amusement_park", "aquarium", "art_gallery", "atm", "bakery", "bank", "bar",
             "beauty_salon", "bicycle_store", "book_store", "bowling_alley", "bus_station", "cafe", "campground",
             "car_dealer", "car_rental", "car_repair", "car_wash", "casino", "cemetery", "church", "city_hall",
             "clothing_store", "convenience_store", "courthouse", "dentist", "department_store", "doctor", "drugstore",
             "electrician", "electronics_store", "embassy", "fire_station", "florist", "funeral_home", "furniture_store",
             "gas_station", "gym", "hair_care", "hardware_store", "hindu_temple", "home_goods_store", "hospital",
             "insurance_agency", "jewelry_store", "laundry", "lawyer", "library", "light_rail_station", "liquor_store",
             "local_government_office", "locksmith", "lodging", "meal_delivery", "meal_takeaway", "mosque", "movie_rental",
             "movie_theater", "moving_company", "museum", "night_club", "painter", "park", "parking", "pet_store",
             "pharmacy", "physiotherapist", "plumber", "police", "post_office", "primary_school", "real_estate_agency",
             "restaurant", "roofing_contractor", "rv_park", "school", "secondary_school", "shoe_store", "shopping_mall",
             "spa", "stadium", "storage", "store", "subway_station", "supermarket", "synagogue", "taxi_stand",
             "tourist_attraction", "train_station", "transit_station", "travel_agency", "university", "veterinary_care",
             "zoo"}

# Initialize a dictionary to store places
places_dict = {}  # The key is (place_id, name); the value is [vicinity, types, rate, number of reviews]

backName = "Cloud9"
@app.route("/")
def index():
    return render_template("SearchC9.html", frontName=backName)

@app.route("/SearchC9", methods=['post'])
def search():
    # Define the supported search type
    type = request.form.get("type")
    type = str.lower(type)

    if type in types_set:
        places_result = NearbySearch(location, radius, type)
        # Store the first page of search
        places_dict.update(StorePlaces(places_result))
        # places_result = NearbySearch2nd(places_result)
        # # Update the places dictionary
        # places_dict.update(StorePlaces(places_result))
        backType = type
        backDict = places_dict
        for items in backDict.keys():
            plc = PlaceDB.query.filter_by(place_id=items[0]).first()
            if plc is None:
                backDict[items][2] = 0
                backDict[items][3] = 0
            else:
                backDict[items][2] = round(plc.rating_avg,2)
                backDict[items][3] = round(plc.count_rev,2)
        return render_template("ResultC9.html", frontName=backName, frontType=backType, frontDict=backDict)
    else:
        return render_template("SearchC9.html", frontName=backName)

@app.route("/ResultC9", methods=['post'])
def comment():
    # Dive into detail page and can make comments
    place_id = request.form.get("place_id")
    name = request.form.get("name")
    address = places_dict[(place_id, name)][0]
    types = places_dict[(place_id, name)][1]
    plc = PlaceDB.query.filter_by(place_id=place_id).first()
    if plc is None:
        rate = 0
        num_of_views = 0
        rt1=0
        rt2=0
        rt3=0
    else:
        rate = round(plc.rating_avg,2)
        num_of_views = round(plc.count_rev,2)
        rt1=round(plc.rating_masks,2)
        rt2=round(plc.rating_distancing,2)
        rt3=round(plc.rating_sanitisation,2)
    return render_template("CommentC9.html", frontName=backName, frontPlaceName=name, frontAddress=address,
                           frontRate=rate, frontNum=num_of_views, frontPlaceID = place_id, frontrt1=rt1,frontrt2=rt2,frontrt3=rt3)

@app.route("/CommentC9", methods=['POST'])
def rev():
    rt1 = request.form.get("i1")
    rt2 = request.form.get("i2")
    rt3 = request.form.get("i3")
    plcid = request.form.get("place_id")
    updateDB(plcid,int(rt1),int(rt2),int(rt3))
    return render_template("SearchC9.html", frontName=backName)


if __name__ == "__main__":
	app.run(debug=True)
