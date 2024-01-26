import requests
import json
import uuid
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from tabulate import tabulate
from tkinter import *
from tkinter import ttk
from functools import partial

# Creates a tkinter gui
class DisplayWindow:
    def __init__(self, root):

        self.root = root
        root.title("Closest Points")

        # Variables
        self.name_address = StringVar()
        self.type_establishment = StringVar()
        self.output_label = StringVar()
        self.lati_longi = None

        # Mainframe
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(W, E, N, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Labels
        loc_label = ttk.Label(mainframe, text="Location: ")
        loc_label.grid(column=1, row=1, sticky=(W, E))

        type_label = ttk.Label(mainframe, text="Type of establishment: ")
        type_label.grid(column=1, row=2, sticky=(W, E))

        result_label = ttk.Label(
            mainframe, textvariable=self.output_label, font=("Consolas", 10)
        )
        result_label.grid(column=2, row=5, sticky=(W, S, N))

        empty_label = ttk.Label(mainframe, text="")
        empty_label.grid(column=4, row=4, sticky=(E))

        # Entries
        loc_entry = ttk.Entry(mainframe, width=60, textvariable=self.name_address)
        loc_entry.grid(column=2, row=1, sticky=(W))

        type_entry = ttk.Entry(
            mainframe, width=60, textvariable=self.type_establishment
        )
        type_entry.grid(column=2, row=2, sticky=(W))

        # Buttons
        search_button = ttk.Button(
            mainframe, text="Search", command=partial(get_places, self)
        )
        search_button.grid(column=2, row=3, sticky=(W))

        save_to_file_button = ttk.Button(
            mainframe, text="Save", command=self.output_to_file
        )
        save_to_file_button.grid(column=2, row=4, sticky=(W))

        # Focus
        loc_entry.focus()

        # Key bind
        root.bind("<Return>", partial(get_places, self))

    # Returns the latitude and longitude based on the object address
    def get_lati_longi(self):
        getaddress = str(self.name_address.get())
        geolocator = Nominatim(user_agent="closestpointscs50p")
        try:
            location = geolocator.geocode(getaddress)
            self.lati_longi = f"{location.latitude},{location.longitude}"
        except AttributeError as Error:
            print("Invalid location.")
        return self.lati_longi

    # Save the search result to a new txt file
    def output_to_file(self, event=None):
        output = self.output_label.get()
        try:
            with open(str(uuid.uuid4()) + ".txt", "w", encoding="utf-8") as file:
                file.write(output)
        except IOError:
            print("Error: Unable to save file.")

def get_places(self, event=None):
    location = self.get_lati_longi()
    keyword = self.type_establishment.get()

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"  # google places api
    params = {
        "location": location,  # format = "latitude,longitude"
        "rankby": "distance",  # rank the api return by the distance from the input location
        "keyword": keyword,  # keyword to search for, might be esblish name or type
        "key": "AIzaSyAVU5xnjIzrb78Tqw9UuvY_fWP4xHiAAk4",  # needs to hide this key before uploading with dotenv//env variable
    }
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as Error:
        print("Error: Failed API request.")

    try:
        places = response.json()["results"]  # get just the list ["result"] that comes inside the dict api return
        if places == []:
            raise ValueError("No results found.")
    except ValueError as Error:
        print(Error)

    places = places[:10]  # places == list of dicts/places, cuts in the 10th place
    places = process_json(self, places)
    self.output_label.set(places)


def process_json(self, placesjson):
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

        user_location = self.lati_longi
        place_location = place.get("geometry").get("location")
        place_location = f"{place_location['lat']},{place_location['lng']}"

        distance = great_circle(
            user_location, place_location
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
