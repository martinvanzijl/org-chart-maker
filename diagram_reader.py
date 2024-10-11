#!/usr/bin/python3

import csv
import datetime
from flask import current_app as app
from flask import g, url_for
from flask.json import loads
import os
import shutil
import tempfile
import uuid
from org_chart_maker.utils import removeSuffix
from werkzeug.utils import secure_filename
import xml.dom.minidom as xml
import zipfile

PERSON_WIDTH = 200
PERSON_HEIGHT = 50

DIAGRAMS_DIR = "save-files";
PHOTOS_DIR_NAME = "photos";

# Based on https://stackoverflow.com/a/670635
def addFolderToZip(zip_file, source_folder, folder_in_zip_file):
    for file_name in os.listdir(source_folder):
        source_path = os.path.join(source_folder, file_name)
        if os.path.isfile(source_path):
            print ('File added: ', str(file_name))
            dest_path = os.path.join(folder_in_zip_file, file_name)
            zip_file.write(source_path, dest_path)
        # elif os.path.isdir(full_path):
        #     print 'Entering folder: ' + str(full_path)
        #     addFolderToZip(zip_file, full_path)

def removeExtension(fileName, extension):
    """Remove the extension from the given file name."""

    if fileName.endswith(extension):
        return fileName[:-len(extension)]

    # Default case.
    return fileName

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

def getTemplatesDir():
    """Get the folder for templates."""

    # TODO: Perhaps move this to the "instance" dir.
    return os.path.join(app.root_path, "..", "templates")

def getExportedFilesDir():
    """Get the folder for exported files."""

    # TODO: Perhaps move this to the "instance" dir.
    return os.path.join(app.root_path, "..", "csv_exports")

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

def getUserTemplatesDir():
    """Get the folder for the templates of the current user."""

    # Calculate the directory.
    diagramsDir = getDiagramsDir()
    templatesDir = os.path.join(diagramsDir, "templates")

    # Ensure the directory exists.
    if not os.path.exists(templatesDir):
        os.mkdir(templatesDir)

    # Return it.
    return templatesDir

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

def deleteUserTemplate(diagram):
    # Append timestamp to deleted file name.
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")

    # Determine destination.
    source = os.path.join(getUserTemplatesDir(), diagram)
    dest = os.path.join(getUserTemplatesDir(), "deleted")

    # Create "deleted" directory if it does not exist.
    if not os.path.exists(dest):
        os.mkdir(dest)

    # Move the file.
    destFileName = os.path.join(dest, diagram)
    if os.path.exists(destFileName):
        os.remove(destFileName)
    shutil.move(source, dest)

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

def renameUserTemplate(diagram, newName):
    # Ensure ending exists.
    if not newName.endswith(".xml"):
        newName += ".xml"

    # Do the rename.
    try:
        source = os.path.join(getUserTemplatesDir(), diagram)
        dest = os.path.join(getUserTemplatesDir(), newName)
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

def createXmlDoc(persons, relationships, subOrgs, name, diagramProperties):
    """Create an XML document object from the given persons and relationships."""

    doc = xml.Document()
    root = doc.createElement("org-chart")
    doc.appendChild(root)

    # Write properties.
    for key in diagramProperties:
        value = diagramProperties[key]
        root.setAttribute(key, str(value))

    # Write persons.
    for person in persons.values():
        element = doc.createElement("item")

        element.setAttribute("id", person["personId"])
        element.setAttribute("name", person["name"])
        element.setAttribute("title", person["title"])

        try:
            element.setAttribute("url", person["url"])
        except KeyError:
            element.setAttribute("url", "")

        try:
            element.setAttribute("department", person["department"])
        except KeyError:
            element.setAttribute("department", "")

        try:
            element.setAttribute("active_photo_index", person["activePhotoIndex"])
        except KeyError:
            element.setAttribute("active_photo_index", 0)

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
        element.setAttribute("type", relationship["type"])

        root.appendChild(element)

    # Write sub-organizations.
    for subOrg in subOrgs.values():
        element = doc.createElement("subOrg")

        element.setAttribute("id", subOrg["id"])
        element.setAttribute("name", subOrg["name"])
        element.setAttribute("diagramId", subOrg["diagramId"])

        if "borderColor" in subOrg:
            element.setAttribute("border_color", subOrg["borderColor"])

        group = loads(subOrg["group"])
        attr = group["attrs"]

        # TODO: Convert to integers first.
        element.setAttribute("x", str(attr["x"]))
        element.setAttribute("y", str(attr["y"]))

        root.appendChild(element)

    # Return.
    return doc

def save(name, persons, relationships, subOrgs, diagramProperties, overwrite = True):
    """Save the given diagram."""

    # Ensure ending exists.
    if not name.endswith(".xml"):
        name += ".xml"

    # Check if diagram exists already.
    if overwrite == "false":
        existingNames = getDiagramList()
        if name in existingNames:
            return {
              "status": "Failed",
              "problem": "A diagram of the same name already exists."
            }

    # Do the save.
    try:
        dest = os.path.join(getDiagramsDir(), name)

        # Create XML document.
        doc = createXmlDoc(persons, relationships, subOrgs, name, diagramProperties)

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

def saveTemplate(name, persons, relationships, subOrgs, diagramProperties):
    """Save the given template."""

    # Ensure ending exists.
    if not name.endswith(".xml"):
        name += ".xml"

    # Do the save.
    try:
        dest = os.path.join(getUserTemplatesDir(), name)

        # Create XML document.
        doc = createXmlDoc(persons, relationships, subOrgs, name, diagramProperties)

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

        # Debug.
        print("Template saved as:", dest)

    except FileNotFoundError as error:
        # Return status.
        returnData = {
          "status": "Failed",
          "problem": str(error)
        }

    return returnData

def export_to_csv(name, persons, relationships, subOrgs):
    """Export the given diagram to a CSV file."""

    # Handle new diagram.
    if name == "": name = "new-diagram"

    # Make file name.
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    basename = removeExtension(name, ".xml")
    outputFileName = basename + "-" + timestamp + ".csv";

    # Export.
    try:
        # Get destination file name.
        dest = os.path.join(getExportedFilesDir(), outputFileName);

        # Create CSV document.
        with open(dest, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name', 'Title', 'URL', 'Department', 'Reports To']);

            # Read relationships.
            reportsTo = {};
            for relationship in relationships:
                managerId = relationship["fromPersonId"];
                employeeId = relationship["toPersonId"];
                try:
                    # Person.
                    reportsTo[employeeId] = persons[managerId]["name"];
                except KeyError:
                    # Sub-org.
                    reportsTo[employeeId] = subOrgs[managerId]["name"];

            # Write persons.
            for person in persons.values():
                row = [person["name"], person["title"], person["url"], person["department"]];

                personId = person["personId"];
                if personId in reportsTo:
                    row.append(reportsTo[personId]);
                else:
                    row.append("");

                writer.writerow(row);

            # Write persons.
            for subOrg in subOrgs.values():
                row = ["(sub-org) " + subOrg["name"], "", "", ""];

                id = subOrg["id"];
                if id in reportsTo:
                    row.append(reportsTo[id]);
                else:
                    row.append("");

                writer.writerow(row);

        # Return status.
        returnData = {
          # "dataURL": dest,
          "dataURL": "downloadCSV?filename=" + outputFileName,
          "downloadFileName": outputFileName,
          "status": "OK"
        };
    except FileNotFoundError as error:
        # Return status.
        returnData = {
          "status": "Failed",
          "problem": str(error)
        };

    return returnData;

def export_to_xml(name, persons, relationships, subOrgs, diagramProperties):
    """Export the given diagram to a XML file."""

    # Handle new diagram.
    if name == "": name = "new-diagram"

    # Create XML document.
    doc = createXmlDoc(persons, relationships, subOrgs, name, diagramProperties)

    # Make file name.
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    basename = removeExtension(name, ".xml")
    outputFileName = basename + "-" + timestamp + ".xml"

    # Write the XML file.
    dest = os.path.join(getExportedFilesDir(), outputFileName);
    outputFile = open(dest, "w")
    outputFile.write(doc.toprettyxml())
    outputFile.close()

    # Return.
    returnData = {
      "dataURL": "downloadCSV?filename=" + outputFileName,
      "downloadFileName": outputFileName,
      "status": "OK"
    }

    return returnData

def export_to_zip_file(name, persons, relationships, subOrgs, diagramProperties):
    """Export the given diagram to a zip file."""

    # Handle new diagram.
    if name == "": name = "new-diagram"

    # Create XML document.
    doc = createXmlDoc(persons, relationships, subOrgs, name, diagramProperties)

    # Make file name.
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    basename = removeExtension(name, ".xml")
    xmlFileName = basename + "-" + timestamp + ".xml"

    # Write the XML file.
    xmlFilePath = os.path.join(getExportedFilesDir(), xmlFileName);
    outputFile = open(xmlFilePath, "w")
    outputFile.write(doc.toprettyxml())
    outputFile.close()

    # TODO: Add photos.
    photosDirPath = getPhotosDir(name)
    print ("Photos dir path:", photosDirPath)

    # Place all in zip file.
    zipFileName = basename + "-" + timestamp + ".zip"
    zipFilePath = os.path.join(getExportedFilesDir(), zipFileName);
    zip = zipfile.ZipFile(zipFilePath, "w", zipfile.ZIP_DEFLATED)
    zip.write(xmlFilePath, xmlFileName)

    if os.path.exists(photosDirPath):
        #zip.write(photosDirPath, "photos")
        addFolderToZip(zip, photosDirPath, "photos")

    zip.close()

    # Return.
    returnData = {
      "dataURL": "downloadCSV?filename=" + zipFileName,
      "downloadFileName": zipFileName,
      "status": "OK"
    }

    return returnData

def getDiagramList():
    try:
        # Get the diagram list.
        fileNames = os.listdir(getDiagramsDir())

        # Remove the "deleted" folder.
        if "deleted" in fileNames:
            fileNames.remove("deleted")

        # Remove the "templates" folder.
        if "templates" in fileNames:
            fileNames.remove("templates")

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

def getUserTemplateListAsJavaScript():
    return "diagramList = [" + quotedList(getUserTemplateList()) + "];";

def quotedList(lst):
    return ', '.join('"' + item + '"' for item in lst)

def stringToInt(str):
    # Use "float" to handle numbers with decimal points.
    try:
        return int(float(str))
    except ValueError as error:
        print(error)
        return 0

def toJavaScriptList(name, lst):
    return name + ": [" + ', '.join('"' + item + '"' for item in lst) + "],\n"

def toJavaScriptProperty(name, value):
    return name + ": '" + str(value) + "',\n";

class Item():
    """Base class for person and sub-org."""

    def __init__(self, name):
        # Set fixed height.
        self.height = PERSON_HEIGHT

        # Hack to set width. This should be really done in JavaScript.
        # https://www.w3schools.com/tags/canvas_measuretext.asp
        fontSize = 20
        averageCharWidth = fontSize * 0.55
        self.width = max(PERSON_WIDTH, len(name) * averageCharWidth)

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

class Person(Item):

    def __init__(self, personId, x, y, name, title, url, department):
        Item.__init__(self, name)

        self.personId = personId
        self.x = x
        self.y = y
        self.name = name
        self.title = title
        self.url = url
        self.department = department

        # Photos list.
        self.photos = []

    def addPhoto(self, photo):
        self.photos.append(photo)

    def toJavaScript(self):
        return "{" \
            + toJavaScriptProperty("personId", self.personId) \
            + toJavaScriptProperty("name", self.name) \
            + toJavaScriptProperty("title", self.title) \
            + toJavaScriptProperty("url", self.url) \
            + toJavaScriptProperty("department", self.department) \
            + toJavaScriptList("photos", self.photos) \
            + toJavaScriptProperty("activePhotoIndex", self.activePhotoIndex) \
            + toJavaScriptProperty("borderColor", self.borderColor) \
            + toJavaScriptProperty("fillColor", self.fillColor) \
            + "}"

class SubOrg(Item):

    def __init__(self, id, x, y, name, diagramId):
        Item.__init__(self, name)

        self.id = id
        self.x = x
        self.y = y
        self.name = name
        self.diagramId = diagramId

    def toJavaScript(self):
        return "{" \
            + toJavaScriptProperty("id", self.id) \
            + toJavaScriptProperty("name", self.name) \
            + toJavaScriptProperty("diagramId", self.diagramId) \
            + toJavaScriptProperty("borderColor", self.borderColor) \
            + "}"

def getTemplateList():
    """Get the list of template diagrams."""

    fileNames = []

    try:
        fileNames += os.listdir(getTemplatesDir())
    except FileNotFoundError as error:
        print(error)

    return fileNames

def getUserTemplateList():
    """Get the list of custom template diagrams."""

    fileNames = []

    try:
        fileNames += os.listdir(getUserTemplatesDir())

        # Remove the "deleted" folder.
        if "deleted" in fileNames:
            fileNames.remove("deleted")

    except FileNotFoundError as error:
        print(error)

    return fileNames

def parse_template_file(fileName, isUserTemplate):
    """Parse a template file."""

    if isUserTemplate:
        templateDir = getUserTemplatesDir()
    else:
        templateDir = getTemplatesDir()

    inputFileName = os.path.join(templateDir, fileName)

    try:
        doc = xml.parse(inputFileName)
        return parse_xml_doc(doc)
    except IOError as e:
        print("Could not load specified template:")
        print(e)

    return None

def parse_diagram_file(fileName, defaultFileName = None):
    """Parse a saved diagram file."""

    # Get input file.
    inputFileName = os.path.join(getDiagramsDir(), fileName)
    if defaultFileName:
        defaultInputFileName = os.path.join(getDiagramsDir(), defaultFileName)

    # Read the input file.
    try:
        # Try reading specified diagram.
        doc = xml.parse(inputFileName)
        g.diagramName = fileName
        g.diagramTitle = removeExtension(fileName, ".xml")
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
                g.diagramTitle = removeExtension(defaultFileName, ".xml")
            except FileNotFoundError as error:
                # Exit if not found.
                g.toastMessage = "Diagram " + fileName + " not found."
                print(error)
                return ""
        else:
            # No default file name, simply return.
            g.toastMessage = "Diagram " + fileName + " not found."
            return ""

    # Parse the document.
    return parse_xml_doc(doc)

def parse_xml_doc(doc):
    """Parse a diagram document object."""

    # Make result.
    result = ""

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
        url = element.getAttribute("url")
        department = element.getAttribute("department")

        # Get active photo index.
        activePhotoIndex = 0 # Default.
        if element.hasAttribute("active_photo_index"):
            activePhotoIndex = stringToInt(element.getAttribute("active_photo_index"))

        # Get text color.
        textColor = 'black' # Default.
        if element.hasAttribute("text_color"):
            textColor = element.getAttribute("text_color")

        # Get border color.
        borderColor = 'black' # Default.
        if element.hasAttribute("border_color"):
            borderColor = element.getAttribute("border_color")

        # Get fill color.
        fillColor = 'white' # Default.
        if element.hasAttribute("fill_color"):
            fillColor = element.getAttribute("fill_color")

        # Store person.
        person = Person(personId, x, y, name, title, url, department)
        person.activePhotoIndex = activePhotoIndex
        person.textColor = textColor
        person.borderColor = borderColor
        person.fillColor = fillColor
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

    # Read the persons.

    # Read the sub-organizations.
    subOrgElements = doc.getElementsByTagName("subOrg")
    subOrgs = {}

    for element in subOrgElements:

        # Read attributes.
        id = element.getAttribute("id")
        name = element.getAttribute("name")
        x = stringToInt(element.getAttribute("x"))
        y = stringToInt(element.getAttribute("y"))
        diagramId = element.getAttribute("diagramId")

        # Get border color.
        borderColor = 'black' # Default.
        if element.hasAttribute("border_color"):
            borderColor = element.getAttribute("border_color")

        # Get fill color.
        fillColor = 'white' # Default.
        if element.hasAttribute("fill_color"):
            fillColor = element.getAttribute("fill_color")

        # Store person.
        subOrg = SubOrg(id, x, y, name, diagramId)
        subOrg.borderColor = borderColor
        subOrg.fillColor = fillColor
        subOrgs[id] = subOrg

        # Create in JavaScript.
        line = "var subOrg = " + subOrg.toJavaScript() + "\n";
        result += line;

        # Add the person to the diagram.
        line = "addSubOrgToDiagram(subOrg, " + str(x) + ", " + str(y) + ")\n";
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

            # Get type.
            type = 'solid' # Default.
            if element.hasAttribute("type"):
                type = element.getAttribute("type")

            # Place arrow.
            try:
                fromPerson = persons[fromPersonId]
            except KeyError:
                fromPerson = subOrgs[fromPersonId]

            try:
                toPerson = persons[toPersonId]
            except KeyError:
                toPerson = subOrgs[toPersonId]

            # Draw the line.
            x1 = fromPerson.getRelationshipOriginX()
            y1 = fromPerson.getRelationshipOriginY()
            x2 = toPerson.getCenterX()
            y2 = toPerson.y # Hack to show arrow head.

            # Add the relationship to the diagram.
            args =  ", ".join(str(val) for val in [x1, y1, x2, y2]);
            args += ", getFromID('" + fromPersonId + "'), getFromID('" + toPersonId + "')"
            args += ", " + quotedList([color, type]);
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

    # Read diagram properties.
    root = doc.documentElement
    organization = root.getAttribute("name")
    location = root.getAttribute("location")
    arrowSize = root.getAttribute("arrowSize")
    result += 'diagramProperties.name = "' + organization + '";'
    result += 'diagramProperties.location = "' + location + '";'
    result += 'diagramProperties.arrowSize = "' + arrowSize + '";'
    result += "updateDiagramBasedOnProperties();"

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

def import_from_csv(inputFile):
    """Import a diagram from the given CSV file."""

    # Read file contents.
    content = inputFile.read().decode().split('\n')
    reader = csv.reader(content)

    # Create the list.
    persons = []

    # Go through each row.
    for row in reader:

        # Skip empty rows.
        if len(row) < 5:
            # print("Skipping row...")
            continue

		# Store person in list.
        person = row
        persons.append(person)

    # Return data.
    returnData = {
      "status": "OK",
      "persons": persons
    }

    return returnData

if __name__ == "__main__":
    parse_diagram_file()
