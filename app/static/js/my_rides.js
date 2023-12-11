window.onload = function() {
    var rideButtons = document.querySelectorAll('.ride-actions button');
    rideButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            event.target.form.submit();
        });
    });

    var pastActionsButtons = document.querySelectorAll('.past-actions button');
    pastActionsButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            event.target.form.submit();
        });
    });
};