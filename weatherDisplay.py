import requests
from liquidcrystal_i2c import LCD
import pyowm
import time
import subprocess
import threading
key = ""
lcd = LCD(bus=1, addr= 39, cols= 16, rows=2)
cityname = None
lock = threading.Lock()

def getIp(): #fetch IP address of network that the pi is connected to
    response = requests.get("https://api64.ipify.org?format=json").json()
    return response["ip"]



def getLocation():
    ip_address = getIp()#with the given IP address from getIP() this fetch the location of device based on the network's local location.
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json() #will return in json format information about our location
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "county": response.get("region")
    }
    return location_data




def get_weather(): #responsible for calling the API for weather information
    global cityname
    while True:
        try:
            with lock:
                if cityname is None:
                    location_info = getLocation()
                    cityname = str(location_info["city"])#fetches the "city" value from the json format data retrun by getLocation() function
                owm = pyowm.OWM(key)
                loc = owm.weather_manager().weather_at_place(cityname)
                weather = loc.weather
                temp = weather.temperature(unit='fahrenheit')
                status = weather.detailed_status
                cleaned_temp_data = (int(temp['temp']))
            temper = str(cleaned_temp_data)
            weather_text = 'The temperature today in ' + cityname + 'is' + temper + 'degrees farenheit. '  + 'The current weather condition is, ' + status #setting up for the builtin linux text to speech
            subprocess.call(['espeak', '-ven+f2', '-s120', weather_text]) #convert the values in weather_text to speech by using linux command allowed by subprocess
            print("Status:", status)
            print("City:", cityname)
            print("Temperature: ", temper)
        except Exception as e:
            print(e)
        time.sleep(5)
def update_display(): #update the display on LCD
    while True:
        try:
            with lock: #allows this function to wait until the information needed is avalible before executing the code below
                if cityname is None:
                    lcd.clear()
                    lcd.home()
                    lcd.print("Getting location")
                else:
                    owm = pyowm.OWM(key)
                    loc = owm.weather_manager().weather_at_place(cityname)
                    weather = loc.weather
                    temp = weather.temperature(unit='fahrenheit')
                    status = weather.detailed_status
                    cleaned_temp_data = (int(temp['temp']))
                    lcd.clear()
                    lcd.home()
                    lcd.setCursor(0, 0)
                    lcd.print("City:" + cityname)
                    lcd.setCursor(0, 1)
                    lcd.print("Temp:" + str(cleaned_temp_data) + "F")
                    lcd.setCursor(9, 1)
                    lcd.print("Status:" + status)
        except Exception as e:
            print(e)
        for i in range(16): #allows our display on lcd to scroll to the left
            lcd.scrollDisplayLeft()
            time.sleep(0.3)
        lcd.home()
        lcd.setCursor(15, 1)
        time.sleep(0.5)
     
        
     
        
     
     
   
def main(): #main function for all the function to set up the sequence of the threads
    threads = [
        threading.Thread(target=get_weather),
        threading.Thread(target=update_display),
    ]
    for thread in threads:
        thread.start() #begins the execution of our threads
    for thread in threads:
        thread.join() # wait for the other exutable thread to finish
        
    
if __name__ == '__main__':
    
    main()



