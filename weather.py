import requests
import random
import datetime

API_KEY = "weatherapi_api_key"  # # Secure code best practices!!
LOCATION = "my_location" 

def get_weather(api_key=API_KEY, location=LOCATION):
    """Fetches weather data from WeatherAPI."""
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['current']['temp_c'], data['current']['condition']['text']
    else:
        print("Error fetching weather data.")
        return None, None

def suggest_outfit(temp, condition):
    """Suggests an outfit based on temperature and weather condition."""
    if temp < 15:
        return "Dress warm with a coat, hat, scarf, and gloves."
    elif temp < 45:
        return "Throw on a jacket or sweater!"
    else:
        return "Enjoy the sunshine! Bless them with the drip and shades."

def get_traditional_outfit(temperature, day_of_week):
    """Suggests a traditional outfit based on temperature and day of the week."""
    if temperature > 80:
        print("WARNING: It's hot outside. Stay hydrated.")
        return "Wear some loose-fitting and lightweight clothes"

    traditional_outfits = {  # Diversified outfits
        "Monday": ["Korean: Hanbok", "Mexican: Guayabera", "Vietnamese: Áo dài"],
        "Tuesday": ["Thai: Chut Thai", "Indonesian: Batik", "Peruvian: Poncho"],
        "Wednesday": ["Moroccan: Djellaba", "Egyptian: Galabeya", "Turkish: Shalwar Kameez"],
        "Thursday": ["Greek: Chiton", "Roman: Toga", "Celtic: Léine"],
        "Friday": ["Indian: Sherwani, Kurta Pyjama", "Nigerian: Dashiki, Buba", "Arab: Thobe"],
        "Saturday": ["Scottish: Kilt", "Japanese: Kimono, Yukata", "Chinese: Hanfu"],
        "Sunday": ["Nigerian: Agbada", "Ghanaian: Kaftan", "Indian: Kurta"]
    }

    return random.choice(traditional_outfits.get(day_of_week, []))

def main():
    """Automates the outfit suggestion process."""
    current_day = datetime.datetime.now().strftime("%A")
    temp, condition = get_weather()
    
    if temp is not None:  
        print(f"\nToday is {current_day}, and the weather is {temp}°C and {condition}.")
        
        if current_day.capitalize() in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            traditional_outfit = get_traditional_outfit(temp, current_day.capitalize())
            print(f"Suggested traditional outfit: {traditional_outfit}")

        outfit = suggest_outfit(temp, condition)
        print(f"General outfit suggestion: {outfit}")


if __name__ == "__main__":
    main()