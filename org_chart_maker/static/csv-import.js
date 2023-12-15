// -----------------------------------------------------------------------------
// Routines for importing CSV files.
// -----------------------------------------------------------------------------

// Add CSV data to the diagram.
function addCsvDataToDiagram (data) {

  // Create relationships list.
  var relationships = {}; // [Employee] --> "Manager"
  var nameToPerson = {};

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
    };

    // Set position.
    var pos = {x: 0, y: 0};

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

  // TODO: Avoid laying out the whole diagram.
  autoLayout();
}
