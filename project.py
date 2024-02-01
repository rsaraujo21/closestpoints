import os
import requests
import json
import uuid
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from tabulate import tabulate
from tkinter import *
from tkinter import ttk
from functools import partial
from dotenv import find_dotenv, load_dotenv

# Get the places api key from the env file
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
API_KEY = os.getenv("API_KEY")


# Creates a tkinter gui
class DisplayWindow:
    def __init__(self, root):
        self.root = root
        root.title("Closest Points")

        # Variables
        self.name_address = StringVar()
        self.type_establishment = StringVar()
        self.output_label = StringVar()
        self.error_label = StringVar()
        self.lati_longi = None

        # Mainframe
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(W, E, N, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Labels
        loc_label = ttk.Label(mainframe, text="Location: ", font=("Consolas", 10))
        loc_label.grid(column=1, row=1, sticky=(W, E))

        type_label = ttk.Label(
            mainframe, text="Type of establishment: ", font=("Consolas", 10)
        )
        type_label.grid(column=1, row=2, sticky=(W, E))

        result_label = ttk.Label(
            mainframe, textvariable=self.output_label, font=("Consolas", 10)
        )
        result_label.grid(column=2, row=5, sticky=(W, S, N))

        error_label = ttk.Label(
            mainframe, textvariable=self.error_label, font=("Consolas", 10)
        )
        error_label.grid(column=1, row=3, sticky=(W, E))

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
            mainframe, text="Save", command=partial(output_to_file, self)
        )
        save_to_file_button.grid(column=2, row=4, sticky=(W))

        # Focus
        loc_entry.focus()

        # Key bind
        root.bind("<Return>", partial(get_places, self))


# Does an api call to google places api, returns the json response
def places_api_call(location, keyword, self):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,
        "rankby": "distance",
        "keyword": keyword,
        "key": API_KEY,
    }
    # ConnectionError/Timeout/TooManyRedirects
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as Error:
        self.error_label.set("Error: Failed API request.")
        response = {"results": []}

    return response


# Calls places_api_call to get the json response, calls process_json to return the formatted output
def get_places(self, event=None):
    self.error_label.set("")  # Clear the error label before each search
    location = get_lati_longi(self)
    keyword = self.type_establishment.get()

    response = places_api_call(location, keyword, self)
    # API request succeed but no results found
    try:
        places = response.json()["results"]
        if places == []:
            raise ValueError("No results found.")
    except ValueError as Error:
        self.error_label.set(Error)

    places = places[:10]  # Limits the output to 10 places from 20
    places = process_json(
        self, places
    )  # Format the output(tabulate), returns tabulate data[0], raw data[1]
    self.output_label.set(places[0])  # Set the output in the textvariable label
    self.name_address.set("")
    self.type_establishment.set("")


# Receives the json file, get the desired values, calls calc_distance to get distance, returns formatted data
def process_json(self, placesjson):
    list_places = []
    for place in placesjson:
        # Dealing with opening_hours optional key and value
        status = place.get("opening_hours", {}).get("open_now")
        status = (
            "Open"
            if status is True
            else "Closed"
            if status is False
            else "Not Available"
        )

        # Getting distance between two points with calc_distance
        user_location = self.lati_longi
        place_location = place.get("geometry").get("location")
        place_location = f"{place_location['lat']},{place_location['lng']}"
        distance = calc_distance(user_location, place_location)

        list_places.append(
            {
                "Name": place.get("name", "Not Available")[:50],
                "Status": status,
                "Rating": place.get("rating", "Not Available"),
                "User Ratings": place.get("user_ratings_total", "Not Available"),
                "Distance": distance,
                "Address": place.get("vicinity", "Not Available"),
            }
        )
    # Tabulate the list of places, return tabulated list to output, and the list to test purposes
    return (tabulate(list_places, headers="keys", tablefmt="fancy_grid"), list_places)


# Uses geopy/great_circle to get the (rough)distance between two points
def calc_distance(user_location, place_location):
    distance = great_circle(user_location, place_location).km
    if distance < 1:
        distance = f"{distance * 1000:.0f}m"
    else:
        distance = f"{distance:.1f}km"
    return distance


# Returns the latitude and longitude based on the object address
def get_lati_longi(self):
    getaddress = str(self.name_address.get())
    geolocator = Nominatim(user_agent="closestpointscs50p")
    # Invalid location
    try:
        location = geolocator.geocode(getaddress)
        self.lati_longi = f"{location.latitude},{location.longitude}"
    except AttributeError as Error:
        self.error_label.set("Invalid location.")
    return self.lati_longi


# Save the search result to a new txt file
def output_to_file(self, event=None):
    output = self.output_label.get()
    # Error when saving output
    try:
        with open(str(uuid.uuid4()) + ".txt", "w", encoding="utf-8") as file:
            file.write(output)
    except IOError:
        self.error_label.set("Error: Unable to save file.")


if __name__ == "__main__":
    root = Tk()
    DisplayWindow(root)
    root.mainloop()
