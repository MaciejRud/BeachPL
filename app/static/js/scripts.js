window.addEventListener('DOMContentLoaded', event => {

    const loginToggle = document.getElementById('login-toggle');
    const loginFormWrapper = document.getElementById('login-form-wrapper');
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('value');



    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            offset: 74,
        });
    };


    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });


    if (isLoggedIn === 'true') {
        // loginToggle.textContent = 'Wyloguj';

        // Obsługa wylogowania
        loginToggle.addEventListener('click', function() {
            fetch(logoutUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (response.ok) {
                    location.reload(); // Odśwież stronę po wylogowaniu
                }
            });
        });
    } else {
        // loginToggle.textContent = 'Zaloguj';

        // Przełączanie widoczności formularza logowania
        loginToggle.addEventListener('click', function() {
            loginFormWrapper.classList.toggle('d-none');
        });

        // Obsługa logowania
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(loginForm);
            const data = {
                email: formData.get('email'),
                password: formData.get('password')
            };

            fetch(loginUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    throw new Error('Nieprawidłowe dane logowania');
                }
            })
            .catch(error => {
                loginError.textContent = error.message;
                loginError.classList.remove('d-none');
            });
        });
    }
});
