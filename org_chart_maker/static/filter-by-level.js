// -----------------------------------------------------------------------------
// JavaScript for filtering people by level.
// -----------------------------------------------------------------------------

// Get the diagram width.
function getDiagramWidth() {
  // Hack!
  return 5000;
}

// Move the given person to the given position.
function setPersonPos(person, x, y) {
  person.group.x(x);
  person.group.y(y);

  updateRelationshipEndPoints(person);
}

// Get the width of a person.
function getPersonWidth(person) {
  return person.rect.width();
}

// Return the "children" of the given person.
function getChildren(person) {
  var children = [];

  for (var index in person.relationships) {
    var relationship = person.relationships[index];

    if (relationship.fromPersonId == person.personId) {
      var child = persons[relationship.toPersonId];
      children.push(child);
    }
  }

  return children;
}

// A temporary map to store the depth of each person.
var m_depthMap = {};

//
// Get the "depth" of the person, i.e. how many layers of descendants they have.
//
function getDepth(person) {
    // Check if depth already calculated.
    if (person in m_depthMap) {
        return m_depthMap[person.personId];
    }

    // Get maximum depth of parents.
    var children = getChildren(person);

    var maxChildDepth = -1;
    for (var index in children) {
        var child = children[index];
        var childDepth = getDepth(child);
        if (childDepth > maxChildDepth) {
            maxChildDepth = childDepth;
        }
    }

    // Add one.
    var personDepth = maxChildDepth + 1;

    // Add to map.
    m_depthMap[person.personId] = personDepth;

    // Return.
    return personDepth;
}

// Automatically lay out the given row of persons at the given Y coordinate.
function autoLayoutRow(items, startY) {
    var startX = 128;

    var x = startX;
    var y = startY;

    var horizontalSpacing = 16;
    var verticalSpacing = 16;

    // Lay out each item in the row.
    for (var index in items) {
        // Get the person.
        var person = items[index];

        // Place the person.
        setPersonPos(person, x, y);

        // Prepare the next position.
        x += getPersonWidth(person) + horizontalSpacing;

        // Wrap to next line if required.
        if (x > getDiagramWidth()) {
            y += person.getHeight() + verticalSpacing;
            x = startX;
        }
    }

    return y;
}

// Automatically layout the diagram.
function autoLayout()
{
    autoLayoutItems(persons);
}

// Automatically layout the given persons.
function autoLayoutItems(personList)
{
    // Clear depth map.
    m_depthMap = {};

    // Set up map of depth to persons.
    var depthMultiMap = {};

    // Find the right depth for each person.
    for (var index in personList) {
        var person = personList[index];
        var depth = getDepth(person);
        if (!(depth in depthMultiMap)) {
            depthMultiMap[depth] = [];
        }
        depthMultiMap[depth].push(person);
    }

    // Get maximum depth.
    var maxDepth = getLastKey(depthMultiMap);

    // Place the persons.
    var y = 64;

    for (var depth = maxDepth; depth >= 0; --depth) {
        y = autoLayoutRow(depthMultiMap[depth], y);
        // y += 256; // Too much.
        // y += 128; // Too little.
        y += 160;
    }

    // Hide the menu.
    hideActiveMenu();
}

// Get the last key in the given dictionary.
function getLastKey(dict) {
  var lastKey = null;

  for (var key in dict) {
      lastKey = key;
  }

  return lastKey;
}
