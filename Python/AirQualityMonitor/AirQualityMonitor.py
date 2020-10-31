# Created by Arpan Neupane.
# Copyright © 2020 Arpan Neupane. All rights reserved.

from tkinter import *
from PIL import ImageTk, Image
import requests
import json

root = Tk()
root.title('Air Quality Monitor')
root.geometry('1000x300')

def search_zipcode():
    
    try:
        api_request = requests.get('http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=' + zipCode.get() + '&distance=10&API_KEY=3A68CA6E-7653-4005-A4DC-95604871E492')
        api = json.loads(api_request.content)
        city = api[0]['ReportingArea']
        quality = api[0]['AQI']
        category = api[0]['Category']['Name']

        if quality > 0 and quality < 50:
            root.configure(bg='#00FF00')

        if quality > 50 and quality < 100:
            root.configure(bg='yellow')

        if quality > 100 and quality < 150:
            root.configure(bg='#ff8000')
        
        if quality > 150 and quality < 200:
            root.configure(bg='#ff0000')
        
        if quality > 200 and quality < 300:
            root.configure(bg='purple')
        
        if quality > 300:
            root.configure(bg='#800020')

        statslabel = Label(root, text=city + " |" + " Air Quality: " + str(quality) + ' | ' + category + " condition", font=('Helvetica', 20))
        statslabel.pack()

    except Exception as e:
        errorlabel = Label(root, text='Not a valid zip code or you are not connected to the internet.')
        errorlabel.pack()



zipCode = Entry(root)
zipCode.pack()

submit_button = Button(root, text="Search Zipcode", command=search_zipcode)
submit_button.pack()
root.mainloop()
