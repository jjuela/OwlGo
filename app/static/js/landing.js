// Get the modal elements
var loginModal = document.getElementById('loginModal');
var registerModal = document.getElementById('registerModal');

// Get the button elements
var loginButton = document.querySelector('.landing-login-button');
var registerButton = document.querySelector('.landing-signup-button');

// Get the close elements (assuming they are span elements)
var loginClose = document.querySelector('#loginModal .close');
var registerClose = document.querySelector('#registerModal .close');

// When the user clicks on the button, open the modal
loginButton.onclick = function() {
    loginModal.style.display = "block";
}

registerButton.onclick = function() {
    registerModal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
loginClose.onclick = function() {
    loginModal.style.display = "none";
}

registerClose.onclick = function() {
    registerModal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == loginModal) {
        loginModal.style.display = "none";
    }
    if (event.target == registerModal) {
        registerModal.style.display = "none";
    }
}