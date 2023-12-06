window.onload = function() {
  // signup modal
  var modal = document.getElementById('signupModal');
  var btn = document.getElementById('signupButton');
  var span = document.getElementById('closeSignupModal');

  btn.onclick = function() {
    modal.style.display = "block";
  }

  span.onclick = function() {
    modal.style.display = "none";
  }

  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  }

  // add stops
  var addStopButton = document.getElementById('add-stop');
  if (addStopButton) {
    addStopButton.addEventListener('click', function() {
      var newField = document.createElement('input');
      newField.type = 'text';
      newField.name = 'stop';
      newField.placeholder = 'Enter a stop';

      var newFieldContainer = document.createElement('div');
      newFieldContainer.appendChild(newField);

      document.getElementById('stops-container').appendChild(newFieldContainer);

      var button = document.getElementById('add-stop');
      stopsField.appendChild(button);
    });
  }

  // report modal
  var reportModal = document.getElementById("reportModal");
  var reportButton = document.getElementById("reportButton");
  var reportSpan = document.getElementsByClassName("close-report")[0];

  reportButton.onclick = function() {
    reportModal.style.display = "block";
  }

  reportSpan.onclick = function() {
    reportModal.style.display = "none";
  }

  window.onclick = function(event) {
    if (event.target == reportModal) {
      reportModal.style.display = "none";
    }
  }
}