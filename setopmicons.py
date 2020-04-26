#!/bin/python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import xml.etree.ElementTree as ET

import argparse
import os


#Declaring namespaces before load the file to avoid the print of "ns0" space
ET.register_namespace('', "http://openbox.org/")
ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

ICONSIZE = 48


themeObject = Gtk.IconTheme.get_default() #Getting the current theme to extract
#the icons path
menupath = os.path.expanduser('~/.config/openbox/menu.xml')
tree = ET.parse(menupath) #The menu file target
root = tree.getroot()


parser = argparse.ArgumentParser(description='It sets icons to the openbox menu.')
args = parser.parse_args()

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
        pathToIcon = ''
    return pathToIcon

def findAnIcon(item, themeObject, ICONSIZE=32):
    """Fretch a icon path using different methods"""
    pathToIcon = iconByLabel(item, themeObject, ICONSIZE)
    if pathToIcon:
        return pathToIcon

    pathToIcon = iconByOldName(item, themeObject, ICONSIZE)
    if pathToIcon:
        return pathToIcon

    if item.tag == '{http://openbox.org/}menu':
        pathToIcon = iconByName(item.get('id'), themeObject, ICONSIZE)
        return pathToIcon 

    if item[0].get('name').lower() in [ 'reconfigure','restart']:
        pathToIcon = iconByName('view-refresh', themeObject, ICONSIZE)
        return pathToIcon

    if item[0].get('name').lower() == 'exit':
        pathToIcon = iconByName('exit', themeObject, ICONSIZE)
        return pathToIcon



    #Find by the command
    action = item[0]
    execute = action[0]
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
            pathToIcon = findAnIcon(item, themeObject, ICONSIZE)
            iterateRecursively(item)
            if not pathToIcon:
                continue
            else:
                item.set('icon', pathToIcon)

        elif item.tag == '{http://openbox.org/}item':
            pathToIcon = findAnIcon(item, themeObject, ICONSIZE)

            if not pathToIcon:
                continue

            else:
                item.set('icon', pathToIcon)

        else:
            print("Can't recognize the item.tag = \'", item.tag, "\'", sep = '')

for element in root:
    iterateRecursively(element)

tree.write('/home/terminator/.config/openbox/menu.xml')
