const filterButton = document.getElementById('filter-button');
const filterForm = document.querySelector('form');

filterButton.addEventListener('click', () => {
    filterForm.classList.toggle('hidden');
});

