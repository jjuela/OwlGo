document.querySelector('.profile-pic').addEventListener('click', function() {
    document.body.classList.add('modal-open');
    document.getElementById('profile-modal').classList.add('open');
    document.getElementById('overlay').style.display = 'block';
});

document.getElementById('close-modal').addEventListener('click', function() {
    document.body.classList.remove('modal-open');
    document.getElementById('profile-modal').classList.remove('open');
    document.getElementById('overlay').style.display = 'none';
});