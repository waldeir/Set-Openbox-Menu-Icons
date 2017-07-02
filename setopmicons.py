#!/bin/python2

import gtk
import xml.etree.ElementTree as ET

#Declaring namespaces before load the file to avoid the print of "ns0" space
ET.register_namespace('', "http://openbox.org/")
ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

ICONSIZE = 32


themeObject = gtk.icon_theme_get_default() #Getting the current theme to extract
#the icons path

tree = ET.parse('/home/terminator/.config/openbox/menu.xml') #The menu file target
root = tree.getroot()


def findAnIcon(iconName, item, themeObject):
    if ' ' in iconName:
       #verify if the current theme has an icon with the previous theme icon name
       iconOldPath = item.get('icon')
       iconName = iconOldPath.split('/')[-1]
       iconName = iconName.split('.')[0] #discharting the extension
       iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                gtk.ICON_LOOKUP_FORCE_SVG)


    #Create an object with the iformation of the looked icon
    iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
            gtk.ICON_LOOKUP_FORCE_SVG)


    if not iconInfoObject:
        #trying to find the icon using its label
        label = item.get('label')
        iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                gtk.ICON_LOOKUP_FORCE_SVG)
    if not iconInfoObject:
        #trying find the icon using its label in lowercase
        label = label.lower()
        iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                gtk.ICON_LOOKUP_FORCE_SVG)
#    if not iconInfoObject:
#        #verify if the actual theme has an icon with the previous theme icon name
#        iconOldPath = item.get('icon')
#        iconName = iconOldPath.split('/')[-1]
#        iconName = iconName.split('.')[0] #discharting the extension
#        iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
#                gtk.ICON_LOOKUP_FORCE_SVG)

        
    #If the path is empty, ask what to do
    while not iconInfoObject:
        print "Sorry, it was not possible to find the icon with the name %s" % (iconName)
        print "Want to try another name? (y/N)" 
        answer = str(raw_input())
        if answer == 'y':

            print "Enter the new iconName:"
            iconName = str(raw_input())
            if ' ' in iconName:
                iconName = removeSpaces(iconName)
        else:
            pathToIcon = ''
            return pathToIcon
                #Create an object with the iformation of the looked icon.
        iconInfoObject = themeObject.lookup_icon(iconName, ICONSIZE,
                gtk.ICON_LOOKUP_FORCE_SVG)
        #Obtaining the path for the icon
    pathToIcon = iconInfoObject.get_filename()

    return pathToIcon

def removeSpaces(iconName):
    #the string to search must not contain any spaces characters
    while ' ' in iconName:
        print "The iconName = '%s' string contains an space" % (iconName)
        print "Enter a valid icon name"
        iconName = str(raw_input())

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

