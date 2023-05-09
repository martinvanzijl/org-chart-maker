from flask import Blueprint
from flask import current_app as app
from flask import flash
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session
from flask import url_for
from flask.json import loads
from werkzeug.exceptions import abort

from org_chart_maker.auth import login_required
from org_chart_maker.db import get_db

import diagram_reader
import os
import tempfile

# Set up logging.
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up web app.
from org_chart_maker.utils import register_new_users_allowed

bp = Blueprint("diagram_editor", __name__)

def get_diagram_list():
    # Result.
    result = ""

    # Get the diagram list.
    fileNames = diagram_reader.getDiagramList()

    # Push onto dialog.
    for fileName in fileNames:
        diagramId = os.path.splitext(fileName)[0]
        html = '<a href="/?diagram=' + diagramId + '"><p>' + diagramId + '</p></a>'
        result += """$( "#openOrgChartDialog" ).append('""" + html + """');\n"""

    # Return.
    return result

# TODO: Use a different URL for the "POST" method.
@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    """Show the diagram editor."""

    # Check for file upload.
    if request.method == "POST":
        if "uploaded_file" not in request.files:
            print("POST used but no file uploaded.")
        else:
            # Get file object.
            f = request.files["uploaded_file"]

            # Set save file name.
            saveFileName = f.filename

            # Save the file.
            # TODO: Save under the username (directory).
            f.save(os.path.join(diagram_reader.getDiagramsDir(), saveFileName))

            # Redirect to the view the new file.
            diagramId = os.path.splitext(saveFileName)[0]
            return redirect("/?diagram=" + diagramId)

    # If the user is logged in, redirect to "new".
    if g.user and not request.args.get('diagram'):
        return redirect("/new")

    # Get the desired diagram.
    diagram = request.args.get('diagram', 'example-org-chart')
    diagramFileName = diagram + ".xml"

    # Read diagram.
    if g.user:
        defaultDiagramFileName = None
    else:
        defaultDiagramFileName = "example-org-chart.xml"
    canvasContent = get_diagram_list() # TODO: Add these directly into the HTML template, instead of JavaScript.

    try:
        canvasContent += diagram_reader.parse_diagram_file(diagramFileName, defaultDiagramFileName)
    except ValueError as error:
        # Message to user.
        g.toastMessage = "Could not load diagram: (" + str(error) + ")"
        # Message to developer.
        logger.exception(error)
        # Clear name.
        g.diagramName = None

    # Pass flag to template.
    g.allow_register_new_users = register_new_users_allowed()

    # Pass scroll position.
    g.scrollLeft = request.args.get('scrollLeft', None)
    g.scrollTop = request.args.get('scrollTop', None)

    # Pass flag to show "saved" message.
    if 'showSavedMessageOnLoad' in session:
        g.showSavedMessageOnLoad = (session['showSavedMessageOnLoad'] == "true")
        session.pop('showSavedMessageOnLoad', None)
    else:
        g.showSavedMessageOnLoad = False

    # Get templates.
    g.templatesList = diagram_reader.getTemplateList();

    # Render web page.
    return render_template("diagram_editor/index.html", canvasContent=canvasContent)

@bp.route("/new", methods=("GET",))
@login_required
def new():
    """Create a new diagram."""

    # Get canvas content.
    canvasContent  = get_diagram_list() # TODO: Add these directly into the HTML template, instead of JavaScript.
    # canvasContent += "persons = {};\n"

    # Pass flag to template.
    g.allow_register_new_users = register_new_users_allowed()

    # Load template if specified.
    template = request.args.get('template')
    if template:
        try:
            canvasContent += diagram_reader.parse_template_file(template)
        except ValueError as error:
            # Message to user.
            g.toastMessage = "Could not load template: (" + str(error) + ")"
            # Message to developer.
            logger.exception(error)

    # Get templates.
    g.templatesList = diagram_reader.getTemplateList();

    # Render web page.
    return render_template("diagram_editor/index.html", canvasContent=canvasContent)

@bp.route("/manage", methods=("GET",))
@login_required
def manage():
    """Show the screen to manage diagrams."""

    diagramList = diagram_reader.getDiagramListAsJavaScript()
    return render_template("diagram_editor/manage.html", diagramList=diagramList)

@bp.route("/preferences", methods=("GET",))
@login_required
def preferences():
    """Show the screen to manage preferences."""

    return render_template("diagram_editor/preferences.html")

@bp.route("/rename", methods=("POST",))
def rename_diagram():
    """Rename a diagram."""

    # Read parameters.
    diagram = request.form.get('diagram')
    newName = request.form.get('name')

    # Do the rename.
    content = diagram_reader.rename(diagram, newName)
    return jsonify(content)

@bp.route("/delete", methods=("POST",))
def delete_diagram():
    """Delete a diagram."""

    # Read parameters.
    diagram = request.form.get('diagram')

    # Do the delete.
    diagram_reader.delete(diagram)

    # Content.
    content = "<p>Diagram deleted.</p>"
    return content

@bp.route("/save", methods=("POST",))
def save_diagram():
    """Save a diagram."""

    # Read parameters.
    name = request.form.get('name')
    persons = request.form.get('persons')
    relationships = request.form.get('relationships')
    session['showSavedMessageOnLoad'] = request.form.get('showSavedMessageOnLoad')

    # Load from JSON.
    pd = loads(persons)
    rd = loads(relationships)

    # Do the save.
    content = diagram_reader.save(name, pd, rd)
    return jsonify(content)

@bp.route("/exportToCSV", methods=("POST",))
def export_to_csv():
    """Export a diagram to a CSV file."""

    # Read parameters.
    name = request.form.get('name')
    persons = request.form.get('persons')
    relationships = request.form.get('relationships')

    # Load from JSON.
    pd = loads(persons)
    rd = loads(relationships)

    # Do the save.
    content = diagram_reader.export_to_csv(name, pd, rd)
    return jsonify(content)

@bp.route("/exportToXML", methods=("POST",))
def export_to_xml():
    """Export a diagram to an XML file."""

    # Read parameters.
    name = request.form.get('name')
    persons = request.form.get('persons')
    relationships = request.form.get('relationships')

    # Load from JSON.
    pd = loads(persons)
    rd = loads(relationships)

    # Do the export.
    content = diagram_reader.export_to_xml(name, pd, rd)
    print ("Content:", content)
    return jsonify(content)

@bp.route("/savePreferences", methods=("POST",))
def save_preferences():
    """Save preferences."""

    # Read parameters.
    top_menu_type = request.form.get('top_menu_type')

    type_id = 0;
    if top_menu_type == "images":
        type_id = 1;

    # Update database.
    db = get_db()

    db.execute(
        "UPDATE user SET top_menu_type = ? WHERE id = ?",
        (type_id, g.user["id"])
    )
    db.commit()

    # Return.
    content = {"status": "OK"};
    return jsonify(content)

@bp.route("/downloadCSV", methods=("GET",))
def download_csv():
    """Download a CSV file."""

    filename = request.args.get('filename')
    directory = os.path.join(app.root_path, "..", "csv_exports")
    return send_from_directory(directory=directory, filename=filename)

@bp.route("/add_photo", methods=("POST",))
def add_photo():
    """Add a photo to a diagram."""

    # Get file object.
    f = request.files["photoToAdd"]

    # Save the file.
    content = diagram_reader.addPhoto(f)

    # Return the data.
    return jsonify(content)
