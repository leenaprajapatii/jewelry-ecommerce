// /* script.js */
// let currentSlide = 1;

// function changeSlide(direction) {
//     const slides = document.querySelector('.slides');
//     const totalSlides = document.querySelectorAll('.slide').length;

//     currentSlide = (currentSlide + direction + totalSlides) % totalSlides;
//     slides.style.transform = `translateX(-${currentSlide * 100}%)`;
// }

let currentIndex = 0;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;
const sliderContainer = document.querySelector('.slides');

function changeSlide(direction) {
    currentIndex += direction;

    if (currentIndex < 0) {
        currentIndex = totalSlides - 1;
    } else if (currentIndex >= totalSlides) {
        currentIndex = 0;
    }

    sliderContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
}
