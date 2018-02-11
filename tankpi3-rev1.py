#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import os
import json
import signal
import subprocess
import sys
import time
import ThunderBorg
import pygame

# Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
sys.stdout = sys.stderr
def getConfigurations():
	path = os.path.dirname(os.path.realpath(sys.argv[0]))
	#get configs
	configurationFile = path + '/config.json'
	configurations = json.loads(open(configurationFile).read())
	return configurations

def TB_Startup():
	# Setup the ThunderBorg
	TB = ThunderBorg.ThunderBorg()
	# TB.i2cAddress = 0x15   # Uncomment and change the value if you have changed the board address
	TB.Init()
	if not TB.foundChip:
		boards = ThunderBorg.ScanForThunderBorg()
		if len(boards) == 0:
			print 'No ThunderBorg found, check you are attached :)'
		else:
			print 'No ThunderBorg at address %02X, but we did find boards:' % TB.i2cAddress
			for board in boards:
				print '    %02X (%d)' % (board, board)
			print 'If you need to change the I²C address change the setup line so it is correct, e.g.'
			print 'TB.i2cAddress = 0x%02X' % (boards[0])
		sys.exit()
	# Ensure the communications failsafe has been enabled!
	failsafe = False
	for i in range(5):
		TB.SetCommsFailsafe(True)
		failsafe = TB.GetCommsFailsafe()
		if failsafe:
			break
	if not failsafe:
		print 'Board %02X failed to report in failsafe mode!' % TB.i2cAddress
		sys.exit()
	return TB

def Joystick_Startup(TB):
	# Setup pygame and wait for the joystick to become available
	os.environ["SDL_VIDEODRIVER"] = "dummy"  # Removes the need to have a GUI window
	pygame.init()
	# pygame.display.set_mode((1,1))
	print 'Waiting for joystick... (press CTRL+C to abort)'
	while True:
		try:
			try:
				pygame.joystick.init()
				# Attempt to setup the joystick
				if pygame.joystick.get_count() < 1:
					# No joystick attached, set LEDs blue
					TB.SetLeds(0, 0, 1)
					pygame.joystick.quit()
					time.sleep(0.1)
				else:
					# We have a joystick, attempt to initialise it!
					joystick = pygame.joystick.Joystick(0)
					break
			except pygame.error:
				# Failed to connect to the joystick, set LEDs blue
				TB.SetLeds(0, 0, 1)
				pygame.joystick.quit()
				time.sleep(0.1)
		except KeyboardInterrupt:
			# CTRL+C exit, give up
			print '\nUser aborted'
			TB.SetCommsFailsafe(False)
			TB.SetLeds(0, 0, 0)
			sys.exit()
	print 'Joystick found'
	return joystick
	
def DoShutdown(TB,joystick,ledBatteryMode):
	# Check for shutdown button combinations
	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
	out, err = p.communicate()
	for line in out.splitlines():
		if 'web-rtc' in line:
			pid = int(line.split(None, 1)[0])
			os.kill(pid, signal.SIGKILL)
		if ledBatteryMode:
			TB.SetLedShowBattery(False)
			TB.SetLeds(0, 0, 0)
			ledBatteryMode = False
			TB.SetCommsFailsafe(False)
			TB.MotorsOff()
	os.system("shutdown now -h")
	sys.exit()

def main():
	TB=TB_Startup()
	configurations = getConfigurations()
	leftStick = int(configurations["axis"][0]["LeftAxis"])
	leftInverted = int(configurations["axis"][0]["LeftInverted"])
	rightStick = int(configurations["axis"][0]["RightAxis"])
	rightInverted = int(configurations["axis"][0]["RightInverted"])
	buttonSlow = int(configurations["buttons"][0]["slow"])
	slowFactor = float(configurations["buttons"][0]["slowFactor"])
	buttonFast = int(configurations["buttons"][0]["fast"])
	rightShoulder = int(configurations["buttons"][0]["rightShoulder"])
	leftShoulder = int(configurations["buttons"][0]["leftShoulder"])
	psButton = int(configurations["buttons"][0]["PS"])
	interval = float(configurations["interval"])
	normalFactor = float(configurations["normalFactor"])
	
	# Power settings
	voltageIn = float(configurations["voltageIn"])
	voltageOut = float(configurations["voltageOut"])
	
	# Setup the power limits
	if voltageOut > voltageIn:
		maxPower = 1.0
	else:
		maxPower = voltageOut / voltageIn
		
	# Show battery monitoring settings
	battMin, battMax = TB.GetBatteryMonitoringLimits()
	battCurrent = TB.GetBatteryReading()
	print 'Battery monitoring settings:'
	print '    Minimum  (red)     %02.2f V' % battMin
	print '    Half-way (yellow)  %02.2f V' % ((battMin + battMax) / 2)
	print '    Maximum  (green)   %02.2f V' % battMax
	print
	print '    Current voltage    %02.2f V' % battCurrent
	print
	joystick=Joystick_Startup(TB)
	joystick.init()
	TB.SetLedShowBattery(True)
	ledBatteryMode = True
	try:
		print 'Press CTRL+C to quit'
		#set drives and steers to zero
		driveLeft = 0.0
		driveRight = 0.0
		
		# Loop indefinitely
		while True:
			# Get the latest events from the system
			events = pygame.event.get()
			# Event Handler		
			for event in events:
				if event.type == pygame.QUIT:
					DoShutdown(TB,joystick,ledBatteryMode)	
				elif event.type == pygame.JOYBUTTONDOWN:
					# A button on the joystick just got pushed down
					#Three key salute shutdown
					if joystick.get_button(psButton) and joystick.get_button(leftShoulder) and joystick.get_button(rightShoulder):
						DoShutdown(TB,joystick,ledBatteryMode)
				elif event.type == pygame.JOYAXISMOTION:
					# Read axis positions (-1 to +1)
					if leftInverted:
						leftinput = -joystick.get_axis(leftStick)
					else:
						leftinput = joystick.get_axis(leftStick)
					if rightInverted:
						rightinput = -joystick.get_axis(rightStick)
					else:
						rightinput = joystick.get_axis(rightStick)
					# Apply steering speeds
					if joystick.get_button(buttonFast):
						#Do nothing, motors will run 100%
						dummy = 0
					elif joystick.get_button(buttonSlow):
						leftinput *= slowFactor
						rightinput *= slowFactor
					else:
						leftinput *= normalFactor
						rightinput *= normalFactor

					# Determine the drive power levels
					driveLeft = -leftinput
					driveRight = -rightinput
					
			# Set the motors to the new speeds
			TB.SetMotor1(driveRight * maxPower)
			TB.SetMotor2(driveLeft * maxPower)
		# Change LEDs to purple to show motor faults
		if TB.GetDriveFault1() or TB.GetDriveFault2():
			if ledBatteryMode:
				TB.SetLedShowBattery(False)
				TB.SetLeds(1, 0, 1)
				ledBatteryMode = False
		else:
			if not ledBatteryMode:
				TB.SetLedShowBattery(True)
				ledBatteryMode = True
		# Wait for the interval period
		time.sleep(interval)
		# Disable all drives
		TB.MotorsOff()
	except KeyboardInterrupt:
		#CTRL+C exit, disable all drives
		TB.MotorsOff()
		TB.SetCommsFailsafe(False)
		TB.SetLedShowBattery(False)
		TB.SetLeds(0, 0, 0)
if __name__ == "__main__":
	main()
