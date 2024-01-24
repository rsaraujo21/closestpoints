import requests
import json
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from tabulate import tabulate
from tkinter import *
from tkinter import ttk

class DisplayWindow:
    def __init__(self, root):

        root.title("Closest Points")

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(W, E, N, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Labels
        loc_label = ttk.Label(mainframe, text="Location: ")
        loc_label.grid(column=1, row=1, sticky=(W, E))

        type_label = ttk.Label(mainframe, text="Type of establishment: ")
        type_label.grid(column=1, row=2, sticky=(W, E))

        # Entries
        loc_entry = ttk.Entry(mainframe, width=60, textvariable=name_address) # needs textvariable= to location
        loc_entry.grid(column=2, row=1, sticky=(W, E))

        type_entry = ttk.Entry(mainframe, width=60, textvariable=type_establishment) #needs textvariable= to type of establishment
        type_entry.grid(column=2, row=2, sticky=(W, E))

        # Buttons
        search_button = ttk.Button(mainframe, text="Search", command=get_places) # needs command= get_places
        search_button.grid(column=2, row=3, sticky=(W, E))

        # Output label
        result_label = ttk.Label(mainframe, textvariable=) # needs change text= to textvariable= output
        result_label.grid(column=2, row=4, sticky=(W, E, S, N))


name_address = StringVar()
type_establishment = StringVar()
output_label = StringVar()





def get_places(args):

    location = get_lati_longi(name_address.get())
    keyword = type_establishment.get()

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"  # google places api
    params = {
        "location": location,  # format = "latitude,longitude"
        "rankby": "distance",  # rank the api return by the distance from the input location
        "keyword": keyword,  # keyword to search for, might be esblish name or type
        "key": "AIzaSyAVU5xnjIzrb78Tqw9UuvY_fWP4xHiAAk4",  # needs to hide this key before uploading with dotenv//env variable
    }
    response = requests.get(url, params=params)
    places = response.json()[
        "results"
    ]  # get just the list ["result"] that comes inside the dict api return
    places = places[:10]  # places == list of dicts/places, cuts in the 10th place
    places = process_json(places)

def get_lati_longi(name_address):
    geolocator = Nominatim(user_agent="closestpointscs50p")  # name of the project
    location = geolocator.geocode(
        name_address
    )  # create a location object with lati,longi,address, and the raw request
    return f"{location.latitude},{location.longitude}"



def process_json(placesjson):
    list_places = []  # list that the places dicts will be stored
    for place in placesjson:
        status = place.get("opening_hours", {}).get(
            "open_now"
        )  # dealing with the opening_hours key and value(dict)
        status = (
            "Open"
            if status is True
            else "Closed"
            if status is False
            else "Not Available"
        )

        user_location = lati_longi
        place_location = place.get("geometry").get("location")
        place_location = f"{place_location['lat']},{place_location['lng']}"
        distance = great_circle(
            lati_longi, place_location
        ).km  # calc the distance using the lat/lon, of the two points with great_circle
        if distance < 1:
            distance = f"{distance * 1000:.0f}m"
        else:
            distance = f"{distance:.1f}km"

        list_places.append(
            {
                "Name": place.get("name", "Not Available"),
                "Status": status,
                "Rating": place.get("rating", "Not Available"),
                "User Ratings": place.get("user_ratings_total", "Not Available"),
                "Distance": distance,
                "Address": place.get("vicinity", "Not Available"),
            }
        )
    return tabulate(list_places, headers="keys", tablefmt="fancy_grid")



root = Tk()
DisplayWindow(root)
root.mainloop()
