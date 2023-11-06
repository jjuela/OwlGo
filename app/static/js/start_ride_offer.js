window.onload = function() {
    // hide fields first
    hideAllFields();

    document.getElementById('ridetype').addEventListener('change', function() {
        // hide fields first
        hideAllFields();

        // show on ride type
        if (this.value == '1') { // commute
            showCommuteFields();
        } else if (this.value == '2') { // errand
            showErrandFields();
        } else if (this.value == '3') { // leisure
            showLeisureFields();
        }
    });
}

function hideAllFields() {
    document.getElementById('departingFrom-field').style.display = 'none';
    document.getElementById('departingAt-field').style.display = 'none';
    document.getElementById('destination-field').style.display = 'none';
    document.getElementById('arrival-field').style.display = 'none';
    document.getElementById('duration-field').style.display = 'none';
    document.getElementById('stops-field').style.display = 'none';
    document.getElementById('reccuring-field').style.display = 'none';
    document.getElementById('accessibility-field').style.display = 'none';
    document.getElementById('description-field').style.display = 'none';
}

function showCommuteFields() {
    document.getElementById('departingFrom-field').style.display = 'block';
    document.getElementById('departingAt-field').style.display = 'block';
    document.getElementById('destination-field').style.display = 'block';
    document.getElementById('arrival-field').style.display = 'block';
    document.getElementById('reccuring-field').style.display = 'block';
    document.getElementById('accessibility-field').style.display = 'block';
    document.getElementById('description-field').style.display = 'block';
}

function showErrandFields() {
    document.getElementById('departingFrom-field').style.display = 'block';
    document.getElementById('departingAt-field').style.display = 'block';
    document.getElementById('destination-field').style.display = 'block';
    document.getElementById('stops-field').style.display = 'block';
    document.getElementById('accessibility-field').style.display = 'block';
    document.getElementById('description-field').style.display = 'block';
}

function showLeisureFields() {
    document.getElementById('departingFrom-field').style.display = 'block';
    document.getElementById('departingAt-field').style.display = 'block';
    document.getElementById('destination-field').style.display = 'block';
    document.getElementById('arrival-field').style.display = 'block';
    document.getElementById('duration-field').style.display = 'block';
    document.getElementById('accessibility-field').style.display = 'block';
    document.getElementById('description-field').style.display = 'block';
}