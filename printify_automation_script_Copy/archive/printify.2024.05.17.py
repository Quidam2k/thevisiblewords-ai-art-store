import requests
import base64
import os
from PIL import Image
import logging
from utils import add_record, load_data, manage_records

# Set up logging
logging.basicConfig(filename='product_creation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set your API credentials
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6Ijc1YzAyMWMyMjZhZjFhOTMyNTE2MjlmYmVjZTQ3ZDQxMDVjOTI5ZjgwMzRlN2M4MWIyODE5YTAzNTM5ZGYzZmJiMjFlYzA5MjZiYzg4NDkwIiwiaWF0IjoxNzExOTA5MTQwLjU2OTM2NiwibmJmIjoxNzExOTA5MTQwLjU2OTM2OCwiZXhwIjoxNzQzNDQ1MTQwLjU2NDM1Miwic3ViIjoiODgzNzA3NiIsInNjb3BlcyI6WyJzaG9wcy5tYW5hZ2UiLCJzaG9wcy5yZWFkIiwiY2F0YWxvZy5yZWFkIiwib3JkZXJzLnJlYWQiLCJvcmRlcnMud3JpdGUiLCJwcm9kdWN0cy5yZWFkIiwicHJvZHVjdHMud3JpdGUiLCJ3ZWJob29rcy5yZWFkIiwid2ViaG9va3Mud3JpdGUiLCJ1cGxvYWRzLnJlYWQiLCJ1cGxvYWRzLndyaXRlIiwicHJpbnRfcHJvdmlkZXJzLnJlYWQiXX0.AEjAnmVK4JobSu1MFlJ3j3RHw_uUNay7zqbd7FjQ0XV8sgjpBDjjcXzUK3Jszny6Wczj4xcFKzp2znAp4GY"
shop_id = "4884445"

# Set the URL for the API endpoints
base_url = "https://api.printify.com/v1"
upload_url = f"{base_url}/uploads/images.json"
product_url = f"{base_url}/shops/{shop_id}/products.json"

def main():
    print("Choose an option:")
    print("1. Manage saved products")
    print("2. Proceed with uploading products")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        manage_records()
    elif choice == '2':
        proceed_with_uploading()
    else:
        print("Invalid choice. Please try again.")
        main()

def proceed_with_uploading():
    # Load the CSV file
    csv_path = "product_information.csv"
    image_df = pd.read_csv(csv_path)

    # Set headers for requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Get the product link from the user
    product_link = input("Enter the product link from the Printify catalog: ")

    # Extract the blueprint ID from the product link
    blueprint_id = int(product_link.split("/")[-3])

    # Get the list of print providers for the given blueprint
    providers_url = f"{base_url}/catalog/blueprints/{blueprint_id}/print_providers.json"
    response = requests.get(providers_url, headers=headers)
    providers = response.json()

    print("Print Providers for the selected product:")
    for idx, provider in enumerate(providers, start=1):
        print(f"{idx}. {provider['title']}")

    # Ask the user to select a print provider
    while True:
        try:
            provider_choice = int(input("Enter the number of the print provider you want to use: "))
            if 1 <= provider_choice <= len(providers):
                print_provider = providers[provider_choice - 1]
                print_provider_id = print_provider['id']
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # Save the selected product and provider details
    record = {
        "blueprint_id": blueprint_id,
        "provider": {
            "id": print_provider_id,
            "title": print_provider['title']
        }
    }
    add_record(record)

    # Get the variant IDs for the selected blueprint and print provider
    variants_url = f"{base_url}/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json"
    response = requests.get(variants_url, headers=headers)

    if response.status_code == 200:
        try:
            json_response = response.json()
            variants = json_response.get('variants', [])  # Safely access the 'variants' key
            if not variants:
                raise ValueError("No variants found in the response.")
        except json.JSONDecodeError:
            logging.error(f"Failed to parse JSON from response. Status Code: {response.status_code}, Response Text: {response.text}")
            raise
        except ValueError as e:
            logging.error(f"Error with variants data: {e}")
            raise
    else:
        logging.error(f"API request failed with status code {response.status_code}: {response.text}")
        raise Exception(f"API request failed with status code {response.status_code}")

    for idx, row in image_df.iterrows():
        with Image.open(row['local_path']) as img:
            img_width, img_height = img.size

        # Convert the image to Base64
        with open(row['local_path'], "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode('utf-8')

        # Upload the image to the Printify media library
        data = {
            "file_name": row['file_name'],
            "contents": img_b64
        }
        response = requests.post(upload_url, headers=headers, json=data)
        
        if response.status_code >= 200 and response.status_code < 300:
            image_id = response.json()["id"]
            preview_url = response.json()["preview_url"]
        else:
            logging.error(f"Failed to upload image for product {idx+1}. Server responded with: {response.text}")
            continue

        # Create the product with the uploaded image
        data = {
            "title": row['title'],
            "description": row['description'] + f"\n\nFull artwork:\n<img src='{preview_url}' alt='Full Artwork'>",
            "tags": row['tags'].split(', '),
            "blueprint_id": blueprint_id,
            "print_provider_id": print_provider_id,
            "variants": [],
            "print_areas": []
        }

        for variant in variants:
            variant_id = variant["id"]
            for placeholder in variant['placeholders']:
                if placeholder['position'] == 'front':  # Example: Assuming you want 'front'
                    variant_width = placeholder['width']
                    variant_height = placeholder['height']

                    if img_width > img_height:
                        scale = variant_height / img_height * img_width / variant_width
                    else:
                        scale = 1.0

                    data["variants"].append({
                        "id": variant_id,
                        "price": 1499,
                        "is_enabled": True
                    })

                    data["print_areas"].append({
                        "variant_ids": [variant_id],
                        "placeholders": [
                            {
                                "position": "front",
                                "images": [
                                    {
                                        "id": image_id,
                                        "x": 0.5,
                                        "y": 0.5,
                                        "scale": scale,
                                        "angle": 0
                                    }
                                ]
                            }
                        ]
                    })
                    break  # Assuming only one 'front' placeholder is needed per variant

        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            response = requests.post(product_url, headers=headers, json=data)
            if response.status_code >= 200 and response.status_code < 300:
                logging.info(f"Product {idx+1} created successfully!")
                break
            else:
                retry_count += 1
                logging.warning(f"Failed to create product {idx+1}. Retrying ({retry_count}/{max_retries})...")
        else:
            logging.error(f"Failed to create product {idx+1} after {max_retries} retries. Server responded with: {response.text}")

if __name__ == "__main__":
    main()
