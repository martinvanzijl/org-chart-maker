// -----------------------------------------------------------------------------
// Routines for importing CSV files.
// -----------------------------------------------------------------------------

// Import the selected CSV file.
// function importSelectedCsvFile() {
//   // Debug.
//   console.log("Importing selected CSV file...");
//
//   // Get fields.
//   var fileName = document.getElementById("import_csv_input").value;
//   console.log("File name:", fileName);
//
//   // TODO:
//   // Set form target to Python method: import_csv_file.
// }

// Add CSV data to the diagram.
function addCsvDataToDiagram (data) {

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
    var reportsTo = row[4];

    // Create ID.
    var personId = createPersonId();

    // Create person.
    person = {
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

    // TODO: Avoid laying out the whole diagram.
    autoLayout();
  }
}
