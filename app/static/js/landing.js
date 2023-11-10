// modal elements
var loginModal = document.getElementById('loginModal');
var registerModal = document.getElementById('registerModal');

// button elements
var loginButton = document.querySelector('.landing-login-button');
var registerButton = document.querySelector('.landing-signup-button');

// close elements
var loginClose = document.querySelector('#loginModal .close');
var registerClose = document.querySelector('#registerModal .close');

// open modal
loginButton.onclick = function() {
    loginModal.style.display = "block";
}

registerButton.onclick = function() {
    registerModal.style.display = "block";
}

// close modal
loginClose.onclick = function() {
    loginModal.style.display = "none";
}

registerClose.onclick = function() {
    registerModal.style.display = "none";
}

// close outside of modal
window.onclick = function(event) {
    if (event.target == loginModal) {
        loginModal.style.display = "none";
    }
    if (event.target == registerModal) {
        registerModal.style.display = "none";
    }
}