#!/usr/bin/python3

import datetime
from flask import current_app as app
from flask import g, url_for
from flask.json import loads
import os
import shutil
from org_chart_maker.utils import removeSuffix
from werkzeug.utils import secure_filename
import xml.dom.minidom as xml

PERSON_WIDTH = 200
PERSON_HEIGHT = 50

DIAGRAMS_DIR = "save-files";
PHOTOS_DIR_NAME = "photos";

def getDiagramName():
    """Get the diagram name."""

    try:
        diagramName = g.diagramName
    except AttributeError as error:
        diagramName = "new-diagram" # Hack. Must rename after saving diagram.

    return diagramName

def getUserName():
    """Get the username."""

    if g.user is None:
        userName = "example"
    else:
        userName = g.user['username']

    return userName

def getDiagramsDir():
    """Get the folder for the diagrams of the current user."""

    # TODO: Perhaps move this to the "instance" dir.
    rootDiagramsDir = os.path.join(app.root_path, "..", DIAGRAMS_DIR)

    # Determine user name.
    userName = getUserName()

    # Determine user directory.
    userDir = os.path.join(rootDiagramsDir, userName)

    # Ensure the directory exists.
    if not os.path.exists(userDir):
        os.mkdir(userDir)

    # Return it.
    return userDir

def getRootPhotosDir():
    """Get the root photos directory."""

    return os.path.join(app.root_path, "static", PHOTOS_DIR_NAME)

def getPhotosDir(diagramName = None):
    """Get the folder for the photos."""

    # Get photos root directory.
    rootPhotosDir = getRootPhotosDir()

    # Add the user name.
    userName = getUserName()
    userPhotosDir = os.path.join(rootPhotosDir, userName)

    # Add the diagram name.
    if not diagramName:
        diagramName = getDiagramName()
    diagramPhotosDir = os.path.join(userPhotosDir, diagramName)

    # Ensure the directory exists.
    if not os.path.exists(diagramPhotosDir):
        os.makedirs(diagramPhotosDir)

    # Return full path.
    return diagramPhotosDir

def getPhotosUrlPath(photoName, diagramName = None):
    """Get the URL path the given photo."""

    # Set diagram name if not given.
    if not diagramName:
        diagramName = getDiagramName()

    # Hack.
    return "/static/" + PHOTOS_DIR_NAME + "/" + getUserName() + "/" + diagramName + "/" + photoName

def delete(diagram):
    # Append timestamp to deleted file name.
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")

    # Determine destination.
    source = os.path.join(getDiagramsDir(), diagram)
    dest = os.path.join(getDiagramsDir(), "deleted")

    # Create "deleted" directory if it does not exist.
    if not os.path.exists(dest):
        os.mkdir(dest)

    # Move the file.
    destFileName = os.path.join(dest, diagram)
    if os.path.exists(destFileName):
        os.remove(destFileName)
    shutil.move(source, dest)

    # Move the photos directory if it exists.
    photosFolder = getPhotosDir(diagram)

    if os.path.exists(photosFolder):
        # Create "deleted" directory if it does not exist.
        deletedPhotosFolder = os.path.join(getRootPhotosDir(), getUserName(), "deleted")
        if not os.path.exists(deletedPhotosFolder):
            os.mkdir(deletedPhotosFolder)

        # Move the photos folder.
        destFolderName = os.path.join(deletedPhotosFolder, diagram)
        if os.path.exists(destFolderName):
            deletePhotoFolder(destFolderName)
        shutil.move(photosFolder, deletedPhotosFolder)

def deletePhotoFolder(folderPath):
    """Delete a photo folder."""

    # Delete photos.
    for fileName in os.listdir(folderPath):
        os.remove(os.path.join(folderPath, fileName))

    # Delete folder.
    os.rmdir(folderPath)

def rename(diagram, newName):
    # Ensure ending exists.
    if not newName.endswith(".xml"):
        newName += ".xml"

    # Do the rename.
    try:
        source = os.path.join(getDiagramsDir(), diagram)
        dest = os.path.join(getDiagramsDir(), newName)
        shutil.move(source, dest)

        # Return status.
        returnData = {
          "status": "OK",
          "newName": newName
        }
    except FileNotFoundError as error:
        # Return status.
        returnData = {
          "status": "Failed",
          "problem": str(error)
        }

    return returnData

    # Convert into JSON:
    # return json.dumps(returnData)

def save(name, persons, relationships):
    """Save the given diagram."""

    # Ensure ending exists.
    if not name.endswith(".xml"):
        name += ".xml"

    # Do the save.
    try:
        dest = os.path.join(getDiagramsDir(), name)

        # Create XML document.
        doc = xml.Document()
        root = doc.createElement("org-chart")
        doc.appendChild(root)

        # Write persons.
        for person in persons.values():
            element = doc.createElement("item")

            element.setAttribute("id", person["personId"])
            element.setAttribute("name", person["name"])
            element.setAttribute("title", person["title"])

            rect = loads(person["rect"])
            attr = rect["attrs"]

            element.setAttribute("fill_color", attr["fill"])
            element.setAttribute("border_color", person["borderColor"])

            group = loads(person["group"])
            attr = group["attrs"]

            element.setAttribute("x", str(attr["x"]))
            element.setAttribute("y", str(attr["y"]))

            # Save photos.
            for photo in person["photos"]:
                # Copy the photo if required, i.e. if saving the diagram for
                # the first time.
                baseName = os.path.basename(photo)

                destPhotoFilePath = os.path.join(getPhotosDir(name), baseName)
                sourcePhotoFilePath = os.path.join(getPhotosDir(), baseName)

                if destPhotoFilePath != sourcePhotoFilePath:
                    shutil.copy(sourcePhotoFilePath, destPhotoFilePath)

                    # Replace the path in the XML file, too.
                    photo = getPhotosUrlPath(baseName, name)

                # Create element.
                photoElement = doc.createElement("photo")

                # Set attributes.
                photoElement.setAttribute("path", photo)

                # Add photo element to person.
                element.appendChild(photoElement)

            # Add person element to document.
            root.appendChild(element)

        # Write relationships.
        for relationship in relationships:
            element = doc.createElement("relationship")

            element.setAttribute("from", relationship["fromPersonId"])
            element.setAttribute("to", relationship["toPersonId"])
            element.setAttribute("color", relationship["color"])

            root.appendChild(element)

        # Write the XML file.
        outputFile = open(dest, "w")
        outputFile.write(doc.toprettyxml())
        outputFile.close()

        # Determine name.
        diagramName = removeSuffix(name, ".xml")

        # Return status.
        returnData = {
          "diagramName": diagramName,
          "status": "OK"
        }
    except FileNotFoundError as error:
        # Return status.
        returnData = {
          "status": "Failed",
          "problem": str(error)
        }

    return returnData

def getDiagramList():
    try:
        # Get the diagram list.
        fileNames = os.listdir(getDiagramsDir())

        # Remove the "deleted" folder.
        if "deleted" in fileNames:
            fileNames.remove("deleted")

    except FileNotFoundError as error:
        # Print info.
        print(error)
        print("Current path:", os.path.abspath("."))
        print("Root path:", app.root_path)
        print("Instance path:", app.instance_path)

        # Empty list.
        fileNames = []

    # Return.
    return fileNames

def getDiagramListAsJavaScript():
    return "diagramList = [" + quotedList(getDiagramList()) + "];";

def quotedList(lst):
    return ', '.join('"' + item + '"' for item in lst)

def stringToInt(str):
    # Use "float" to handle numbers with decimal points.
    return int(float(str))

def toJavaScriptList(name, lst):
    return name + ": [" + ', '.join('"' + item + '"' for item in lst) + "],\n"

def toJavaScriptProperty(name, value):
    return name + ": '" + value + "',\n";

class Person():

    def __init__(self, personId, x, y, name, title):
        self.personId = personId
        self.x = x
        self.y = y
        self.name = name
        self.title = title

        # Photos list.
        self.photos = []

        # Set fixed height.
        self.height = PERSON_HEIGHT

        # Hack to set width. This should be really done in JavaScript.
        # https://www.w3schools.com/tags/canvas_measuretext.asp
        fontSize = 20
        averageCharWidth = fontSize * 0.55
        self.width = max(PERSON_WIDTH, len(name) * averageCharWidth)

    def addPhoto(self, photo):
        self.photos.append(photo)

    def getCenterX(self):
        return self.x + (self.getWidth() / 2)

    def getCenterY(self):
        return self.y + (self.getHeight() / 2)

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def getRelationshipOriginX(self):
        return self.getCenterX()

    def getRelationshipOriginY(self):
        return self.getCenterY()

    def toJavaScript(self):
        return "{" \
            + toJavaScriptProperty("personId", self.personId) \
            + toJavaScriptProperty("name", self.name) \
            + toJavaScriptProperty("title", self.title) \
            + toJavaScriptList("photos", self.photos) \
            + toJavaScriptProperty("borderColor", self.borderColor) \
            + "}"

def parse_diagram_file(fileName, defaultFileName = None):

    # Make result.
    result = ""

    # Get input file.
    inputFileName = os.path.join(getDiagramsDir(), fileName)
    if defaultFileName:
        defaultInputFileName = os.path.join(getDiagramsDir(), defaultFileName)

    # Read the input file.
    try:
        # Try reading specified diagram.
        doc = xml.parse(inputFileName)
        g.diagramName = fileName
    except IOError as e:
        # Print error.
        print("Could not load specified diagram:")
        print(e)

        if defaultFileName:
            # Load default diagram instead.
            try:
                print("Loading default diagram instead.")
                doc = xml.parse(defaultInputFileName)
                g.diagramName = defaultFileName
            except FileNotFoundError as error:
                # Exit if not found.
                g.toastMessage = "Diagram " + fileName + " not found."
                print(error)
                return result
        else:
            # No default file name, simply return.
            g.toastMessage = "Diagram " + fileName + " not found."
            return result

    # Read the persons.
    personElements = doc.getElementsByTagName("item")

    # Create the list.
    persons = {}

    # Add the persons from the list.
    for element in personElements:

        # Read attributes.
        personId = element.getAttribute("id")
        name = element.getAttribute("name")
        x = stringToInt(element.getAttribute("x"))
        y = stringToInt(element.getAttribute("y"))
        title = element.getAttribute("title")

        # Get text color.
        textColor = 'black' # Default.
        if element.hasAttribute("text_color"):
            textColor = element.getAttribute("text_color")

        # Get border color.
        borderColor = 'black' # Default.
        if element.hasAttribute("border_color"):
            borderColor = element.getAttribute("border_color")

        # Store person.
        person = Person(personId, x, y, name, title)
        person.textColor = textColor
        person.borderColor = borderColor
        persons[personId] = person

        # Read the photos.
        photoElements = element.getElementsByTagName("photo")

        for photoElement in photoElements:
            photoPath = photoElement.getAttribute("path")
            person.addPhoto(photoPath)

    # Draw the persons.
    for person in persons.values():

        # Read values.
        x = person.x
        y = person.y
        name = person.name
        textColor = person.textColor

        # Create the person.
        line = "var person = " + person.toJavaScript() + "\n";
        result += line;

        # Add the person to the diagram.
        line = "addPersonToDiagram(person, " + str(x) + ", " + str(y) + ")\n";
        result += line;

        # Set text color.
        line = "person.text.fill('" + textColor + "');\n";
        result += line;

    # Read the relationships.
    relationshipElements = doc.getElementsByTagName("relationship")

    # Add the relationships from the list.
    for element in relationshipElements:

        # Read from XML.
        if element.hasAttribute("from") and element.hasAttribute("to"):

            # Get persons.
            fromPersonId = element.getAttribute("from")
            toPersonId = element.getAttribute("to")

            # Get color.
            color = 'black' # Default.
            if element.hasAttribute("color"):
                color = element.getAttribute("color")

            # Place arrow.
            fromPerson = persons[fromPersonId]
            toPerson = persons[toPersonId]

            # Draw the line.
            x1 = fromPerson.getRelationshipOriginX()
            y1 = fromPerson.getRelationshipOriginY()
            x2 = toPerson.getCenterX()
            y2 = toPerson.y # Hack to show arrow head.

            # Add the relationship to the diagram.
            args =  ", ".join(str(val) for val in [x1, y1, x2, y2]);
            args += ", " + quotedList([fromPersonId, toPersonId, color]);
            line = "addRelationshipToDiagram(" + args + ");\n";
            result += line;

    # Scroll position.
    if len(persons) > 0:
        scrollX = min(person.x for person in persons.values())
        scrollY = min(person.y for person in persons.values())

        # Hack.
        margin = 16
        toolbarWidth = 150
        stagePositionX = -(scrollX - margin - toolbarWidth)
        stagePositionY = -(scrollY - margin)
        line = "contentsTopLeft = {x:" + str(stagePositionX) + ",y:" + str(stagePositionY) + "};"
        result += line

    # Return.
    return result

def addPhoto(f):
    """Add a photo."""

    # Get the destination directory.
    dir = getPhotosDir()

    # Create it if it does not exist.
    if not os.path.exists(dir):
        os.mkdir(dir)

    # Save the photo file.
    fileName = secure_filename(f.filename)
    filePath = os.path.join(dir, fileName)

    # Try to ensure a unique file name.
    [baseName, extension] = os.path.splitext(fileName)

    for suffix in range(2, 1000):
        if os.path.exists(filePath):
            fileName = baseName + "-" + str(suffix) + extension
            filePath = os.path.join(dir, fileName)
        else:
            break

    # Store the file.
    f.save(filePath)

    # Get the image path.
    relativePath = getPhotosUrlPath(fileName)

    # Return data.
    returnData = {
      "status": "OK",
      "photoPath": relativePath,
      "photoName": fileName
    }

    return returnData

if __name__ == "__main__":
    parse_diagram_file()
