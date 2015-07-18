#!/usr/bin/python
#
# Dock Profile Creation Script
# Vaughn Miller
# July 2015
# 
# Script to generate a Dock configuration profile for managing the
# dock in OS X.  Uses a json file as data input and outputs a 
# correctly formated mobileconfig file.

import argparse
import plistlib
import uuid
import json
import os
import sys


def error(message):
	''' Print an error message, then exit program '''
	print '#' * 80
	print '# Fatal Error:'
	print '#   ' + message
	print '#' * 80
	sys.exit()


def addStaticApp(appLabel, appPath, profile):
	'''Builds a dictionry for an application entry and
	them appends to the profile and returns the updated
	profile'''
	# Build the dict for the app
	a = {'mcx_typehint':1,
		'tile-type':'file-tile',
		'tile-data':{
			'file-label':appLabel,
			'file-data':{
				'_CFURLString':appPath,
				'_CFURLStringType':0
				}
			}
		}
	#append to the profile
	profile['PayloadContent'][0]['static-apps'].append(a)
	return profile


def addStaticOther(otherLabel, otherPath, profile):
	# build the dict
	a = {'mcx_typehint':2,
		'tile-type':'directory-tile',
		'tile-data':{
			'file-label':otherLabel,
			'file-data':{
				'_CFURLString':otherPath,
				'_CFURLStringType':0
				},
			'file-type':2
			}
		}
	#append to the profile
	profile['PayloadContent'][0]['static-others'].append(a)
	return profile


def addRelativeOther(otherLabel, otherPath, profile):
	a = {'mcx_typehint':2,
		'tile-type':'directory-tile',
		'tile-data':{
			'file-label':otherLabel,
			'home directory relative':otherPath,
			'arrangement':2,
			'displayas':2,
			'showas':1
			}
		}
	profile['PayloadContent'][0]['static-others'].append(a)
	return profile


def createProfile(applist, identifier, profile):
	'''Creates a new profile using the supplied list and identifier'''

	displayName = 'Dock Profile'
	description = 'Dock settings'
	# create new uuids
	profileUUID = str(uuid.uuid4())
	payloadUUID = str(uuid.uuid4())

	profileDict = {'PayloadIdentifier':identifier,
		'PayloadRemovalDisallowed':False,
		'PayloadScope':'User',
		'PayloadType':'Configuration',
		'PayloadUUID':profileUUID,
		'PayloadOrganization':'Lafayette College',
		'PayloadVersion':1,
		'PayloadDisplayName':displayName,
		'PayloadDescription':description,
		'PayloadContent':[{
			'PayloadType':'com.apple.dock',
			'PayloadVersion':1,
			'PayloadIdentifier':identifier,
			'PayloadEnabled':True,
			'PayloadUUID':payloadUUID,
			'PayloadDisplayName':'Dock',
			'tilesize':64,
			'size-immutable':True,
			'magnification':False,
			'largesize':64,
			'magnify-immutable':True,
			'magsize-immutable':True,
			'orientation':'bottom',
			'position-immutable':True,
			'mineffect':'genie',
			'mineffect-immutable':True,
			'launchanim':True,
			'launchanim-immutable':True,
			'autohide':False,
			'show-process-indicators':False,
			'show-process-indicators-immutable':True,
			'contents-immutable':True,
			'static-only':True,
			'static-apps':[],
			'static-others':[]
		}]
		}
	return profileDict


def addItemsToProfile(applist, profile):
	'''function to load in items from the json input file and
	add them to an existing empty profile'''

	try:
		with open(applist) as inputfile:
			try:
				inputJSON = json.load(inputfile)
			except ValueError, e:
				error('Problem with JSON : \n#      ' + str(e))
	except IOError, e:
		error('Unable to load JSON file : \n#      ' + str(e))

	for category in inputJSON:
		if category == "static-apps":
			for app in inputJSON[category]:
				profile = addStaticApp(app, inputJSON[category][app], profile)
		if category == "relative-others":
			for other in inputJSON[category]:
				profile = addRelativeOther(other, inputJSON[category][other], profile)
		if category == "static-others":
			for other in inputJSON[category]:
				profile = addStaticOther(other, inputJSON[category][other], profile)
	return profile


def updateProfile(applist, profile):
	''' Empy the items out of a profile, increment the version 
	and then add items to the profile '''

	profileDict = plistlib.readPlist(profile)
	# Empty the existing items
	profileDict['PayloadContent'][0]['static-apps'] = []
	profileDict['PayloadContent'][0]['static-others'] = []
	# Increment the payload version
	profileDict['PayloadContent'][0]['PayloadVersion'] = profileDict['PayloadContent'][0]['PayloadVersion'] + 1
	# Add the disired items to the dictionary
	profileDict = addItemsToProfile(applist, profileDict)

	return profileDict # Return the updated dictionary


def main():
	'''Main method'''
	parser = argparse.ArgumentParser()
	parser.add_argument('--new', help='Create new profile', action='store_true')
	parser.add_argument('--identifier', help='reverse domain style identifier for a new profile')
	parser.add_argument('--profile', help='/path/to/profile')
	parser.add_argument('--input', help='/path/to/inputfile')

	args = parser.parse_args()

	if (not args.input or not args.profile):
		error('Must provide input and profile arguments')
	else:
		if not os.path.isfile(args.input):
			error('input file ' + str(os.path.abspath(args.input)) + ' not found')
		if args.new:
			if os.path.isfile(args.profile):
				error(str(os.path.abspath(args.profile)) + ' already exists!')
			elif not args.identifier:
				error('Argument --identifier required with argument --new')
			else:
				newProfile = createProfile(args.input, args.identifier, args.profile)
				newProfile = addItemsToProfile(args.input, newProfile)
				if not os.path.exists(os.path.dirname(args.profile)):
					os.makedirs(os.path.dirname(args.profile))
				try:
					plistlib.writePlist(newProfile, args.profile)
				except IOError, e:
					error(str(e))
		elif os.path.isfile(args.profile):
			newProfile = updateProfile(args.input, args.profile)
			plistlib.writePlist(newProfile, args.profile)
		else:
			error(str(os.path.abspath(args.profile)) + ' does not exist!')
		

if __name__ == '__main__':
	main()