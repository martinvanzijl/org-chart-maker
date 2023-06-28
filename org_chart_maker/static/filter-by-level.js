// -----------------------------------------------------------------------------
// JavaScript for filtering people by level.
// -----------------------------------------------------------------------------

// A temporary map to store the depth of each person.
// static QMap<DiagramItem *, int> m_depthMap; // C++
var m_depthMap = {};

//
// Get the "depth" of the person, i.e. how many layers of descendants they have.
//
// static int getDepth(DiagramItem *person) { // C++
function getDepth(person) {
    // Check if depth already calculated.
    // if (m_depthMap.contains(person)) { // C++
    if (person in m_depthMap)
        return m_depthMap[person];
    }

    // Get maximum depth of parents.
    // QList<DiagramItem *> children = person->getChildren(); // C++
    var children = person.getChildren();

    var maxChildDepth = -1;
    // for (DiagramItem *child: children) { // C++
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
    m_depthMap[person] = personDepth;

    // Return.
    return personDepth;
}

// Automatically lay out the given row of persons at the given Y coordinate.
// int DiagramScene::autoLayoutRow(const QList<DiagramItem *> &items, int startY) { // C++
function autoLayoutRow(items, startY) {
    var startX = 128;

    var x = startX;
    var y = startY;

    var horizontalSpacing = 16;
    var verticalSpacing = 16;

    // Lay out each item in the row.
    // for (auto item: items) { // C++
    for (var index in items) {
        // Get the person.
        var person = items[index];
        // DiagramItem *person = qgraphicsitem_cast<DiagramItem*> (item); // C++

        // Place the person.
        // person->setPos(x, y); // C++
        person.setPos(x, y);

        // Prepare the next position.
        // x += person->getWidthIncludingSpouse() + horizontalSpacing; // C++
        x += person.getWidth() + horizontalSpacing;

        // Wrap to next line if required.
        // if (x > sceneRect().right()) {
        if (x > scene.right()) {
            // y += person->boundingRect().height() + verticalSpacing;
            y += person.getHeight() + verticalSpacing;
            x = startX;
        }
    }

    return y;
}

// Automatically layout the diagram.
function autoLayout()
{
    // Clear depth map.
    // m_depthMap.clear(); // C++
    m_depthMap = {};

    // Set up map of depth to persons.
    // QMultiMap<int, DiagramItem* > depthMultiMap; // C++
    var depthMultiMap = {};

    // Find the right depth for each person.
    // for (auto item: items()) { // C++
    for (var index in persons) {
        var person = persons[index];
        // if (item->type() == DiagramItem::Type) { // C++
            // DiagramItem *person = qgraphicsitem_cast<DiagramItem*> (item); // C++

            var depth = getDepth(person);
            if (!(depth in depthMultiMap)) {
              depthMultiMap[depth] = [];
            }
            // depthMultiMap.insert(depth, person); // C++
            depthMultiMap[depth].push(person);
        // } // C++
    }

    // Get maximum depth.
    // auto maxDepth = depthMultiMap.lastKey(); // C++
    var maxDepth = getLastKey(depthMultiMap);

    // Place the persons.
    var y = 64;

    for (var depth = maxDepth; depth >= 0; --depth) {
        // y = autoLayoutRow(depthMultiMap.values(depth), y); // C++
        y = autoLayoutRow(depthMultiMap[depth], y);
        y += 256;
    }
}

// Get the last key in the given dictionary.
function getLastKey(dict) {
  var lastKey = null;

  for (var key in dict) {
      lastKey = key;
  }

  return lastKey;
}
