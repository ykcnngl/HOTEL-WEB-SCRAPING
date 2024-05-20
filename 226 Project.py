import requests # Import requests module
from bs4 import BeautifulSoup   # Import BeautifulSoup module
import pandas as pd # Import pandas module
import tkinter as tk    # Import tkinter module
from tkinter import ttk, messagebox # Import ttk and messagebox modules from tkinter
from PIL import Image, ImageTk  # Import Image and ImageTk modules from PIL
from tkcalendar import DateEntry  # Import DateEntry from tkcalendar module
import csv  # Import CSV module for file operations



convert = 30  # 1 Euro = 30 TL

def scrape_hotels(city, checkin_date, checkout_date, adults, currency): # Scrape hotels from Booking.com
    mainurl = f"https://www.booking.com/searchresults.html?ss={city}&checkin={checkin_date}&checkout={checkout_date}&group_adults={adults}&no_rooms=1&group_children=0"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, likeGecko) Chrome/51.0.2704.64 Safari/537.36','Accept-Language': 'en-US, en;q=0.5'}
    response = requests.get(mainurl, headers=headers) # Send a GET request to the URL with headers
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML as a string
    hotels = soup.findAll('div', {'data-testid': 'property-card'})  # Find all hotels
    print(mainurl)
    hotels_data = []

    for hotel in hotels: # Extract information for each hotel
        name_element = hotel.find('div', {'data-testid': 'title'}) # Find the hotel title
        address_element = hotel.find('span', {'data-testid': 'address'}) # Find the hotel address
        distance_element = hotel.find('span', {'data-testid': 'distance'}) # Find the distance to city center
        rating_element = hotel.find('span', {'class': 'a3332d346a'}) # Find the hotel rating
        price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'}) # Find the hotel price

        name = name_element.text.strip() if name_element else "NOT GIVEN"
        address = address_element.text.strip() if address_element else "NOT GIVEN"
        distance = distance_element.text.strip() if distance_element else "NOT GIVEN"
        rating = rating_element.text.strip() if rating_element else "NOT GIVEN"
        price = price_element.text.strip() if price_element else "NOT GIVEN"
        print(name, address, distance, rating, price)

        if currency == "TL":  # Convert price to TL if currency is TL
            price_in_tl = round(float(
                price.replace('€', '').replace('TL', '').replace(' ', '').replace(',', '').replace('\u00a0', '')) / convert, 1)
            price = f"{price_in_tl:.2f} Euro"

        hotels_data.append({    # Append hotel information to the list
            'Hotel Title': name,
            'Address': address,
            'Distance to City Center': distance,
            'Rating': rating,
            'Price': price
        })
    print(hotels_data)

    # Sort hotels based on criteria (price)
    sorted_hotels = sorted(hotels_data, key=lambda x: float(x['Price'].replace('Euro', '').replace('TL', '').replace('\xa0', '').replace(',', '').strip()))

    # Save sorted hotels to a CSV file
    with open('myhotels.csv', 'w', newline='', encoding='utf-8') as csvfile: # Open a CSV file in write mode
        fieldnames = ['Hotel Title', 'Address', 'Distance to City Center', 'Rating', 'Price'] # Define field names
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames) # Create a CSV writer object
        writer.writeheader() # Write header to the CSV file
        writer.writerows(sorted_hotels[:5])  # Write top 5 hotels to the CSV file

    return sorted_hotels[:5]  # Return top 5 hotels


def update_price(isEuro=None): # Update the price based on the selected currency
    hotels = pd.read_csv('myhotels.csv')    # Read the hotels from the CSV file
    if hotels['Price'][1] == "NOT GIVEN": # If no hotels are found
        display_results() # Display the results
        return

    if isEuro.get() == 1:  # If Euro is selected
        if str(hotels['Price'][1]).startswith('Euro'): # If Euro is selected
            return
        hotels['Price'] = hotels['Price'].replace('TL', '', regex=True).replace(',', '', regex=True).replace(' ', '', regex=True).replace(' ', '', regex=True).astype(float) # Convert price to float
        hotels['Price'] = round(hotels['Price'] / 30, 1)    # Convert price to Euro
        hotels['Price'] = 'Euro ' + hotels['Price'].astype(str) # Add Euro to the price

        hotels.to_csv('myhotels.csv', index=False)  # Save the updated prices to a CSV file
        display_results()   # Display the results
    else:
        if str(hotels['Price'][1]).startswith('TL'): # If TL is selected
            return
        hotels['Price'] = hotels['Price'].replace('Euro ', '', regex=True).astype(float) # Convert price to float
        hotels['Price'] = round(hotels['Price'] * 30, 0)   # Convert price to TL
        hotels['Price'] = 'TL ' + hotels['Price'].astype(str)   # Add TL to the price

        hotels.to_csv('myhotels.csv', index=False) # Save the updated prices to a CSV file
        display_results()


def get_selected_currency(): # Get the selected currency from the radio buttons
    return "TL" if currency_var.get() == 1 else "EURO"


def search_hotels():  # Search for hotels based on user input
    city = city_combobox.get()      # Get the selected city from the combobox
    checkin_date = checkin_entry.get() # Get the check-in date from the DateEntry widget
    checkout_date = checkout_entry.get() # Get the check-out date from the DateEntry widget
    adults = adults_entry.get() # Get the number of adults from the entry widget
    currency = get_selected_currency() # Get the selected currency

    try:  # Try to scrape hotels and display the results
        hotels_list = scrape_hotels(city, checkin_date, checkout_date, adults, currency)
        display_results(hotels_list)
        update_background(city)  # Update the background image based on the selected city
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def display_results(hotels_list):  # Display the results in the text box
    result_text.delete('1.0', tk.END) # Clear the text box
    for hotel in hotels_list:
        result_text.insert(tk.END, f"Hotel Title: {hotel['Hotel Title']}\n" # Insert hotel information to the text box
                                   f"Address: {hotel['Address']}\n"  
                                   f"Distance to City Center: {hotel['Distance to City Center']}\n"
                                   f"Rating: {hotel['Rating']}\n"
                                   f"Price: {hotel['Price']}\n\n")


def update_background(city):
    # Load and place the background image based on the selected city
    background_image_path = city_backgrounds.get(city, "a.jpg")  # Get the background image path based on the selected city
    original_image = Image.open(background_image_path)  # Open the background image
    resized_image = original_image.resize((1600, 900)) # Resize the image
    image = ImageTk.PhotoImage(resized_image) # Create an ImageTk object
    canvas.create_image(0, 0, image=image, anchor="nw") # Place the image on the canvas
    # Keep a reference to the image to prevent it from being garbage collected
    canvas.image = image

# Dictionary to map cities to background image paths
city_backgrounds = {
    "Edinburgh": "Edinburgh.jpg",
    "London": "London.jpg",
    "Münich": "Münich.jpg",
    "Rome": "Rome.jpg",
    "Madrid": "Madrid.jpg",
    "Vienna": "Vienna.jpg",
    "Amsterdam": "Amsterdam.jpg",
    "Brussels": "Brussels.jpg",
    "Prague": "Prague.jpg",
    "Athens": "Athens.jpg"
}

# Create main window
window = tk.Tk()
window.title("Hotel Search")
window.geometry("1600x900+50+50")
window.attributes('-alpha', 1)  # Set transparency for the window

# Create a Canvas for the background image
canvas = tk.Canvas(window, width=1200, height=800) # Create a canvas with a specific width and height
canvas.pack(fill="both", expand=True)   # Fill the entire window with the canvas

# Load and place the background image on the canvas
original_image = Image.open("a.jpg")
resized_image = original_image.resize((1600, 900))
image = ImageTk.PhotoImage(resized_image)
canvas.create_image(0, 0, image=image, anchor="nw") # Place the image on the canvas

# Create GUI elements within the main window with transparent background
label_bg = 'lightblue'

tk.Label(window, text="Select a City:", bg=label_bg).place(x=10, y=10)
cities = ["Edinburgh", "London", "Münich", "Rome", "Madrid", "Vienna", "Amsterdam", "Brussels", "Prague", "Athens"]
city_combobox = ttk.Combobox(window, values=cities)
city_combobox.place(x=150, y=10)

# Set default date
tk.Label(window, text="Check-in Date:", bg=label_bg).place(x=10, y=40)
checkin_entry = DateEntry(window, date_pattern='yyyy-mm-dd')  # Use DateEntry widget for check-in date
checkin_entry.set_date("2024-05-25")  # Set default date
checkin_entry.place(x=150, y=40)

# Set default date
tk.Label(window, text="Check-out Date:", bg=label_bg).place(x=10, y=70)
checkout_entry = DateEntry(window, date_pattern='yyyy-mm-dd')  # Use DateEntry widget for check-out date
checkout_entry.set_date("2024-05-30")  # Set default date
checkout_entry.place(x=150, y=70)

tk.Label(window, text="Number of Adults:", bg=label_bg).place(x=10, y=100)
adults_entry = tk.Entry(window)
adults_entry.insert(0, "2")
adults_entry.place(x=150, y=100)

currency_var = tk.IntVar()
tk.Radiobutton(window, text="TL", variable=currency_var, value=0, bg=label_bg).place(x=10, y=130) # Create radio buttons for currency selection
tk.Radiobutton(window, text="Euro", variable=currency_var, value=1, bg=label_bg).place(x=60, y=130) # Create radio buttons for currency selection

search_button = tk.Button(window, text="Search Hotels",fg = 'black', bg='lightblue', command=search_hotels)     # Create a search button
search_button.place(x=10, y=160)

result_text = tk.Text(window, height=15, width=80, bg='lightblue')  # Create a text box to display the results
result_text.place(x=10, y=650)

window.mainloop()
