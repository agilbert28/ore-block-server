"""Who's Online (whosonline.py)

This script changes the DotStar lights when someone has joined the Boys Night
server.

Notes
-------------------------------------------------------------------------------
Created by Austin Gilbert for the Boys.
"""

import subprocess
import time
import board
import adafruit_dotstar as dotstar
from mcstatus import JavaServer
from astral import LocationInfo
from astral.sun import sun
import pvlib
from pvlib.irradiance import disc
import datetime as dt
from dateutil import tz
import pandas as pd
import numpy as np
import requests

# Editable Global Variables
coordinates = (42.53947240410033,
               -83.21562708740335) # Birmingham, MI
elivation = 237.0 #float
timezone = 'America/Detroit'

# Default Values
cloudCover = 0
temperature = 12
pressure = 0

# Set up Server
server = JavaServer('10.0.0.247', 25565)

# Set up DotStars
dots = dotstar.DotStar(board.SCK, board.MOSI, 25, brightness = 0.2)
dots.fill((0, 0, 0))
dim = False
brightness = 0.2

location = pvlib.location.Location(coordinates[0], coordinates[1], timezone, elivation)
localTz = tz.gettz(timezone)

# Every 10 seconds...
while True:

	# While the Minecraft Server is running...
	try:
		if subprocess.check_output('screen -ls | { egrep -c "Pinecraft" || true; }',
		shell = True).strip().decode('utf-8') == '1':

			api = f'https://api.openweathermap.org/data/2.5/weather?lat={coordinates[0]}&lon={coordinates[1]}&units=metric&appid=c38c04c4dfbd1f8a5710153012af6ae2'
			response = requests.get(api)
			try:
				data = response.json()

				main = data['main']
				temperature = main['temp']
				pressure = main['pressure'] * 100

				clouds = data['clouds']
				cloudCover = clouds['all'] / 100

				print(f"Temperature: {temperature}*C")
				print(f"Pressure: {pressure} Pa")
				print(f"Cloud Cover: {cloudCover * 100}%")
			except:
				print("Error in the HTTP request")

			# Check the Day of Week and Time
			localTz = tz.gettz(timezone)
			now = dt.datetime.now(tz=localTz)
			nowIndex = pd.DatetimeIndex([now])
			print(now)
			day = dt.datetime.today().weekday()

			# Illuminance/Irradiance Calculations
			location = pvlib.location.Location(coordinates[0], coordinates[1], timezone, elivation)
			solpos = location.get_solarposition(now, pressure, temperature)
			cs = location.get_clearsky(nowIndex, solar_position=solpos)
			ghi = (0.35 + (1 - 0.35) * (1 - cloudCover)) * cs['ghi'][0]
			dni = disc(ghi, solpos['zenith'], cloudCover)['dni']
			dhi = ghi - dni * np.cos(np.radians(solpos['zenith']))
			irradiance = pvlib.irradiance.get_total_irradiance(0, 90, solpos['zenith'][0], solpos['azimuth'][0], dni, ghi, dhi, dni_extra=1.2, surface_type='urban')
			totalIrradiance = irradiance['poa_global'][0] + 1
			print(f"Total Irradiance: {totalIrradiance} W/m2")

			# Match Brightness to Irradiance
			if totalIrradiance < 7:
				brightness = 0.01
			elif totalIrradiance > 700:
				brightness = 1
			else:
				brightness = totalIrradiance / 700
			dots.brightness = brightness

			# Display Number of Players & Latency
			players = server.status().players.online
			print(f'Players Online: {players}  Latency: {server.status().latency} ms')
			if players > 0:
				print(', '.join(server.query().players.names))

			# If Someone is Online...
			if players > 0:
				# Turn Red
				dots.fill((255, 0, 0))
			# If Someone is not Online...
			else:
				# Turn Cyan
				dots.fill((64, 255, 255))

		# Otherwise...		
		else:
			# Turn off
			print('brightness = 0')
			dots.fill((0, 0, 0))

	except:
		# Turn off
		print('brightness = 0')
		print('Error')
		# dots.fill((0, 0, 0))

	# dots.show()
	time.sleep(10)
