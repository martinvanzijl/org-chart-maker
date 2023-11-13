// -----------------------------------------------------------------------------
// JavaScript for preferences.
// -----------------------------------------------------------------------------

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

  showArrowHeads = document.getElementById("show_arrow_heads").checked;
  params["show_arrow_heads"] = showArrowHeads;

  // Update on client.
  updateDiagramBasedOnPreferences();

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
  var arrowSize = showArrowHeads ? diagramProperties.arrowSize : 0;
  setArrowSizes(arrowSize);
}
