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
from datetime import datetime
from astral import LocationInfo
from astral.sun import sun

# Set up Server
server = JavaServer('10.0.0.247', 25565)

# Set up DotStars
dots = dotstar.DotStar(board.SCK, board.MOSI, 25, brightness = 0.2)
dots.fill((0, 0, 0))
dim = False

# Set up Sunrise/Sunset Location
location = LocationInfo(name = 'Detroit', region = 'USA', timezone = 'America/Detroit',
						latitude = 44.953060, longitude = -89.614100)

# Every 10 seconds...
while True:

	# While the Minecraft Server is running...
	if subprocess.check_output('screen -ls | { egrep -c "Pinecraft" || true; }',
	shell = True).strip().decode('utf-8') == '1':

		# Check today's Sunrise/Sunset
		s = sun(location.observer, date = datetime.today(), tzinfo = location.timezone)

		# Check the Day of Week and Time
		now = datetime.now().time()
		day = datetime.today().weekday()

		# Set to Dim between Sunset and Sunrise
		dim = (now > s['sunset'].time()) or (now < s['sunrise'].time())

		# Display Number of Players & Latency
		players = server.status().players.online
		print(f'Players Online: {players}  Latency: {server.status().latency} ms')
		if players > 0:
			print(', '.join(server.query().players.names))

		# If Someone is Online...
		if players > 0 and (day == 6 or day == 7):
			# Increase the Brightness
			dots.fill((255, 0, 0))
			if dim:
				dots.brightness = 0.1
			else:
				dots.brightness = 0.9

		elif players > 0:
			dots.fill((64, 255, 255))
			if dim:
				dots.brightness = 0.1
			else:
				dots.brightness = 0.9
				
		# If Someone is not Online...
		else:
			# Lower the Brightness
			dots.fill((64, 255, 255))
			if dim:
				dots.brightness = 0.01
			else:
				dots.brightness = 0.2

	# Otherwise...		
	else:
		# Turn off
		dots.fill((0, 0, 0))

	dots.show()
	time.sleep(10)
