#!/bin/python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import xml.etree.ElementTree as ET
import os
import sys
import pdb

import argparse
from xdg.DesktopEntry import DesktopEntry

parser = argparse.ArgumentParser(description='Program to set icons to your custom openbox menu')
parser.add_argument('-d', action='store_true', help="Erase current icons from menu.xml")
parser.add_argument('-i', type=str, nargs=1, help="Look for a path to a icon with the provided name", default=None)

args = parser.parse_args()

# Generation dictionary with executable names and their freedesktop.org .desktop objects 

dotDesktopFiles = os.listdir('/usr/share/applications/')

dictionaryDesktop = {}

for archive in dotDesktopFiles:
    if archive.split('.')[-1] != 'desktop' : # Exclude non .desktop files
        continue
    dotDesktopObject = DesktopEntry()
    dotDesktopObject.parse('/usr/share/applications/' + archive)
    executable = dotDesktopObject.getExec().split(' ')[0]
    dictionaryDesktop[executable] = dotDesktopObject


# Declaring namespaces before load the file to avoid the print of "ns0" space
ET.register_namespace('', "http://openbox.org/")
ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

ICONSIZE = 48


themeObject = Gtk.IconTheme.get_default() # Getting the current theme to extract
# the icons path
menupath = os.path.expanduser('~/.config/openbox/menu.xml')
tree = ET.parse(menupath) # The menu file target
root = tree.getroot()




def iconByOldName(item, themeObject, ICONSIZE = 32):
    """verify if the current theme has an icon with the previous theme icon name"""
    iconOldPath = item.get('icon')
    if iconOldPath:
        iconName = iconOldPath.split('/')[-1]
        iconName = iconName.split('.')[0] #discharting the extension
        iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
        Gtk.IconLookupFlags.FORCE_SVG)

        if not iconInfoObject:
            return ''

        else:
            pathToIcon = iconInfoObject.get_filename()
            return pathToIcon

    else:
        return ''

def iconByLabel(item, themeObject, ICONSIZE = 32):
    """Fetch a icon path by item label"""

    #trying to find the icon using its label
    label = item.get('label')
    label = label.replace(' ','-')
    iconInfoObject = themeObject.lookup_icon(label, ICONSIZE,
            Gtk.IconLookupFlags.FORCE_SVG)
    if iconInfoObject:
        pathToIcon = iconInfoObject.get_filename()
        return pathToIcon

    #trying find the icon using its label in lowercase
    label = label.lower()
    iconInfoObject = themeObject.lookup_icon(label, ICONSIZE,
            Gtk.IconLookupFlags.FORCE_SVG)
    if iconInfoObject:
        pathToIcon = iconInfoObject.get_filename()
        return pathToIcon

    else:
        return ''


def iconByName(iconName, themeObject, ICONSIZE = 32, QUESTION = True):
    """Fetch a icon path by its name"""

    #Create an object with the iformation of the icon found
    iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                Gtk.IconLookupFlags.FORCE_SVG)

    if QUESTION == True:
        #If the path is empty, ask what to do
        while not iconInfoObject:
            print ("Atention: Icon \"", iconName, "\" was not found.", sep = '')
            answer = input("Do you want to try another name? (y/N) ")
            if answer.lower() == 'y' or answer.lower() == 'yes':
                print("Enter the new iconName:")
                iconName = input("iconName = ")
                print("")

                if ' ' in iconName:
                    iconName = removeSpaceWarning(iconName)

            elif answer.lower() == "n" or answer.lower() == "no" or answer == '':
                pathToIcon = ''
                print("")
                return pathToIcon

            else:
                print("The option \"", answer, "\" is invalid\n", sep = '')
                continue
            #Create an object with the iformation of the looked icon.
            iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                    Gtk.IconLookupFlags.FORCE_SVG)
        #Obtaining the path for the icon
        pathToIcon = iconInfoObject.get_filename()

    else:

        if iconInfoObject:
            pathToIcon = iconInfoObject.get_filename()
        else:
            pathToIcon = ''

    return pathToIcon

def findAnIcon(item, themeObject, ICONSIZE=32):
    """Fetch a icon path using different methods"""
    pathToIcon = iconByLabel(item, themeObject, ICONSIZE)
    if pathToIcon:
        return pathToIcon

    pathToIcon = iconByOldName(item, themeObject, ICONSIZE)
    if pathToIcon:
        return pathToIcon

    if item.tag == '{http://openbox.org/}menu':
        pathToIcon = iconByName(item.get('id'), themeObject, ICONSIZE, QUESTION=False)
        if not pathToIcon:
            pathToIcon = iconByName(item.get('label'), themeObject, ICONSIZE)
            return pathToIcon 
        else:
            return pathToIcon

    if item[0].get('name').lower() in [ 'reconfigure','restart']:
        pathToIcon = iconByName('view-refresh', themeObject, ICONSIZE)
        return pathToIcon

    if item[0].get('name').lower() == 'exit':
        pathToIcon = iconByName('exit', themeObject, ICONSIZE)
        return pathToIcon
    
    # Find by .desktop file parsing
    action = item[0]
    execute = action[0]


    pathToIcon = ''
    if execute.text in dictionaryDesktop.keys():
        dotDesktop = dictionaryDesktop[execute.text]
        iconToFind = dotDesktop.getIcon()
        pathToIcon = iconByName(iconToFind, themeObject, ICONSIZE, QUESTION = False)

    if pathToIcon:
        return pathToIcon


    # Find by the command
    iconToFind = execute.text
    pathToIcon = iconByName(iconToFind, themeObject, ICONSIZE)
    if pathToIcon:
        return pathToIcon
    else:
        return ''


def removeSpacesWarning(iconName):
    """If the user types a iconName with spaces, show an error"""
    while ' ' in iconName:
        print("The \"", iconName, "\" string contains an space", sep = '')
        iconName = input("Enter a valid icon name\niconName = ")
        print("")

    return iconName


def iterateRecursively(xmlEtreeElement):
    """Iterate through the menu elements recursively and try to find their icons."""
    element = xmlEtreeElement

    for item in element:

        if item.tag == '{http://openbox.org/}separator':
            continue

        elif item.tag == '{http://openbox.org/}menu':
            if args.d == True:
                item.set('icon', '')
                continue

            pathToIcon = findAnIcon(item, themeObject, ICONSIZE)
            iterateRecursively(item)

            if not pathToIcon:
                continue
            else:
                item.set('icon', pathToIcon)

        elif item.tag == '{http://openbox.org/}item':
            if args.d == True:
                item.set('icon', '')
                continue

            pathToIcon = findAnIcon(item, themeObject, ICONSIZE)

            if not pathToIcon:
                continue
            else:
                item.set('icon', pathToIcon)
                

        else:
            print("Can't recognize the item.tag = \'", item.tag, "\'", sep = '')

if args.i:
    pathToIcon = iconByName(args.i[0], themeObject, ICONSIZE)
    print(pathToIcon)
    sys.exit()

## Set labels to the submenus if they do not have ##
menuLabels={}
for element in root:
    menuLabels[element.get('id')] = element.get('label')

for element in root:
    if element.get('id') == 'root-menu':
        for item in element:
            if item.tag == '{http://openbox.org/}menu':
                itemId = item.get('id')
                item.set('label',menuLabels[itemId])
##########################################################

for element in root:
    iterateRecursively(element)


homeDir = os.path.expanduser('~')

tree.write(homeDir + '/.config/openbox/menu.xml')
