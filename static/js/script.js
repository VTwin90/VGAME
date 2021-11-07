//Back To The Top Button, Code customised from: https://mdbootstrap.com/snippets/standard/mdbootstrap/2964350#js-tab-view

//Get Back to Top Button
const backToTopBtn = document.getElementById("btn-back-to-top");

// Back to Top Button shows when the user scrolls down 20px
window.onscroll = function () {
  scroll();
};

function scroll() {
  if (
    document.body.scrollTop > 20 ||
    document.documentElement.scrollTop > 20
  ) {
    backToTopBtn.style.display = "block";
  } else {
    backToTopBtn.style.display = "none";
  }
}
// Click to scroll to the Top
backToTopBtn.addEventListener("click", backToTop);

function backToTop() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}