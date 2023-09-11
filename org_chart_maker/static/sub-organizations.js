// -----------------------------------------------------------------------------
// Routines for sub-organizations.
// -----------------------------------------------------------------------------

// Space for icon.
var ICON_SPACE = 42;

// Sub-organizations dictionary.
var subOrgs = {};

// Add sub-org to diagram at the given coordinates.
function addSubOrgToDiagram(org, x, y) {
  // Set size.
  var width = 200; // Math.max(simpleText.width() + 32, 200)
  var height = 50;

  // Calculate group coordinates.
  var groupX = x;
  var groupY = y;

  // Create the group (for drag and drop).
  var group = new Konva.Group({
    x: groupX,
    y: groupY,
    draggable: true,
  });

  // Calculate center.
  var centerX = (width / 2);
  var centerY = (height / 2);

  // Center the text in the box.
  var fontSize = 20;
  var textX = 20;
  var textY = centerY - (fontSize / 2);

  // Create the text element.
  var text = new Konva.Text({
      x: textX,
      y: textY,
      text: org.name,
      fontSize: fontSize,
      fontFamily: 'Calibri',
      fill: 'black',
  });

  // Create the rectangle.
  var rect = new Konva.Rect({
    x: 0,
    y: 0,
    width: width,
    height: height,
    fill: 'white',
    stroke: 'black',
    strokeWidth: 1,
  });

  // Create icon.
  Konva.Image.fromURL("/static/images/sub-org-icon.png", function (imageNode) {
    // Set image attributes.
    imageNode.setAttrs({
      x: width - ICON_SPACE,
      y: 8,
      width: 32,
      height: 32,
    });

    // Add to group.
    group.add(imageNode);

    // Place.
    imageNode.x(org.rect.width() - ICON_SPACE);

    // Set field.
    org.icon = imageNode;
  });

  // Add the shapes to the group.
  group.add(rect);
  group.add(text);

  // Add the group to the layer.
  layer.add(group);

  // Get id.
  var id = org.id;

  // Add to dictionary.
  subOrgs[id] = org;

  // Add click handlers.
  group.on('pointerdblclick', function () {
      showSubOrgDetails(id);
  });

  rect.on('click', function (e) {
    if (diagramMode == DEFAULT) {
      selectSubOrg(org);
      e.cancelBubble = true; // Stop event propogation.
    }
  });

  text.on('click', function (e) {
    if (diagramMode == DEFAULT) {
      selectSubOrg(org);
      e.cancelBubble = true; // Stop event propogation.
    }
  });

  group.on('dragstart', function (e) {
    if (diagramMode == DEFAULT) {
      selectSubOrg(org);
    }
  });

  // TODO: Decide how to use relationships.
  // group.on('mousedown', function (e) {
  //   if (diagramMode == ADD_RELATIONSHIP) {
  //     newRelationshipParent = org;
  //     drawingArrow = true;
  //   }
  // });
  //
  // group.on('mouseup', function (e) {
  //   if (diagramMode == ADD_RELATIONSHIP) {
  //     newRelationshipChild = org;
  //   }
  // });
  //
  // group.on('dragmove', function (e) {
  //   // Move relationships.
  //   updateRelationshipEndPoints(org);
  // });

  // Add pointers to shapes.
  org.rect = rect;
  org.text = text;
  org.group = group;

  // Add relationship list.
  org.relationships = [];

  // Set border color.
  restoreBorderColor(org);

  // Update thumbnail.
  // person.thumbnailBox = null;
  // updateThumbnail(person);

  // Update box to fit name.
  updateSubOrgBoxToFitName(org);

  // Add to tree view.
  // var row = personsTable.insertRow(personsTable.rows.length);
  // var cell = row.insertCell(0);
  // cell.innerHTML = person.name;
  // cell.onclick = function() {
  //   goToPerson(person);
  //   selectPerson(person);
  // }
  // personsTableRows[personId] = row;
}

// Select sub-org.
var selectedSubOrg = null;

// Function to select sub-org.
function selectSubOrg(org) {
  // Deselect previous person.
  selectNone();

  // Select the sub-org.
  selectedSubOrg = org;

  // Highlight the person.
  org.rect.stroke("blue");
  org.rect.strokeWidth(2);
}

// Update box to fit name.
function updateSubOrgBoxToFitName(org) {
  // Constants.
  var MARGIN = 20;

  // Calculate margin.
  var textWidth = org.text.width();
  var textBoxWidth = textWidth + (MARGIN * 2)
  var rectWidth = textBoxWidth + ICON_SPACE;

  // Set width.
  org.rect.width(rectWidth);

  // Center text.
  org.text.x(textBoxWidth / 2 - textWidth / 2);

  // Place icon.
  if (org.icon)
  {
    org.icon.x(rectWidth - ICON_SPACE);
  }
}

// The currently shown sub-org.
var currentSubOrg = null;

// Function to sub-org details.
function showSubOrgDetails(id) {
  // Get person.
  var org = subOrgs[id];

  // Store.
  currentSubOrg = org;

  // Set title.
  $( "#subOrgDetailsDialog" ).dialog( "option", "title", "Sub-Org. details - " + org.name );

  // Add person details.
  document.getElementById("subOrgName").value = org.name;
  document.getElementById("subOrgDiagramId").value = org.diagramId;

  // Show dialog.
  $( "#subOrgDetailsDialog" ).dialog( "open" );

  // Set the dialog to a constant height.
  // $( "#"tabs" ).tabs( "option", "heightStyle", "auto" );
}

// Create a new sub-organization.
function createNewSubOrg(pos) {
  // Create ID.
  var id = Date.now().toString(36) + Math.random().toString(36).substring(2);

  // Create sub-org.
  org = {
      id: id,
      name: "New Sub-Org",
      diagramId: "",
      borderColor: "black",
  };

  // Add to diagram.
  addSubOrgToDiagram(org, pos.x, pos.y);

  // Select it immediately.
  selectSubOrg(org);

  // Debug.
  // console.log("Would create new sub-org...");

  // Reset the mode.
  setDiagramMode (DEFAULT);
}

// Function to save sub-org details.
function saveSubOrgDetails() {
  // Update details.
  currentSubOrg.name = $( "#subOrgName" ).val();
  currentSubOrg.diagramId = $( "#subOrgDiagramId" ).val();

  // Update diagram.
  currentSubOrg.text.text( currentSubOrg.name );
  updateSubOrgBoxToFitName( currentSubOrg );
  // updateFilterStatus( currentSubOrg );

  // updateRelationshipEndPoints(currentSubOrg);

  // Update tree view.
  // personsTableRows[currentPerson.personId].cells[0].innerHTML = currentPerson.name;

  // Close the dialog.
  subOrgDetailsDialog.dialog( "close" );

  // Update undo stack.
  addUndo();
}
