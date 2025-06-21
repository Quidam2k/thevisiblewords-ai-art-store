import requests
import pandas as pd
import base64
import os
from PIL import Image  # Import the Python Imaging Library

# Set your API credentials
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6Ijc1YzAyMWMyMjZhZjFhOTMyNTE2MjlmYmVjZTQ3ZDQxMDVjOTI5ZjgwMzRlN2M4MWIyODE5YTAzNTM5ZGYzZmJiMjFlYzA5MjZiYzg4NDkwIiwiaWF0IjoxNzExOTA5MTQwLjU2OTM2NiwibmJmIjoxNzExOTA5MTQwLjU2OTM2OCwiZXhwIjoxNzQzNDQ1MTQwLjU2NDM1Miwic3ViIjoiODgzNzA3NiIsInNjb3BlcyI6WyJzaG9wcy5tYW5hZ2UiLCJzaG9wcy5yZWFkIiwiY2F0YWxvZy5yZWFkIiwib3JkZXJzLnJlYWQiLCJvcmRlcnMud3JpdGUiLCJwcm9kdWN0cy5yZWFkIiwicHJvZHVjdHMud3JpdGUiLCJ3ZWJob29rcy5yZWFkIiwid2ViaG9va3Mud3JpdGUiLCJ1cGxvYWRzLnJlYWQiLCJ1cGxvYWRzLndyaXRlIiwicHJpbnRfcHJvdmlkZXJzLnJlYWQiXX0.AEjAnmVK4JobSu1MFlJ3j3RHw_uUNay7zqbd7FjQ0XV8sgjpBDjjcXzUK3Jszny6Wczj4xcFKzp2znAp4GY"
# doesn't change from product to product
shop_id = "4884445"


target_pixels_width = 4065  # THESE CHANGE FOR DIFFERENT PRODUCTS
target_pixels_height = 2850
blueprint_id = 976
print_provider_id = 92

# NEED TO USE THIS SOMEHOW TO GENERATE AN ARRAY OF VARIANT IDS
# GET /v1/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json


# Set the URL for the API endpoints
base_url = "https://api.printify.com/v1"
upload_url = f"{base_url}/uploads/images.json"
product_url = f"{base_url}/shops/{shop_id}/products.json"

# Load the CSV file
csv_path = "product_information.csv"  # Update this to your CSV file path
image_df = pd.read_csv(csv_path)

# Set headers for requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

for idx, row in image_df.iterrows():

    with Image.open(row['local_path']) as img:
        img_width, img_height = img.size
        img_aspect = img_width / img_height
        target_aspect = target_pixels_width / target_pixels_height


        print(f"Image dimensions: {img_width}x{img_height}")  # Debug print
        print(f"Image aspect ratio: {img_aspect}, Target aspect ratio: {target_aspect}")  # Debug print

        # THE SCALING CODE THAT CAME WITH THE SCRIPT BUT WHICH DOESN'T SEEM TO WORK
        if img_aspect > target_aspect:
            # Image is wider than target; scale based on height to fill vertically
            scale = target_pixels_height / img_height
        else:
            # Image is taller than target; scale based on width to fill horizontally
            scale = target_pixels_width / img_width
            
        # THE SCALING CODE GIVEN TO ME BY THE PRINTIFY API SUPPORT TEAM AND WHICH APPEARS TO HAVE ISSUES OF ITS OWN
        # supposedly this works: placeholder height/image height * image width/placeholder width
        scale = target_pixels_height / img_height * img_width / target_pixels_width

        print(f"Image scaled at: {scale}")  # Debug print

    # Convert the image to Base64
    with open(row['local_path'], "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode('utf-8')


    # Upload the image to the Printify media library
    data = {
        "file_name": row['file_name'],
        "contents": img_b64
    }
    response = requests.post(upload_url, headers=headers, json=data)
    image_id = response.json()["id"]

    # Create the product with the uploaded image
    data = {
        "title": row['title'],
        "description": row['description'],
        "tags": row['tags'].split(', '),  # Assuming tags are comma-separated in the CSV
        "blueprint_id": blueprint_id,  # Replace with the actual blueprint ID
        "print_provider_id": print_provider_id,
        
        # HERE WE NEED TO IMPLEMENT ITERATING THROUGH THE ARRAY OF VARIANT IDS TO GENERATE ALL THE VARIANTS
        
        "variants": [
            {
                "id": 65223,  # Replace with the actual variant ID
                "price": 1499,
                "is_enabled": True
            }
        ],
        "print_areas": [
            {
                "variant_ids": [65223],  # Replace with the actual variant ID
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_id,
                                "x": 0.5,
                                "y": 0.5,
                                "scale": scale,  # Set the scale based on earlier calculation
                                "angle": 0
                            }
                        ]
                    }
                ]
            }
        ]
    }
    response = requests.post(product_url, headers=headers, json=data)
    if response.status_code >= 200 and response.status_code < 300:
        print(f"Product {idx+1} created successfully!")
    else:
        print(f"Failed to create product {idx+1}. Server responded with: {response.text}")
