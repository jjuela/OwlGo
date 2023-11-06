document.getElementById('ridetype').addEventListener('change', function() {
    // hide fields first
    document.getElementById('departingFrom-field').style.display = 'none';
    document.getElementById('departingAt-field').style.display = 'none';
    document.getElementById('destination-field').style.display = 'none';
    document.getElementById('arrival-field').style.display = 'none';
    document.getElementById('duration-field').style.display = 'none';
    document.getElementById('stops-field').style.display = 'none';
    document.getElementById('reccuring-field').style.display = 'none';
    document.getElementById('accessibility-field').style.display = 'none';
    document.getElementById('description-field').style.display = 'none';

    // show on ride type
    if (this.value == '1') { // commute
        document.getElementById('departingFrom-field').style.display = 'block';
        document.getElementById('departingAt-field').style.display = 'block';
        document.getElementById('destination-field').style.display = 'block';
        document.getElementById('arrival-field').style.display = 'block';
        document.getElementById('reccuring-field').style.display = 'block';
        document.getElementById('accessibility-field').style.display = 'block';
        document.getElementById('description-field').style.display = 'block';
    } else if (this.value == '2') { // errand
        document.getElementById('departingFrom-field').style.display = 'block';
        document.getElementById('departingAt-field').style.display = 'block';
        document.getElementById('destination-field').style.display = 'block';
        document.getElementById('stops-field').style.display = 'block';
        document.getElementById('accessibility-field').style.display = 'block';
        document.getElementById('description-field').style.display = 'block';
    } else if (this.value == '3') { // leisure
        document.getElementById('departingFrom-field').style.display = 'block';
        document.getElementById('departingAt-field').style.display = 'block';
        document.getElementById('destination-field').style.display = 'block';
        document.getElementById('arrival-field').style.display = 'block';
        document.getElementById('duration-field').style.display = 'block';
        document.getElementById('accessibility-field').style.display = 'block';
        document.getElementById('description-field').style.display = 'block';
    }
});