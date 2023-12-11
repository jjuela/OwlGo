window.onload = function() {
    hideAllFields();

    document.getElementById('ridetype').addEventListener('change', function() {
        hideAllFields();

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

    document.getElementById('reccuring').addEventListener('change', function() {
        if (this.checked) {
            document.getElementById('recurring_days-field').style.display = 'block';
        } else {
            document.getElementById('recurring_days-field').style.display = 'none';
        }
    });
};

function hideAllFields() {
    document.getElementById('departingFrom-field').style.display = 'none';
    document.getElementById('departingAt-field').style.display = 'none';
    document.getElementById('destination-field').style.display = 'none';
    document.getElementById('arrival-field').style.display = 'none';
    document.getElementById('duration-field').style.display = 'none';
    document.getElementById('stops-field').style.display = 'none';
    document.getElementById('reccuring-field').style.display = 'none';
    document.getElementById('recurring_days-field').style.display = 'none';
    document.getElementById('accessibility-field').style.display = 'none';
    document.getElementById('description-field').style.display = 'none';
    document.getElementById('vehicleType-field').style.display = 'none';
    document.getElementById('submit-field').style.display = 'none';
}

function showCommuteFields() {
    document.getElementById('departingFrom-field').style.display = 'block';
    document.getElementById('destination-field').style.display = 'block';
    document.getElementById('arrival-field').style.display = 'block';
    document.getElementById('reccuring-field').style.display = 'block';
    document.getElementById('vehicleType-field').style.display = 'block';
    document.getElementById('submit-field').style.display = 'block'; 

    var reccuringCheckbox = document.getElementById('reccuring');
    if (reccuringCheckbox.checked) {
        document.getElementById('recurring_days-field').style.display = 'block';
    }

    reccuringCheckbox.addEventListener('change', function() {
        if (this.checked) {
            document.getElementById('recurring_days-field').style.display = 'block';
        } else {
            document.getElementById('recurring_days-field').style.display = 'none';
        }
    });

    document.getElementById('accessibility-field').style.display = 'block';
    document.getElementById('description-field').style.display = 'block';
}

function showErrandFields() {
    document.getElementById('departingFrom-field').style.display = 'block';
    document.getElementById('departingAt-field').style.display = 'block';
    document.getElementById('stops-field').style.display = 'block';
    document.getElementById('accessibility-field').style.display = 'block';
    document.getElementById('description-field').style.display = 'block';
    document.getElementById('vehicleType-field').style.display = 'block';
    document.getElementById('submit-field').style.display = 'block'; 
}

function showLeisureFields() {
    document.getElementById('departingFrom-field').style.display = 'block';
    document.getElementById('departingAt-field').style.display = 'block';
    document.getElementById('destination-field').style.display = 'block';
    document.getElementById('arrival-field').style.display = 'block';
    document.getElementById('duration-field').style.display = 'block';
    document.getElementById('accessibility-field').style.display = 'block';
    document.getElementById('description-field').style.display = 'block';
    document.getElementById('vehicleType-field').style.display = 'block';
    document.getElementById('submit-field').style.display = 'block'; 
}

document.getElementById('add-stop').addEventListener('click', function() {
    var stopsField = document.getElementById('stops-field');
    var newStopField = document.createElement('input');
    newStopField.type = 'text';
    newStopField.name = 'stops';
    stopsField.appendChild(newStopField);

    var button = document.getElementById('add-stop');
    stopsField.appendChild(button);
});

document.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    console.log('Form submission prevented');
});