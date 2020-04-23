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

ICONSIZE = 32


themeObject = Gtk.IconTheme.get_default() #Getting the current theme to extract
#the icons path
menupath = os.path.expanduser('~/.config/openbox/menu.xml')
tree = ET.parse(menupath) #The menu file target
root = tree.getroot()


parser = argparse.ArgumentParser(description='It sets icons to the openbox menu.')
args = parser.parse_args()

def findAnIcon(iconName, item, themeObject):
    if ' ' in iconName:
       #verify if the current theme has an icon with the previous theme icon name
       iconOldPath = item.get('icon')
       iconName = iconOldPath.split('/')[-1]
       iconName = iconName.split('.')[0] #discharting the extension
       iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                Gtk.IconLookupFlags.FORCE_SVG)


    #Create an object with the iformation of the icon found
    iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
            Gtk.IconLookupFlags.FORCE_SVG)


    if not iconInfoObject:
        #trying to find the icon using its label
        label = item.get('label')
        iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                Gtk.IconLookupFlags.FORCE_SVG)
    if not iconInfoObject:
        #trying find the icon using its label in lowercase
        label = label.lower()
        iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                Gtk.IconLookupFlags.FORCE_SVG)

        
    #If the path is empty, ask what to do
    while not iconInfoObject:
        print ("Atention: Icon \"", iconName, "\" was not found.", sep='')
        answer = input("You want to try another name? (y/N) ")
        if answer.lower() == 'y' or answer.lower() == 'yes':

            print("Enter the new iconName:")
            iconName = input("iconName = ")
            print("")
            if ' ' in iconName:
                iconName = removeSpaces(iconName)
        elif answer.lower() == "n" or answer.lower() == "no" or answer == '':
            pathToIcon = ''
            print("")
            return pathToIcon
        else:
            print("The option \"", answer, "\" is invalid\n", sep='')
            continue
                #Create an object with the iformation of the looked icon.
        iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                Gtk.IconLookupFlags.FORCE_SVG)
        #Obtaining the path for the icon
    pathToIcon = iconInfoObject.get_filename()

    return pathToIcon

def removeSpaces(iconName):
    #the string to search must not contain any spaces characters
    while ' ' in iconName:
        print("The iconName =", iconName, "string contains an space")
        iconName = input("Enter a valid icon name\n")

    return iconName

#it will work only for menus with no more than one degree of recursion
for element in root:# Iterate over the root menu elements
    #Skip the root menu constructor
    if element.get("id") == "root-menu":
        continue
    for item in element: #Try to find an icon for each menu item
        #If the tag is a sepatator just skip. We just need tags that indecate menu
        #items
        if item.tag == '{http://openbox.org/}separator':
            continue
        #Each item is associated to only an action, which is stored at position
        #"0"
        action = item[0]
        if action.get('name') != "Execute":
            continue
        execute = action[0]
        iconToFind = execute.text#Get the command name string.

        pathToIcon = findAnIcon(iconToFind, item, themeObject)
        if not pathToIcon:
            continue
        item.set('icon', pathToIcon)
        tree.write('/home/terminator/.config/openbox/menu.xml')

