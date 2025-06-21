import requests
import pandas as pd
import base64
import os

# Set your API credentials
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6Ijc1YzAyMWMyMjZhZjFhOTMyNTE2MjlmYmVjZTQ3ZDQxMDVjOTI5ZjgwMzRlN2M4MWIyODE5YTAzNTM5ZGYzZmJiMjFlYzA5MjZiYzg4NDkwIiwiaWF0IjoxNzExOTA5MTQwLjU2OTM2NiwibmJmIjoxNzExOTA5MTQwLjU2OTM2OCwiZXhwIjoxNzQzNDQ1MTQwLjU2NDM1Miwic3ViIjoiODgzNzA3NiIsInNjb3BlcyI6WyJzaG9wcy5tYW5hZ2UiLCJzaG9wcy5yZWFkIiwiY2F0YWxvZy5yZWFkIiwib3JkZXJzLnJlYWQiLCJvcmRlcnMud3JpdGUiLCJwcm9kdWN0cy5yZWFkIiwicHJvZHVjdHMud3JpdGUiLCJ3ZWJob29rcy5yZWFkIiwid2ViaG9va3Mud3JpdGUiLCJ1cGxvYWRzLnJlYWQiLCJ1cGxvYWRzLndyaXRlIiwicHJpbnRfcHJvdmlkZXJzLnJlYWQiXX0.AEjAnmVK4JobSu1MFlJ3j3RHw_uUNay7zqbd7FjQ0XV8sgjpBDjjcXzUK3Jszny6Wczj4xcFKzp2znAp4GY"
shop_id = "4884445"

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
        "blueprint_id": 485,  # Replace with the actual blueprint ID
        "print_provider_id": 28,
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
                                "scale": 1.0,
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
