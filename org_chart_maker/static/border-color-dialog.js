// -----------------------------------------------------------------------------
// Routines for setting border color.
// -----------------------------------------------------------------------------

// The previous color.
var previousBorderColor = null;
var previousFillColor = null;

// Get the selected item.
function getSelectedItem() {
  if (selectedPerson) return selectedPerson; // Person is selected...
  if (selectedSubOrg) return selectedSubOrg; // Sub-org is selected...
  return null; // Nothing is selected...
}

// Show the border color dialog.
function showBorderColorDialog() {
  var selectedItem = getSelectedItem();
  if (selectedItem) {
    previousBorderColor = selectedItem.borderColor;
    previousFillColor = selectedItem.fillColor;
    $( "#colorpickerHolder" ).ColorPickerSetColor(previousBorderColor);
    $( "#borderColorDialog" ).dialog( "open" );
  }
  else {
    showToastMessage("Please select an item first.");
  }
}

// Save the border color from the dialog.
function saveBorderColor(hex) {
  var selectedItem = getSelectedItem();
  if (selectedItem) {
    selectedItem.borderColor = "#" + hex;
    restoreBorderColor(selectedItem);
  }
}

// Revert the border color of the selected item.
function revertBorderColor() {
  var selectedItem = getSelectedItem();
  if (selectedItem) {
    selectedItem.borderColor = previousBorderColor;
    restoreBorderColor(selectedItem);
    borderColorDialog.dialog( "close" );
  }
}

// Save the fill color from the dialog.
function saveFillColor(hex) {
  var selectedItem = getSelectedItem();
  if (selectedItem) {
    selectedItem.fillColor = "#" + hex;
    restoreFillColor(selectedItem);
  }
}

// Revert the fill color of the selected item.
function revertFillColor() {
  var selectedItem = getSelectedItem();
  if (selectedItem) {
    selectedItem.fillColor = previousFillColor;
    restoreFillColor(selectedItem);
    borderColorDialog.dialog( "close" );
  }
}
