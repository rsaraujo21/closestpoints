import requests
import json
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from tabulate import tabulate


def main():
    print(process_json(get_places(lati_longi, get_type_establishment())))


def get_places(location, keyword):
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
    return places[:10]  # places == list of dicts/places, cuts in the 10th place


def get_lati_longi():
    name_address = input(
        "Location:"
    )  # the address can be as specific as desired, just a city or even a specific place
    geolocator = Nominatim(user_agent="closestpointscs50p")  # name of the project
    location = geolocator.geocode(
        name_address
    )  # create a location object with lati,longi,address, and the raw request
    return f"{location.latitude},{location.longitude}"


lati_longi = get_lati_longi()


def get_type_establishment():
    return input("Type of establishment:")


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


if __name__ == "__main__":
    main()
