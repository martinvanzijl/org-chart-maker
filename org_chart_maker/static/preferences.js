// -----------------------------------------------------------------------------
// JavaScript for preferences.
// -----------------------------------------------------------------------------

// Function to save preferences and immediately apply to the diagram.
function saveAndApplyPreferences() {
  savePreferences();
  updateDiagramBasedOnPreferences();
}

// Function to save preferences.
function savePreferences() {
  // Use AJAX to ask the server to save the diagram.
  var url = "/savePreferences";

  var params = {};
  if (document.getElementById("text").checked) {
    params["top_menu_type"] = "text";
  }
  else {
    params["top_menu_type"] = "images";
  }

  // TODO: Actually update the menu bar to show text/images as required.
  // Perhaps this is overkill?

  showArrowHeads = document.getElementById("show_arrow_heads").checked;
  params["show_arrow_heads"] = showArrowHeads;

  // Save to server.
  $.post( url, params, function(data, status) {
    // Get AJAX response.
    var jsonReply = data;

    // Check result.
    var replyStatus = jsonReply.status;

    if (replyStatus == "OK") {
      showToastMessage("Preferences saved.");
    }
    else {
      // An error happened.
      alert("Could not save preferences. Details:\n" + jsonReply.problem);
    }
  });
}

// Update diagram based on preferences.
function updateDiagramBasedOnPreferences() {
  console.log("Updating diagram.");
  var arrowSize = showArrowHeads ? diagramProperties.arrowSize : 0;
  setArrowSizes(arrowSize);
}
