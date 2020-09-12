# ==============================================================
# ==============================================================
# Edited by Xuhua 'Cloud9' Sun (xsun57@jhu.edu) in HopHacks 2020
# Following Tutorials for Google APIs with Python
# ==============================================================
# ==============================================================

from flask import Flask, render_template, request
import googlemaps
import time
# import pprint

def StorePlaces(places_results):
    dict = {}  # The key is (place_id, name); the value is [vicinity, types, rate, number of reviews]
    # Loop the places in response results
    for place in places_result['results']:
        # Define place ID
        place_id = place['place_id']  # A unique ID for a place, required
        name = place['name']  # Name, required
        vicinity = place['vicinity']  # Address, if needed
        types = place['types']  # Types of this place (more than the searched type), if needed
        rate = 0
        num_of_reviews = 0
        dict[(place_id, name)] = [vicinity, types, rate, num_of_reviews]
    return dict

# Define api key (automatically get or filled by yourself, see below)
# from GoogleMapsAPIKey import get_my_key
# API_Key = get_my_key()

# ==========================================================
# ==========================================================
# Fill YOUR key get from Google (might change in the future)
API_Key = 'AIzaSyDtxFWPkJsohSkOvf0XxSfXRQU0Uyf621E'
# ==========================================================
# ==========================================================

app = Flask(__name__, template_folder=".")

# Define our client
gmaps = googlemaps.Client(key=API_Key)

# Initialize a dictionary to store places
places_dict = {}  # The key is (place_id, name); the value is [vicinity, types, rate, number of reviews]

# Locate the region
location = '39.3299013,-76.6227064'  # coordinate of Johns Hopkins University, Homewood Campus
radius = 40000  # units: meters
# Define the supported search type (we use cafe here)
type = 'cafe'
# Define our search and initialize the search(using Nearby Search)
places_result = gmaps.places_nearby(location=location, radius=radius, open_now=False, type=type)
# Every time 20 results in total

# Store the first page of search
places_dict = StorePlaces(places_result)

# Wait for second search (Must)
time.sleep(3)
# Store the next page of search
places_result = gmaps.places_nearby(page_token=places_result['next_page_token'])
# Update the places dictionary
places_dict.update(StorePlaces(places_result))

# # Print the Results
# for item in places_dict.keys():
#     print('Name:', item[1], '(Address:', places_dict[item][0], ')')
#     # print('Related Types:', places_dict[item][1])
#     print('Total Rate:', places_dict[item][2], '(with', places_dict[item][3], 'views currently)')
#     print('\n')

@app.route("/")
def index():
    backName = "Cloud9"
    backLst = []
    backDict = places_dict
    return render_template("cloud9.html", frontName=backName, frontLst=backLst, frontDict=backDict)

if __name__ == '__main__':
    app.run(debug=True)


