window.addEventListener('DOMContentLoaded', event => {

    const loginToggle = document.getElementById('login-toggle');
    const loginFormWrapper = document.getElementById('login-form-wrapper');
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('value');

    const token = localStorage.getItem('authToken');
    if (token) {
        // Użytkownik jest zalogowany, pokaż przycisk "Wyloguj"
        loginToggle.innerHTML = `
                <span class="d-flex align-items-center">
                    <i class="bi-box-arrow-right me-2"></i>
                    <span class="small">Wyloguj</span>
                </span>`;
        loginToggle.classList.remove('btn-primary');
        loginToggle.classList.add('btn-danger');

        // Obsługa wylogowania
        loginToggle.addEventListener('click', function() {
            // Usuń token i odśwież stronę
            localStorage.removeItem('authToken');
            location.reload();
        });
    }

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
                return response.json();
            } else {
                throw new Error('Nieprawidłowe dane logowania');
            }
        })
        .then(data => {
            // Zapisz token w localStorage
            localStorage.setItem('authToken', data.token);

            // Ukryj formularz logowania
            loginFormWrapper.classList.add('d-none');

            // Zmień przycisk "Zaloguj" na "Wyloguj"
            loginToggle.innerHTML = `
                <span class="d-flex align-items-center">
                    <i class="bi-box-arrow-right me-2"></i>
                    <span class="small">Wyloguj</span>
                </span>`;
            loginToggle.classList.remove('btn-primary');
            loginToggle.classList.add('btn-danger');

            // Obsługa wylogowania
            loginToggle.addEventListener('click', function() {
                // Usuń token i odśwież stronę
                localStorage.removeItem('authToken');
                location.reload();
            });
        })
        .catch(error => {
            loginError.textContent = error.message;
            loginError.classList.remove('d-none');
        });
    });
});
