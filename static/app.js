// alert('debug');

// Function for setting a client-side cookie, using this temporarily for login functionality
function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}


// Function for getting cookie value by it's name, using this temporarily for login functionality
function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

// Function for handling login in client-side. Should be moved to backend.
function handleLoginForm() {
    var username = document.forms['login']['username'].value;
    var password = document.forms['login']['password'].value;

    // TODO: it is a very bad practice to perform login in client-side, this should be moved to backend when appropriate
    if ((username == "shani" || username == "stav")  && password == "123456"){
        setCookie("username", username, 7);
        // Login succeed :)
        return true;
    }

    alert("Login failed!");
    return false;
}

// Function for fetching information about the current logged in user and displaying their profile. At the moment this uses hard-coded data.
function populateProfilePage() {
    const hardcodedInfo = {
        'stav': {
            'full_name': 'Stav Bider',
            'address': 'Hertzel 45, Tel Aviv',
            'phone': '052-5381648',
            'role': 'Marketing',
            'company': 'Example Company Inc'
        },
        'shani': {
            'full_name': 'Shani Bar',
            'address': 'Hertzel 45, Tel Aviv',
            'phone': '052-5381648',
            'role': 'Marketing',
            'company': 'Example Company Inc'
        }
    }

    // Fetch username from cookie
    const username = getCookie("username")

    // Ensure user is logged in
    if (username == null) {
        alert("You are not logged in!")
        window.location = "/login"
        return
    }

    // Populate information within the page
    const profile = hardcodedInfo[username]
    if (!profile) {
        alert("Cannot display information about this profile")
        window.location = "/login"
    }

    document.getElementById("profile_full_name").innerText = profile['full_name']
    document.getElementById("profile_address").innerText = profile['address']
    document.getElementById("profile_phone").innerText = profile['phone']
    document.getElementById("profile_role").innerText = profile['role']
    document.getElementById("profile_company").innerText = profile['company']

}

// Function for doing form validation on contact-us page
function validateContactUs() {
    const form = document.getElementById('contactForm');
    const successMessage = document.getElementById('success-message');

    // Regular expressions for validation
    const patterns = {
        phone: /^(?:\+972|0)(?:[23489]|5[0-9]|77)[0-9]{7}$/,
        email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        fullname: /^[\u0590-\u05FF\s]{2,}\s[\u0590-\u05FF\s]{2,}$/
    };

    // Function to show error
    function showError(field, isError) {
        const errorElement = document.getElementById(`${field}-error`);
        const inputElement = document.getElementById(field);

        if (isError) {
            errorElement.style.display = 'block';
            inputElement.classList.add('invalid');
        } else {
            errorElement.style.display = 'none';
            inputElement.classList.remove('invalid');
        }
    }

    // Validate individual fields
    function validateField(field, value) {
        switch(field) {
            case 'fullname':
                return value.trim().length >= 4;
            case 'phone':
                return patterns.phone.test(value);
            case 'email':
                return patterns.email.test(value);
            case 'message':
                return value.trim().length >= 10;
            default:
                return true;
        }
    }

    // Form submission
        let isValid = true;

        // Validate all fields
        ['fullname', 'phone', 'email', 'message'].forEach(field => {
            const element = document.getElementById(field);
            const fieldIsValid = validateField(field, element.value);
            showError(field, !fieldIsValid);
            if (!fieldIsValid) isValid = false;
        });

        if (isValid) {
            alert('Form submitted successfully!')
            // Form is valid, we can send the request to the backend
            // TODO: when we have backend, save the information submitted from this form
            return true
        }

        // Form is invalid :(
        return false
}

// Function for doing form validation on add-product page
function validateAddProduct() {
    const form = document.getElementById('addProductForm');
    const successMessage = document.getElementById('success-message');

    // Regular expressions for validation
    const patterns = {
        product_id: /^[a-zA-Z0-9-_]+$/
    };

    // Function to show error
    function showError(field, isError) {
        const errorElement = document.getElementById(`${field}-error`);
        const inputElement = document.getElementById(field);

        if (isError) {
            errorElement.style.display = 'block';
            inputElement.classList.add('invalid');
        } else {
            errorElement.style.display = 'none';
            inputElement.classList.remove('invalid');
        }
    }

    // Validate individual fields
    function validateField(field, value) {
        switch(field) {
            case 'product_id':
                return patterns.product_id.test(value);
            case 'product_name':
            case 'supplier_name':
                return value.trim().length >= 2;
            case 'description':
                return value.trim().length >= 10;
            case 'image':
                return value !== '';
            case 'price':
            case 'units':
                return !isNaN(value) && parseFloat(value) > 0;
            default:
                return true;
        }
    }

    // Form submission
    let isValid = true;

    // Validate all fields
    ['product_id', 'product_name', 'description', 'image', 'price', 'units', 'supplier_name'].forEach(field => {
        const element = document.getElementById(field);
        const fieldIsValid = validateField(field, element.value);
        showError(field, !fieldIsValid);
        if (!fieldIsValid) isValid = false;
    });

    if (isValid) {
        alert('מוצר נוסף בהצלחה!')
        // Form is valid, we can send the request to the backend
        // TODO: when we have backend, save the information submitted from this form
        return true;
    }

    // Form is invalid :(
    return false;
}