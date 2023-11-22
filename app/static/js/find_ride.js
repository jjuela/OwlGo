window.onload = function() {
    // hide fields on load
    hideAllFields();

    document.getElementById('ridetype').addEventListener('change', function() {
        hideAllFields();

        // show fields when ride type is selected
        if (this.value) {
            if (this.value == 'commute') {
                showCommuteFields();
            } else if (this.value == 'errand') {
                showErrandFields();
            } else if (this.value == 'leisure') {
                showLeisureFields();
            }
        }
    });

// hide fields and filters
function hideAllFields() {
    document.getElementById('departingFrom-field').style.display = 'none';
    document.getElementById('destination-field').style.display = 'none';
    document.getElementById('duration-field').style.display = 'none';
    document.getElementById('stops-field').style.display = 'none';
    document.getElementById('reccuring-field').style.display = 'none';
    document.getElementById('recurring-days-field').style.display = 'none';
    document.getElementById('accessibility-field').style.display = 'none';
    document.getElementById('vehicle-type-field').style.display = 'none';
    document.getElementById('time-choice-field').style.display = 'none';
    document.getElementById('time-start-field').style.display = 'none';
    document.getElementById('time-end-field').style.display = 'none';
    document.getElementById('submit').style.display = 'none';
    document.getElementById('filter').style.display = 'none';
}

// show commute fields and filters
function showCommuteFields() {
    document.getElementById('departingFrom-field').style.display = 'block';
    document.getElementById('destination-field').style.display = 'block';
    document.getElementById('reccuring-field').style.display = 'block';

    document.getElementById('submit').style.display = 'block'; 

    var reccuringCheckbox = document.getElementById('reccuring');
    if (reccuringCheckbox.checked) {
        document.getElementById('recurring-days-field').style.display = 'block';
    }

    reccuringCheckbox.addEventListener('change', function() {
        if (this.checked) {
            document.getElementById('recurring-days-field').style.display = 'block';
        } else {
            document.getElementById('recurring-days-field').style.display = 'none';
        }
    });

    document.getElementById('accessibility-field').style.display = 'block';
    document.getElementById('time-choice-field').style.display = 'block';
    document.getElementById('time-start-field').style.display = 'block';
    document.getElementById('time-end-field').style.display = 'block';
    document.getElementById('filter').style.display = 'block';
}

// show errand fields and filters
function showErrandFields() {
    document.getElementById('departingFrom-field').style.display = 'block';
    document.getElementById('stops-field').style.display = 'block';
    document.getElementById('accessibility-field').style.display = 'block';
    document.getElementById('time-choice-field').style.display = 'block';
    document.getElementById('time-start-field').style.display = 'block';
    document.getElementById('time-end-field').style.display = 'block';
    document.getElementById('submit').style.display = 'block'; 
    document.getElementById('filter').style.display = 'block';
}

// show leisure fields and filters
function showLeisureFields() {
    document.getElementById('departingFrom-field').style.display = 'block';
    document.getElementById('destination-field').style.display = 'block';
    document.getElementById('duration-field').style.display = 'block';
    document.getElementById('accessibility-field').style.display = 'block';
    document.getElementById('time-choice-field').style.display = 'block';
    document.getElementById('time-start-field').style.display = 'block';
    document.getElementById('time-end-field').style.display = 'block';
    document.getElementById('submit').style.display = 'block'; 
    document.getElementById('filter').style.display = 'block';
}

// filters modal
var modal = document.getElementById("filtersModal");
var btn = document.getElementById("filter");
var span = document.getElementById("closeModalButton");

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
}};