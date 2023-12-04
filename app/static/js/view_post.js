// get the modal and buttons
var modal = document.getElementById('signupModal');
var btn = document.getElementById('signupButton');
var span = document.getElementById('closeSignupModal');

// open on click
btn.onclick = function() {
  modal.style.display = "block";
}

// close on click
span.onclick = function() {
  modal.style.display = "none";
}

// close outside of modal
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

// add stops
document.getElementById('add-stop').addEventListener('click', function() {
  var newField = document.createElement('input');
  newField.type = 'text';
  newField.name = 'stop';
  newField.placeholder = 'Enter a stop';

  var newFieldContainer = document.createElement('div');
  newFieldContainer.appendChild(newField);

  document.getElementById('stops-container').appendChild(newFieldContainer);

  // button at the end of the fieldlist
  var button = document.getElementById('add-stop');
  stopsField.appendChild(button);
});

// hide fields based on ride type
