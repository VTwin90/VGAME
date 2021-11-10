//Code from emailjs and CI course
function sendMail(contactForm) {
    emailjs.send('service_gmail', 'V_GAMES', {
        'from_name': contactForm.name.value,
        'from_email': contactForm.emailaddress.value,
        'message': contactForm.message.value
    })
    .then(
        function(response) {
            Swal.fire({
                position: 'center',
                icon: 'success',
                title: 'Your message was successfully sent!',
                showConfirmButton: false,
                timer: 4500
              }),document.getElementById("contactForm").reset();
        },
        function(error) {
            Swal.fire({
                position: 'center',
                icon: 'error',
                title: 'Oops...',
                text: 'Your message was not sent',
                showConfirmButton: false,
                timer: 4500
              }),document.getElementById("contactForm").reset();
        },
    );
    return false;  // To block from loading a new page
}
