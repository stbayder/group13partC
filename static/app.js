// Helper Functions

// Function to set a client-side cookie
function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}
  
  // Function to get the value of a cookie by its name
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
  
  // Function to show or hide error messages for form validation
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
  
// Validation Functions

// Validate fields on the Contact Us page
function validateContactUs() {
    const patterns = {
        phone: /^(?:\+972|0)(?:[23489]|5[0-9]|77)[0-9]{7}$/,  // Valid phone pattern (Israel)
        email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, // Valid email pattern
        fullname: /^[\u0590-\u05FF\s]{2,}\s[\u0590-\u05FF\s]{2,}$/ // Hebrew name pattern
};
  
function validateField(field, value) {
    switch (field) {
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
  
    let isValid = true;
  
    // Validate all fields
    ['fullname', 'phone', 'email', 'message'].forEach(field => {
      const element = document.getElementById(field);
      const fieldIsValid = validateField(field, element.value);
      showError(field, !fieldIsValid);
      if (!fieldIsValid) isValid = false;
    });
  
    if (isValid) {
      alert('Form submitted successfully!');
      return true;
    }
  
    return false;
  }
  
  // Validate fields on the Add Product page
  function validateAddProduct() {
    const patterns = {
      product_id: /^[a-zA-Z0-9-_]+$/  // Valid product ID pattern (alphanumeric and special characters)
    };
  
    function validateField(field, value) {
      switch (field) {
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
  
    let isValid = true;
  
    // Validate all fields
    ['product_id', 'product_name', 'description', 'image', 'price', 'units', 'supplier_name'].forEach(field => {
      const element = document.getElementById(field);
      const fieldIsValid = validateField(field, element.value);
      showError(field, !fieldIsValid);
      if (!fieldIsValid) isValid = false;
    });
  
    if (isValid) {
      alert('מוצר נוסף בהצלחה!'); // Successfully added product message
      return true;
    }
  
    return false;
  }
  
  // Authentication & Profile Functions
  
  // Handle login logic (to be moved to the backend)
  function handleLoginForm(event) {
    event.preventDefault()
    var username = document.forms['login']['username'].value;
    var password = document.forms['login']['password'].value;

    fetch("/login", {
        method: "POST",
        body: JSON.stringify({
            userName: username,
            password: password,
        }),
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json()) // Convert response to JSON
    .then(data => {
        if (data.message) {
            alert(data.message);  // Success message
            setCookie("username", username, 7);

            // ✅ Clear form fields after successful login
            document.forms['login']['username'].value = "";
            document.forms['login']['password'].value = "";

            // window.location.href = "/profile";  // Redirect to profile page
        } else {
            alert("Login failed! " + (data.error || ""));
            // ❌ Don't clear fields here to let the user correct their input
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Login failed due to an error!");  // Handle network errors
    });

    return false; // Prevent form submission
}

  
  // Populate profile page with user data (currently using hardcoded data)
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
  
    const username = getCookie("username");
  
    // Ensure user is logged in
    if (username == null) {
      alert("You are not logged in!");
      window.location = "/login";
      return;
    }
  
    const profile = hardcodedInfo[username];
    if (!profile) {
      alert("Cannot display information about this profile");
      window.location = "/login";
      return;
    }
  
    document.getElementById("profile_full_name").innerText = profile['full_name'];
    document.getElementById("profile_address").innerText = profile['address'];
    document.getElementById("profile_phone").innerText = profile['phone'];
    document.getElementById("profile_role").innerText = profile['role'];
    document.getElementById("profile_company").innerText = profile['company'];
  }
  