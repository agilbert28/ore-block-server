import pvlib
from pvlib.irradiance import disc
import datetime as dt
from dateutil import tz
import pandas as pd
import numpy as np
import requests

# Birmingham, MI
coordinates = (42.53947240410033,
               -83.21562708740335)
elivation = 237.0 #float
timezone = 'America/Detroit'

# Oak Park, CA
# coordinates = (34.189075820781085,
#                -118.76189492425992)
# elivation = 1200.0 #float
# timezone = 'America/Los_Angeles'

cloudCover = 0
temperature = 12
pressure = 0

api = f'https://api.openweathermap.org/data/2.5/weather?lat={coordinates[0]}&lon={coordinates[1]}&units=metric&appid=c38c04c4dfbd1f8a5710153012af6ae2'
response = requests.get(api)
if response.status_code == 200:
   data = response.json()

   main = data['main']
   temperature = main['temp']
   pressure = main['pressure'] * 100

   clouds = data['clouds']
   cloudCover = clouds['all'] / 100

   print(f"Temperature: {temperature}*C")
   print(f"Pressure: {pressure} Pa")
   print(f"Cloud Cover: {cloudCover * 100}%")
else:
   print("Error in the HTTP request")

localTz = tz.gettz(timezone)
now = dt.datetime.now(tz=localTz)
print(now)
nowIndex = pd.DatetimeIndex([now])

location = pvlib.location.Location(coordinates[0], coordinates[1], timezone, elivation)
solpos = location.get_solarposition(now, pressure, temperature)
cs = location.get_clearsky(nowIndex, solar_position=solpos)

ghi = (0.35 + (1 - 0.35) * (1 - cloudCover)) * cs['ghi'][0]
dni = disc(ghi, solpos['zenith'], cloudCover)['dni']
dhi = ghi - dni * np.cos(np.radians(solpos['zenith']))
print(ghi, dni, dhi)

irradiance = pvlib.irradiance.get_total_irradiance(0, 90, solpos['zenith'][0], solpos['azimuth'][0], dni, ghi, dhi, dni_extra=1.2, surface_type='urban')
print(f"\nDirect: {irradiance['poa_direct'][0]} W/m2")
print(f"Diffuse: {irradiance['poa_diffuse'][0]} W/m2\n")
print(f"Total Irradiance: {irradiance['poa_global'][0] + 1} W/m2")
print(f"Total Illuminance: {(irradiance['poa_global'][0] + 1) * 120} lx")