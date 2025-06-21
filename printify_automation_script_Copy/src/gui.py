import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from utils import add_record, load_data, save_data, modify_record, delete_record, load_config
from upload import upload_products
import threading
import requests

config = load_config()
access_token = config["access_token"]
shop_id = config["shop_id"]
base_url = "https://api.printify.com/v1"

def fetch_provider_info_from_api(provider_id):
    providers_url = f"{base_url}/catalog/print_providers/{provider_id}.json"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(providers_url, headers=headers)
    if response.status_code == 200:
        provider_info = response.json()
        country = provider_info.get("location", {}).get("country", "Unknown")
        cost = sorted(set(variant.get("price") for variant in provider_info.get("products", [])))
        return {"country": country, "cost": cost}
    return {"country": "Unknown", "cost": []}

def update_provider_info(provider):
    if "id" in provider:
        provider_info = fetch_provider_info_from_api(provider["id"])
        if provider_info:
            provider.update(provider_info)
            modify_record(provider)

def load_providers():
    providers = load_data()
    for provider in providers:
        if "country" not in provider or "cost" not in provider or not provider["country"] or not provider["cost"]:
            update_provider_info(provider)
    save_data(providers)
    return providers

def start_application():
    root = tk.Tk()
    root.title("Printify Product Manager")
    root.geometry("800x600")

    progress_label = tk.Label(root, text="")
    progress_label.pack()
    progress_bar = ttk.Progressbar(root, mode='determinate')
    progress_bar.pack(fill=tk.X, padx=10, pady=5)

    def fetch_providers(blueprint_id):
        providers_url = f"{base_url}/catalog/blueprints/{blueprint_id}/print_providers.json"
        response = requests.get(providers_url, headers={"Authorization": f"Bearer {access_token}"})
        if response.status_code == 200:
            provider_list = response.json()
            for provider in provider_list:
                if "country" not in provider or "cost" not in provider:
                    provider_info = fetch_provider_info_from_api(provider["id"])
                    provider.update(provider_info)
            return provider_list
        messagebox.showerror("Error", f"Failed to fetch providers: {response.text}")
        return []

    def add_products():
        def select_providers(product_links, all_providers):
            select_provider_window = tk.Toplevel(root)
            select_provider_window.title("Select Providers")
            select_provider_window.geometry("600x400")

            frame = tk.Frame(select_provider_window)
            frame.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(frame)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            provider_vars = []

            def save_products():
                for product_link, provider_var, providers in zip(product_links, provider_vars, all_providers):
                    provider_choice = provider_var.get()
                    print_provider = next((p for p in providers if f"{p['title']} ({p['country']} - ${', $'.join(map(str, p['cost']))})" == provider_choice), None)
                    if not print_provider:
                        messagebox.showerror("Error", "Invalid print provider selected.")
                        return
                    blueprint_id = int(product_link.split("/")[-3])
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

            def fetch_providers_thread(product_links):
                all_providers = []
                progress_bar["maximum"] = len(product_links)
                for idx, product_link in enumerate(product_links):
                    blueprint_id = int(product_link.split("/")[-3])
                    available_providers = fetch_providers(blueprint_id)
                    all_providers.append(available_providers)
                    if not available_providers:
                        continue
                    tk.Label(scrollable_frame, text=f"{product_link}").pack(anchor=tk.W)
                    provider_options = [f"{p['title']} ({p['country']} - ${', $'.join(map(str, p['cost']))})" for p in available_providers]
                    provider_var = tk.StringVar()
                    provider_menu = ttk.Combobox(scrollable_frame, textvariable=provider_var, values=provider_options)
                    provider_menu.pack(fill=tk.X, padx=5, pady=2)
                    provider_vars.append(provider_var)
                    progress_bar["value"] = idx + 1
                    progress_label.config(text=f"Fetching providers for {idx + 1}/{len(product_links)} products")
                    select_provider_window.update_idletasks()
                tk.Button(select_provider_window, text="Save", command=save_products).pack(pady=10)

            threading.Thread(target=fetch_providers_thread, args=(product_links,)).start()

        def submit_product_links():
            product_links = text_product_links.get("1.0", tk.END).strip().split("\n")
            for product_link in product_links:
                blueprint_id = int(product_link.split("/")[-3])
                providers = fetch_providers(blueprint_id)
                if len(providers) == 1:
                    record = {
                        "blueprint_id": blueprint_id,
                        "provider": {
                            "id": providers[0]['id'],
                            "title": providers[0]['title'],
                            "country": providers[0]['country'],
                            "cost": providers[0]['cost']
                        }
                    }
                    add_record(record)
                else:
                    select_providers([product_link], [providers])
            update_product_list()
            add_product_window.destroy()

        add_product_window = tk.Toplevel(root)
        add_product_window.title("Add Products")
        add_product_window.geometry("600x400")
        tk.Label(add_product_window, text="Product Links (one per line):").pack()
        text_product_links = tk.Text(add_product_window, width=80, height=15)
        text_product_links.pack()
        tk.Button(add_product_window, text="Next", command=submit_product_links).pack(pady=10)

    def manage_products():
        def delete_selected_product():
            selected_index = listbox_products.curselection()
            if selected_index:
                data = load_data()
                data.pop(selected_index[0])
                save_data(data)
                update_product_list()

        def delete_all_providers():
            save_data([])
            update_product_list()

        def edit_selected_product():
            selected_index = listbox_products.curselection()
            if not selected_index:
                return
            selected_product = load_data()[selected_index[0]]

            def save_changes():
                product_link = entry_product_link.get()
                blueprint_id = int(product_link.split("/")[-3])
                provider_choice = provider_var.get()
                print_provider = next((p for p in providers if f"{p['title']} ({p['country']} - ${', $'.join(map(str, p['cost']))})" == provider_choice), None)
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
                data[selected_index[0]] = updated_record
                save_data(data)
                update_product_list()
                edit_product_window.destroy()

            edit_product_window = tk.Toplevel(root)
            edit_product_window.title("Edit Product")
            edit_product_window.geometry("400x200")
            tk.Label(edit_product_window, text="Product Link:").pack()
            entry_product_link = tk.Entry(edit_product_window, width=50)
            entry_product_link.pack()
            entry_product_link.insert(0, selected_product['blueprint_id'])
            tk.Label(edit_product_window, text="Provider:").pack()
            provider_var = tk.StringVar(edit_product_window)
            provider_var.set(selected_product['provider']['title'])
            providers = fetch_providers(selected_product['blueprint_id'])
            provider_menu = ttk.Combobox(edit_product_window, textvariable=provider_var, values=[f"{p['title']} ({p['country']} - ${', $'.join(map(str, p['cost']))})" for p in providers])
            provider_menu.pack()
            tk.Button(edit_product_window, text="Save", command=save_changes).pack()

        manage_window = tk.Toplevel(root)
        manage_window.title("Manage Products")
        manage_window.geometry("600x400")
        listbox_products = tk.Listbox(manage_window, width=80, height=20)
        listbox_products.pack()
        update_product_list()
        tk.Button(manage_window, text="Edit", command=edit_selected_product).pack()
        tk.Button(manage_window, text="Delete", command=delete_selected_product).pack()
        tk.Button(manage_window, text="Delete All", command=delete_all_providers).pack()

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

        def update_progress(value):
            progress_bar['value'] = value
            progress_label.config(text=f"Uploading: {value:.2f}%")
            root.update_idletasks()

        def upload_thread():
            try:
                error_summary = upload_products(products_to_upload, image_directory, progress_callback=update_progress)
                progress_label.config(text="Upload complete.")
                if error_summary:
                    error_message = "\n".join(error_summary)
                    messagebox.showwarning("Upload Completed with Warnings", 
                        f"The upload process completed, but some images were skipped due to size limitations or other issues. "
                        f"Please check the log file at 'printify_upload.log' for details.\n\n"
                        f"Summary of skipped images:\n{error_message}")
                else:
                    messagebox.showinfo("Success", "Upload process completed successfully without any errors.")
            except Exception as e:
                progress_label.config(text="Upload failed.")
                messagebox.showerror("Error", f"An unexpected error occurred during the upload process: {str(e)}")
            finally:
                progress_bar['value'] = 0
                root.update_idletasks()

        threading.Thread(target=upload_thread).start()
        progress_label.config(text="Uploading products...")

    show_na_only = tk.BooleanVar()
    tk.Checkbutton(root, text="Show only providers from North America", variable=show_na_only).pack(anchor=tk.W)
    tk.Button(root, text="Add Products", command=add_products).pack()
    tk.Button(root, text="Manage Products", command=manage_products).pack()
    tk.Label(root, text="Select products to upload:").pack()
    listbox_products = tk.Listbox(root, selectmode=tk.MULTIPLE, width=80, height=20)
    listbox_products.pack()
    
    def update_product_list():
        listbox_products.delete(0, tk.END)
        for record in load_providers():
            listbox_products.insert(tk.END, f"{record['blueprint_id']} - {record['provider']['title']} ({record['provider'].get('country', 'Unknown')} - ${', $'.join(map(str, record['provider'].get('cost', [])))})")

    update_product_list()
    tk.Button(root, text="Upload Selected Products", command=upload_selected_products).pack()
    root.mainloop()

if __name__ == "__main__":
    start_application()