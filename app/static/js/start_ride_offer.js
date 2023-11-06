document.getElementById('ridetype').addEventListener('change', function() {
    // hide rest
    document.getElementById('location-field').style.display = 'none';
    document.getElementById('destination-field').style.display = 'none';
    document.getElementById('departing-field').style.display = 'none';
    document.getElementById('arrival-field').style.display = 'none';
    document.getElementById('duration-field').style.display = 'none';
    document.getElementById('pickup-field').style.display = 'none';
    document.getElementById('stops-field').style.display = 'none';
    document.getElementById('reccuring-field').style.display = 'none';
    document.getElementById('accessibility-field').style.display = 'none';
    document.getElementById('description-field').style.display = 'none';

    if (this.value == '1') { // leisure
        document.getElementById('location-field').style.display = 'block';
        document.getElementById('destination-field').style.display = 'block';
        document.getElementById('arrival-field').style.display = 'block';
        document.getElementById('duration-field').style.display = 'block';
        document.getElementById('accessibility-field').style.display = 'block';
        document.getElementById('description-field').style.display = 'block';
    } else if (this.value == '2') { // commute
        document.getElementById('location-field').style.display = 'block';
        document.getElementById('destination-field').style.display = 'block';
        document.getElementById('arrival-field').style.display = 'block';
        document.getElementById('reccuring-field').style.display = 'block';
        document.getElementById('accessibility-field').style.display = 'block';
        document.getElementById('description-field').style.display = 'block';
    } else if (this.value == '3') { // errand
        document.getElementById('location-field').style.display = 'block';
        document.getElementById('destination-field').style.display = 'block';
        document.getElementById('departing-field').style.display = 'block';
        document.getElementById('stops-field').style.display = 'block';
        document.getElementById('accessibility-field').style.display = 'block';
        document.getElementById('description-field').style.display = 'block';
    }
});