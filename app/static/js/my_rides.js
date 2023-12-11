window.onload = function() {
    var buttons = document.querySelectorAll('.ride-actions button');
    buttons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    });
};