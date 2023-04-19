// -----------------------------------------------------------------------------
// JavaScript for showing toast messages.
// Based on  https://www.w3schools.com/howto/howto_js_snackbar.asp
// -----------------------------------------------------------------------------

// Show the toast message.
function showToastMessage(message) {
  var x = document.getElementById("snackbar");
  x.innerHTML = message;
  x.className = "show";
  setTimeout(function() { x.className = x.className.replace("show", ""); }, 1750);
}
