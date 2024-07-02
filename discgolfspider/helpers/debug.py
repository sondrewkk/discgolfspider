import datetime
import json
import os


def save_response(json_response, spider_name):
    if not os.path.exists("raw_data"):
        os.makedirs("raw_data")

    # Create a file name with spider name and current date and time
    file_name = f"raw_data/{spider_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

    # Dump the response as JSON
    with open(file_name, "w") as file:
        json.dump(json_response, file)
