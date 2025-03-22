// Helper Functions
async function getUserData() {
  const username = getCookie("username");

  if (!username) {
    alert('יש להתחבר למערכת כדי לבצע פעולה זו.')
    window.location.href = "/login";  
    return;
  }

  try {
    const response = await fetch(`/users/${username}`);
    const userData = await response.json();

    return(userData)
  }
  catch (error) {
    console.error("Error fetching user data:", error);
  }
}

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

async function saveSupplierToLocalStorage(userData) {
  if (userData.Role === "Supplier") {
      try {
          const response = await fetch(`/suppliers/by-username/${userData.UserName}`, {
              method: "GET",
              headers: { "Content-Type": "application/json" },
          });

          const data = await response.json();
          if (response.ok) {
              let supplierID = data.data.SuppID;
              localStorage.setItem("Supplier", supplierID);
          } else {
              alert("שגיאה: " + data.error);
          }
      } catch (error) {
          console.error("Error fetching supplier ID:", error);
          alert("שגיאה בחיבור לשרת.");
      }
  }
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

    fetch("/auth/login", {
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
      // Successful login logic
        if (data.message) {
            alert(data.message); 
            setCookie("username", username, 7);

            document.forms['login']['username'].value = "";
            document.forms['login']['password'].value = "";

            // window.location.href = "/profile";  
        } else {
          // Unsuccessful login logic
            alert("Login failed! " + (data.error || ""));
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Login failed due to an error!");  // Handle network errors
    });

    return false; // Prevent form submission
}

  
  // Populate profile page with user data (currently using hardcoded data)
  async function populateProfilePage() {
    const username = getCookie("username");
    if (username == null) {
      alert("You are not logged in!");
      window.location = "/login";
      return;
    }
    userData = await getUserData()
    if(userData.Role == "Supplier"){
      fetch(`/suppliers/by-username/${username}`, {
          method: "GET",
          headers: {
              "Content-Type": "application/json"
          }
      })
      .then(response => response.json())
      .then(data=>{
        if (data.message === "Success") {
          document.getElementById("profile_full_name").innerText = data.data['fullname'];
          document.getElementById("profile_address").innerText = data.data['address'];
          document.getElementById("profile_phone").innerText = data.data['phone'];
          document.getElementById("profile_role").innerText = data.data['role'] == "Supplier" ? "ספק" : data.data['role'];
          document.getElementById("profile_company").innerText = data.data['SuppName'] ;
        } else {
          // Unsuccessful login logic
            alert("לא נמצא שם משתמש או ספק מתאים " + (data.error || ""));
            window.location = "/login";
            return;
        }
      }) 
    }
    else if (userData.Role == "Admin"){
      document.getElementById('profileNameLabel').innerText = "שם משתמש"
      document.getElementById("profile_full_name").innerText = userData.UserName;
      document.getElementById("profile_address").innerText = "-";
      document.getElementById("profile_phone").innerText = "-";
      document.getElementById("profile_role").innerText = "אדמין";
      document.getElementById("profile_company").innerText = "-" ;
    }
  }
  