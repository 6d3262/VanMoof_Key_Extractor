import argparse
import base64
import getpass
import os
import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def authenticate(username, password, API_URL, API_KEY):
    # Prepare headers for authentication
    headers = {
        "Api-Key": API_KEY,
        "Authorization": "Basic "
        + base64.b64encode((username + ":" + password).encode()).decode("ascii"),
    }

    # Send POST request to authenticate
    result = requests.post(API_URL + "/authenticate", headers=headers)
    result.raise_for_status()  # Will raise an exception for HTTP errors

    # Parse JSON response
    result = result.json()

    # Check for errors in response
    if "error" in result:
        logging.error(result)
        raise Exception("Authentication error")

    # Extract token from response
    token = result.get("token")
    if not token:
        raise Exception("No token in response.")
    
    return token

def get_customer_data(token, API_URL, API_KEY):
    # Prepare headers for customer data request
    headers = {
        "Api-Key": API_KEY,
        "Authorization": "Bearer " + token,
    }

    # Send GET request to retrieve customer data
    result = requests.get(
        API_URL + "/getCustomerData",
        headers=headers,
        params={"includeBikeDetails": ""},
    )
    result.raise_for_status()

    # Parse JSON response
    result = result.json()
    return result

def extract_bike_details(result):
    # Extract bike details from response
    bike_details = result.get("data", {}).get("bikeDetails")
    if not bike_details or not isinstance(bike_details, list) or len(bike_details) == 0:
        logging.error(result)
        raise Exception("No bike details in response.")

    # Only get the first bike's details
    bike_info = bike_details[0]
    bike_type = bike_info.get("name")  # Get bike type
    encryption_key = bike_info.get("key", {}).get("encryptionKey")
    passcode = bike_info.get("key", {}).get("passcode")
    frame_number = bike_info.get("frameNumber")
    mac_address = bike_info.get("macAddress")

    # Check if all required data are present
    if not encryption_key or not passcode or not frame_number or not mac_address:
        logging.error(result)
        raise Exception("Missing data in response.")
        
    return bike_type, frame_number, mac_address, encryption_key, passcode

def save_to_file(result, bike_type, frame_number):
    # Generate the filename
    filename = f"VanMoof_{bike_type.replace(' ', '_')}_{frame_number}.json"
    file_path = os.path.expanduser(f"~/Downloads/{filename}")
    
    # Save the full output to a file in the user's Downloads directory
    with open(file_path, "w") as outfile:
        json.dump(result, outfile)
        
    return file_path

def query(username=None, password=None, json_file=None):
    API_URL = "https://my.vanmoof.com/api/v8"
    API_KEY = "fcb38d47-f14b-30cf-843b-26283f6a5819"

    if json_file:
        # Load data from a local JSON file if provided
        logging.info(f"Loading data from local file: {json_file}")
        with open(json_file, 'r') as file:
            result = json.load(file)
        file_path = json_file
    else:
        # Otherwise, fetch data from the API
        if username is None:
            username = input("Please enter your username: ")
        if password is None:
            password = getpass.getpass("Please enter your password: ")
        logging.info(f"Fetching data from API for user: {username}")
        token = authenticate(username, password, API_URL, API_KEY)
        result = get_customer_data(token, API_URL, API_KEY)
    
    # Extract the bike details from the data
    bike_type, frame_number, mac_address, encryption_key, passcode = extract_bike_details(result)

    # Save the data to a file only if it was fetched from the API
    if not json_file:
        file_path = save_to_file(result, bike_type, frame_number)

    return bike_type, frame_number, mac_address, encryption_key, passcode, file_path

if __name__ == "__main__":
    print()
    print("*********************************")
    print("      VanMoof Key Extractor     ")
    print("*********************************")
    print()
    
    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
        pass

    parser = argparse.ArgumentParser(description="Query the Vanmoof API or parse a local JSON file.\n\n"
                                                 "Examples:\n"
                                                 "1. To query the API:\n"
                                                 "   pymoof3.py -u username@example.com -p yourpassword\n"
                                                 "2. To parse a local JSON file:\n"
                                                 "   pymoof3.py -j /path/to/your/file.json\n",
                                     formatter_class=CustomFormatter)
    parser.add_argument('-u', '--username', help='The username to use for the API query. If not provided, a prompt will ask for it.')
    parser.add_argument('-p', '--password', help='The password to use for the API query. If not provided, a prompt will ask for it.')
    parser.add_argument('-j', '--json', help='A local JSON file to parse instead of querying the API.')
    args = parser.parse_args()

    if args.json:
        bike_type, frame_number, mac_address, encryption_key, passcode, file_path = query(json_file=args.json)
    else:
        if not args.username:
            args.username = input("Please enter your username: ")
        if not args.password:
            args.password = getpass.getpass("Please enter your password: ")
        bike_type, frame_number, mac_address, encryption_key, passcode, file_path = query(args.username, args.password)

    print()
    print(f"Bike Type: {bike_type}")
    print(f"Frame Number: {frame_number}")
    print(f"MAC Address: {mac_address}")
    print(f"Encryption Key: {encryption_key}")
    print(f"Passcode: {passcode}")
    print()
    
    if not args.json:
        print()
        print(f"A file with all the JSON data has been written to {file_path}")
        print()
