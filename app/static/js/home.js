let index = 0;
const items = document.querySelectorAll('.ride-carousel-item');
const totalItems = items.length;

document.querySelector('.ride-carousel').addEventListener('click', () => {
    index = (index + 1) % totalItems;  // Move to the next item
    items.forEach((item, i) => {
        item.style.transform = `translateX(${(i - index) * 100}%)`;
    });
});