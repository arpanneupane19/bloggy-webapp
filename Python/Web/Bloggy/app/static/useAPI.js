var viewBtn = document.querySelector('.api');
var apiModal = document.querySelector('.api-modal');
var closeBtn = document.querySelector('.close-modal');

viewBtn.addEventListener('click', function() {
    apiModal.classList.add('bg-active');
});

closeBtn.addEventListener('click', function() {
    apiModal.classList.remove('bg-active')
})
