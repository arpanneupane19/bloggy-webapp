var modalBtn = document.querySelector('.view-followers');
var modalBg = document.querySelector('.followers-modal');
var closeBtn = document.querySelector('.close-modal');
var image = document.getElementById('userImage');

modalBtn.addEventListener('click', function () {
    modalBg.classList.add('bg-active');
});

closeBtn.addEventListener('click', function () {
    modalBg.classList.remove('bg-active')
})
