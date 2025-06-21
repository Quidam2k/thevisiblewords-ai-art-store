import tkinter as tk
from tkinter import filedialog, messagebox
from utils import add_record, load_data, save_data, modify_record, delete_record
import os
from PIL import Image, ExifTags
import requests
import base64
import logging

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

def extract_prompt_from_image(image_path):
    with Image.open(image_path) as img:
        exif_data = img._getexif()
        if not exif_data:
            return "No prompt found"
        for tag, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag, tag)
            if tag_name == 'ImageDescription':
                return value
    return "No prompt found"

def upload_products(selected_products, image_directory):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    for record in selected_products:
        blueprint_id = record['blueprint_id']
        print_provider_id = record['provider']['id']

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

        for image_file in os.listdir(image_directory):
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(image_directory, image_file)
                prompt = extract_prompt_from_image(image_path)
                title = prompt.split('.')[0]
                description = prompt

                with Image.open(image_path) as img:
                    img_width, img_height = img.size

                # Convert the image to Base64
                with open(image_path, "rb") as img_file:
                    img_b64 = base64.b64encode(img_file.read()).decode('utf-8')

                # Upload the image to the Printify media library
                data = {
                    "file_name": os.path.basename(image_path),
                    "contents": img_b64
                }
                response = requests.post(upload_url, headers=headers, json=data)
                
                if response.status_code >= 200 and response.status_code < 300:
                    image_id = response.json()["id"]
                    preview_url = response.json()["preview_url"]
                else:
                    logging.error(f"Failed to upload image. Server responded with: {response.text}")
                    continue

                # Create the product with the uploaded image
                data = {
                    "title": title,
                    "description": description + f"\n\nFull artwork:\n<img src='{preview_url}' alt='Full Artwork'>",
                    "tags": [],  # Tags will be added later
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
                        logging.info("Product created successfully!")
                        break
                    else:
                        retry_count += 1
                        logging.warning(f"Failed to create product. Retrying ({retry_count}/{max_retries})...")
                else:
                    logging.error(f"Failed to create product after {max_retries} retries. Server responded with: {response.text}")

def main():
    root = tk.Tk()
    root.title("Printify Product Manager")
    root.geometry("800x600")  # Increase the window size

    def add_product():
        def fetch_providers(blueprint_id):
            providers_url = f"{base_url}/catalog/blueprints/{blueprint_id}/print_providers.json"
            response = requests.get(providers_url, headers={"Authorization": f"Bearer {access_token}"})
            if response.status_code == 200:
                return response.json()
            else:
                messagebox.showerror("Error", f"Failed to fetch providers: {response.text}")
                return []

        def select_provider(providers, blueprint_id):
            def save_product():
                provider_choice = provider_var.get()
                print_provider = next((p for p in providers if p['title'] == provider_choice), None)
                if not print_provider:
                    messagebox.showerror("Error", "Invalid print provider selected.")
                    return

                record = {
                    "blueprint_id": blueprint_id,
                    "provider": {
                        "id": print_provider['id'],
                        "title": print_provider['title']
                    }
                }
                add_record(record)
                update_product_list()
                select_provider_window.destroy()

            select_provider_window = tk.Toplevel(root)
            select_provider_window.title("Select Provider")
            select_provider_window.geometry("400x200")

            tk.Label(select_provider_window, text="Provider:").pack()
            provider_var = tk.StringVar(select_provider_window)
            provider_var.set(providers[0]['title'])  # set default provider

            provider_menu = tk.OptionMenu(select_provider_window, provider_var, *[p['title'] for p in providers])
            provider_menu.pack()

            tk.Button(select_provider_window, text="Save", command=save_product).pack()

        def fetch_blueprint_id(product_link):
            try:
                blueprint_id = int(product_link.split("/")[-3])
                providers = fetch_providers(blueprint_id)
                if providers:
                    select_provider(providers, blueprint_id)
            except (IndexError, ValueError):
                messagebox.showerror("Error", "Invalid product link format.")
        
        def submit_product_link():
            product_link = entry_product_link.get()
            fetch_blueprint_id(product_link)
            add_product_window.destroy()

        add_product_window = tk.Toplevel(root)
        add_product_window.title("Add Product")
        add_product_window.geometry("400x200")

        tk.Label(add_product_window, text="Product Link:").pack()
        entry_product_link = tk.Entry(add_product_window, width=50)
        entry_product_link.pack()

        tk.Button(add_product_window, text="Next", command=submit_product_link).pack()

    def manage_products():
        def delete_selected_product():
            selected_index = listbox_products.curselection()
            if selected_index:
                data = load_data()
                data.pop(selected_index[0])
                save_data(data)
                update_product_list()

        def edit_selected_product():
            selected_index = listbox_products.curselection()
            if not selected_index:
                return
            selected_product = listbox_products.get(selected_index)
            selected_index = selected_index[0]

            edit_product_window = tk.Toplevel(root)
            edit_product_window.title("Edit Product")
            edit_product_window.geometry("400x200")

            tk.Label(edit_product_window, text="Product Link:").pack()
            entry_product_link = tk.Entry(edit_product_window, width=50)
            entry_product_link.pack()
            entry_product_link.insert(0, selected_product['blueprint_id'])

            tk.Label(edit_product_window, text="Provider:").pack()
            provider_var = tk.StringVar(edit_product_window)
            provider_var.set(selected_product['provider']['title'])  # set current provider

            provider_menu = tk.OptionMenu(edit_product_window, provider_var, *[p['title'] for p in providers])
            provider_menu.pack()

            def save_changes():
                product_link = entry_product_link.get()
                blueprint_id = int(product_link.split("/")[-3])

                provider_choice = provider_var.get()
                print_provider = next((p for p in providers if p['title'] == provider_choice), None)
                if not print_provider:
                    messagebox.showerror("Error", "Invalid print provider selected.")
                    return

                updated_record = {
                    "blueprint_id": blueprint_id,
                    "provider": {
                        "id": print_provider['id'],
                        "title": print_provider['title']
                    }
                }
                data = load_data()
                data[selected_index] = updated_record
                save_data(data)
                update_product_list()
                edit_product_window.destroy()

            tk.Button(edit_product_window, text="Save", command=save_changes).pack()

        manage_window = tk.Toplevel(root)
        manage_window.title("Manage Products")
        manage_window.geometry("600x400")

        listbox_products = tk.Listbox(manage_window, width=80, height=20)
        listbox_products.pack()

        update_product_list = lambda: [listbox_products.insert(tk.END, record) for record in load_data()]
        update_product_list()

        tk.Button(manage_window, text="Edit", command=edit_selected_product).pack()
        tk.Button(manage_window, text="Delete", command=delete_selected_product).pack()

    def upload_selected_products():
        selected_products = listbox_products.curselection()
        if not selected_products:
            messagebox.showerror("Error", "No products selected.")
            return

        image_directory = filedialog.askdirectory()
        if not image_directory:
            messagebox.showerror("Error", "No image directory selected.")
            return

        products_to_upload = [load_data()[i] for i in selected_products]
        upload_products(products_to_upload, image_directory)

    tk.Button(root, text="Add Product", command=add_product).pack()
    tk.Button(root, text="Manage Products", command=manage_products).pack()

    tk.Label(root, text="Select products to upload:").pack()
    listbox_products = tk.Listbox(root, selectmode=tk.MULTIPLE, width=80, height=20)
    listbox_products.pack()
    update_product_list = lambda: [listbox_products.insert(tk.END, record) for record in load_data()]
    update_product_list()

    tk.Button(root, text="Upload Selected Products", command=upload_selected_products).pack()

    root.mainloop()

if __name__ == "__main__":
    main()
