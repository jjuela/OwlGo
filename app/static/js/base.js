document.querySelector('.profile-pic').addEventListener('click', function() {
    document.getElementById('profile-modal').classList.add('open');
});

document.getElementById('close-modal').addEventListener('click', function() {
    document.getElementById('profile-modal').classList.remove('open');
});