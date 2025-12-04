// -----------------------------------------------------------------------------
// Routines for importing CSV files.
// -----------------------------------------------------------------------------

// Add CSV data to the diagram.
function addCsvDataToDiagram (data) {

  // Create relationships list.
  var relationships = {}; // [Employee] --> "Manager"
  var nameToPerson = {};
  var personList = {};

  // Flag.
  var csvIncludesCoordinates = false;

  // Go through persons.
  for (var index in data.persons) {
    // Skip header row.
    if (index == 0) {
      continue;
    }

    // Get row.
    var row = data.persons[index];

    // Get fields.
    var name = row[0];
    var title = row[1];
    var url = row[2];
    var department = row[3];
    var reportsToName = row[4];

    // Get the X and Y coordinates if available.
    var pos = {x: 0, y: 0};

    if (row.length >= 7) {
      pos = {x: parseInt(row[5]), y: parseInt(row[6])};

      csvIncludesCoordinates = true;
    }

    // Create ID.
    var personId = createPersonId();

    // Create person.
    var person = {
        personId: personId,
        name: name,
        title: title,
        url: url,
        department: department,
        photos: [],
        activePhotoIndex: 0,
        borderColor: "black",
        fillColor: "white",
    };

    // Add to list.
    personList[personId] = person;

    // Set position.
    // var pos = {x: 0, y: 0};

    // Add to diagram.
    addPersonToDiagram(person, pos.x, pos.y);

    // Note relationship.
    nameToPerson[name] = person;

    if (reportsToName) {
      relationships[personId] = reportsToName;
    }
  }

  // Go through relationships.
  for (var personId in relationships) {
    // Get row.
    var reportsToName = relationships[personId];

    // Get fields.
    var employee = persons[personId];
    var manager = nameToPerson[reportsToName];

    // Create relationship.
    addRelationshipToDiagram(0, 0, 0, 0, employee, manager, 'black', SOLID);
  }

  // TODO: Skip this step if the positions are specified in the CSV file.
  // Layout the added persons.
  if (!csvIncludesCoordinates) {
    autoLayoutItems(personList);
  }

  // Update undo stack.
  addUndo(new ImportCSVUndo(personList));
}
