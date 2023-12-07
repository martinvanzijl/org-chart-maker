// -----------------------------------------------------------------------------
// Routines for importing CSV files.
// -----------------------------------------------------------------------------

// Import the selected CSV file.
function importSelectedCsvFile() {
  // Debug.
  console.log("Importing selected CSV file...");

  // Get fields.
  var fileName = document.getElementById("import_csv_input").value;
  console.log("File name:", fileName);

  // TODO:
  // Set form target to Python method: import_csv_file.
}

// Add CSV data to the diagram.
function addCsvDataToDiagram (data) {
  console.log("Adding CSV data...");
}
