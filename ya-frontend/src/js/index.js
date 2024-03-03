// import Fancybox css
// import 'fancyapps/ui/dist/fancybox.css';

// import Swiper styles and modules styles
import 'swiper/css';
import 'swiper/css/pagination';

import '../css/style.css';

import Alpine from 'alpinejs';
import intersect from '@alpinejs/intersect';

// import Swiper JS
import Swiper, { Navigation } from 'swiper';

// import ScrollReveal
import ScrollReveal from 'scrollreveal';

// import Isotope
import Isotope from 'isotope-layout';

// import fslightbox
import fslightbox from 'fslightbox';
// require('fslightbox');

Alpine.plugin(intersect);
window.Alpine = Alpine;

Alpine.start();

// Testimonial
const testimonial01 = new Swiper('.testimonial-01', {
  // configure Swiper to use modules
  modules: [Navigation],
  loop: true,
  spaceBetween: 50,
  centeredSlides: false,
  slidesPerView: 1,
  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev',
  },
});

/*========== SCROLL REVEAL ANIMATION ==========*/
window.sr = ScrollReveal({
  distance: '60px',
  duration: 2800,
  reset: false,
});

sr.reveal(`.animate_top`, {
  origin: 'top',
  interval: 100,
});

sr.reveal(`.animate_left`, {
  origin: 'left',
  interval: 100,
});

sr.reveal(`.animate_right`, {
  origin: 'right',
  interval: 100,
});

// Project Tab
const projectsWrapper = document.querySelector('.projects-wrapper');
const projectTabBTN = document.querySelectorAll('.project-tab-btn');

const iso = new Isotope(projectsWrapper, {
  // options
  itemSelector: '.project-item',
  masonry: {
    columnWidth: '.project-sizer',
  },
});

projectTabBTN.forEach((btn) => {
  btn.addEventListener('click', () => {
    const selector = btn.getAttribute('data-filter');
    iso.arrange({
      filter: selector,
    });
  });
});

// Document Loaded
document.addEventListener('DOMContentLoaded', () => {});
