// -----------------------------------------------------------------------------
// Routines for setting border color.
// -----------------------------------------------------------------------------

// The previous color.
var previousBorderColor = null;
var previousFillColor = null;

// Show the border color dialog.
function showBorderColorDialog() {
  if (selectedPerson) {
    previousBorderColor = selectedPerson.borderColor;
    previousFillColor = selectedPerson.fillColor;
    $( "#colorpickerHolder" ).ColorPickerSetColor(previousBorderColor);
    $( "#borderColorDialog" ).dialog( "open" );
  }
  else {
    showToastMessage("Please select an item first.");
  }
}

// Save the border color from the dialog.
function saveBorderColor(hex) {
  if (selectedPerson) {
    selectedPerson.borderColor = "#" + hex;
    restoreBorderColor(selectedPerson);
  }
}

// Revert the border color of the selected item.
function revertBorderColor() {
  if (selectedPerson) {
    selectedPerson.borderColor = previousBorderColor;
    restoreBorderColor(selectedPerson);
    borderColorDialog.dialog( "close" );
  }
}

// Save the fill color from the dialog.
function saveFillColor(hex) {
  if (selectedPerson) {
    selectedPerson.fillColor = "#" + hex;
    restoreFillColor(selectedPerson);
  }
}

// Revert the fill color of the selected item.
function revertFillColor() {
  if (selectedPerson) {
    selectedPerson.fillColor = previousFillColor;
    restoreFillColor(selectedPerson);
    borderColorDialog.dialog( "close" );
  }
}
