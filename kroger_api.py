import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()
KROGER_API_BASE_URL = os.getenv("KROGER_API_BASE_URL_PROD")

def get_kroger_auth_token():
    KROGER_AUTH_TOKEN = None
    auth_url = f"{KROGER_API_BASE_URL}/connect/oauth2/token"
    client_id = os.getenv("KROGER_CLIENT_ID_PROD")
    client_secret = os.getenv("KROGER_CLIENT_SECRET_PROD")
    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    data = {"grant_type": "client_credentials", "scope": "product.compact"}

    response = requests.post(auth_url, auth=auth, data=data)

    if response.status_code == 200:
        KROGER_AUTH_TOKEN = response.json()["access_token"]
        return KROGER_AUTH_TOKEN
    else:
        print(f"Error obtaining auth token: {response.status_code} - {response.text}")
        return None

def get_kroger_locations(
    zipcode=None, radius=None, limit=None, latlong=None, auth_token=None
):

    filters = []

    if zipcode:
        filters.append(f"filter.zipCode.near={zipcode}")
    if radius:
        filters.append(f"filter.radiusInMiles={radius}")
    if limit:
        filters.append(f"filter.limit={limit}")
    if latlong:
        filters.append(f"filter.latLong.near={latlong}")

    filter_string = "&".join(filters)

    url = f"{KROGER_API_BASE_URL}/locations?{filter_string}"

    print(f"Fetching locations with URL: {url}")

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching locations: {response.status_code} - {response.text}")
        return None

def create_kroger_location_url(location: dict) -> str:
    state = location["address"]["state"].lower()
    city = location["address"]["city"].lower()
    store_name = (
        re.sub(r"^'?Kroger\s*-\s*|'+$", "", location["name"])
        .strip()
        .lower()
        .replace(" ", "-")
    )
    division = location["divisionNumber"].lower()
    store_number = location["storeNumber"]

    result = f"https://www.kroger.com/stores/grocery/{state}/{city}/{store_name}/{division}/{store_number}/"

    return result

def kroger_product_search(
    search_term,
    auth_token,
    location_id=None,
    product_id=None,
    brand=None,
    fulfillment=None,
    limit=None,
):

    filters = []
    if location_id:
        filters.append(f"filter.locationId={location_id}")
    if product_id:
        filters.append(f"filter.productId={product_id}")
    if brand:
        filters.append(f"filter.brand={brand}")
    if fulfillment:
        filters.append(f"filter.fulfillment={fulfillment}")
    if limit:
        filters.append(f"filter.limit={limit}")

    filter_string = "&".join(filters)

    url = f"{KROGER_API_BASE_URL}/products?filter.term={search_term}&{filter_string}"

    print(f"Fetching products with URL: {url}")

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching products: {response.status_code} - {response.text}")
        return None

def get_kroger_product_listings(UPC, location_id=None, auth_token=None):

    filters = []

    if location_id:
        filters.append(f"filter.locationId={location_id}")

    filter_string = "&".join(filters)

    url = f"{KROGER_API_BASE_URL}/products/{UPC}?{filter_string}"

    print(f"Fetching product listings with URL: {url}")

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"Error fetching product listings: {response.status_code} - {response.text}"
        )