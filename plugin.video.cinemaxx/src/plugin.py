import xbmc, xbmcaddon
import os, re
try:
	try: import cPickle as pickle
	except ImportError: import pickle
except: pass
try:
	try: import json
	except ImportError: import simplejson as json
except: pass


addonId = 'plugin.video.cinemaxx'

selfAddon = xbmcaddon.Addon(id=addonId)
profilePath = xbmc.translatePath(selfAddon.getAddonInfo('profile'))

try: os.makedirs(profilePath)
except: pass


def getPluginVersion():
	return "%s v%s" % (addonId, selfAddon.getAddonInfo('version'))


def getPluginPath():
	return xbmc.translatePath(selfAddon.getAddonInfo('path'))


def getSetting(settingId):
	return selfAddon.getSetting(settingId)


def openSettings():
	selfAddon.openSettings()


def saveData(filename, data):
	savePath = os.path.join(profilePath, filename)
	try:
		pickle.dump(data, open(savePath, 'wb'))
		return True
	except pickle.PickleError:
		return False


def loadData(filename):
	loadPath = os.path.join(profilePath, filename)
	if os.path.isfile(loadPath):
		try: return pickle.load(open(loadPath))
		except: return False
	else:
		return False
