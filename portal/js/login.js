/*global $, document, window, setTimeout, navigator, console, location*/
var backendUrl = 'https://thanima-backend.herokuapp.com';
// var backendUrl = 'http://localhost:8000';
function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
          c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
          return c.substring(name.length, c.length);
      }
  }
  return "";
}

function register() {
  var email = jQuery('#email').val();
  var contact = jQuery('#phone').val();
  var fullname = jQuery('#name').val();
  var gender = jQuery('#gender').val();
  var reg_no = jQuery('#regno').val();
  var password = jQuery('#password').val();

  var registerRequest = {
    'email': email,
    'contact': contact,
    'full_name': fullname,
    'gender': gender,
    'reg_no': reg_no,
    'password': password
  };

  fetch(`${backendUrl}/api/auth/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(registerRequest)
  }).then((response) => response.json())
  .then((result) => {
    console.log(result);
    console.log(result.status);
    if(result.status == 200) {
      console.log('sup');
      setCookie("token",result.data.token, 3);
      console.log(document.cookie);
      location.reload();
    } else {
      alert(result.message);
    }
  })
}

function letMeIn() {
  var email = document.getElementById('loginMail').value;
  var password = document.getElementById('loginPassword').value;
  console.log(email, password);

  var loginRequest = {
    'email': email,
    'password': password
  };

  fetch(`${backendUrl}/api/auth/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(loginRequest)
  }).then((response) => response.json())
  .then(result => {
    console.log(result);
    if(result.status == 200) {
      setCookie("token",result.data.key, 3);
      window.location.replace(`https://${window.location.host}/profile/`);
    } else {
      alert('Invalid Login Credentials');
    }
  });
}

if(getCookie('token') != "" && getCookie('token') != 'undefined') {
  window.location.replace(`https://${window.location.host}/profile/`);
}

$(document).ready(function () {
  "use strict";

  var usernameError = true,
    emailError = true,
    regError = true,
    phoneError = true,
    passwordError = true;

  var $regex_regno = /^([0-9]{2}[A-Z]{3}[0-9]{4})$/;
  var $regex_mail = /@vitstudent.ac.in/;
  var $regex_phone = /^\d{10}$/;

  // Detect browser for css purpose
  if (navigator.userAgent.toLowerCase().indexOf("firefox") > -1) {
    $(".form form label").addClass("fontSwitch");
  }

  // Label effect
  $("input").focus(function () {
    $(this).siblings("label").addClass("active");
  });

  // Form validation
  $("input").blur(function () {
    // User Name
    if ($(this).hasClass("name")) {
      if ($(this).val().length === 0) {
        $(this)
          .siblings("span.error")
          .text("Please type your full name")
          .fadeIn()
          .parent(".form-group")
          .addClass("hasError");
        usernameError = true;
      } else if ($(this).val().length > 1 && $(this).val().length <= 5) {
        $(this)
          .siblings("span.error")
          .text("Please type at least 6 characters")
          .fadeIn()
          .parent(".form-group")
          .addClass("hasError");
        usernameError = true;
      } else {
        $(this)
          .siblings(".error")
          .text("")
          .fadeOut()
          .parent(".form-group")
          .removeClass("hasError");
        usernameError = false;
      }
    }
    // Email
    if ($(this).hasClass("email")) {
      if ($(this).val().match($regex_mail)) {
        $(this)
          .siblings(".error")
          .text("")
          .fadeOut()
          .parent(".form-group")
          .removeClass("hasError");
        emailError = false;
      } else if ($(this).val().length === 0) {
        $(this)
          .siblings("span.error")
          .text("Please type your VIT mail ID")
          .fadeIn()
          .parent(".form-group")
          .addClass("hasError");
        emailError = true;
      } else {
        $(this)
          .siblings("span.error")
          .text("Please check the mail ID. Use VIT mail ID.")
          .fadeIn()
          .parent(".form-group")
          .addClass("hasError");
        emailError = true;
      }
    }

    // Registration Number
    if ($(this).hasClass("regno")) {
      if ($(this).val().match($regex_regno)) {
        $(this)
          .siblings(".error")
          .text("")
          .fadeOut()
          .parent(".form-group")
          .removeClass("hasError");
        regError = false;
      } else if ($(this).val().length === 0) {
        $(this)
          .siblings("span.error")
          .text("Please type your registration number")
          .fadeIn()
          .parent(".form-group")
          .addClass("hasError");
        regError = true;
      } else {
        $(this)
          .siblings("span.error")
          .text("Please check your registration number.")
          .fadeIn()
          .parent(".form-group")
          .addClass("hasError");
        regError = true;
      }
    }

    // Phone Number
    if ($(this).hasClass("phone")) {
      if ($(this).val().match($regex_phone)) {
        $(this)
          .siblings(".error")
          .text("")
          .fadeOut()
          .parent(".form-group")
          .removeClass("hasError");
        phoneError = false;
      } else if ($(this).val().length === 0) {
        $(this)
          .siblings("span.error")
          .text("Please type your contact number")
          .fadeIn()
          .parent(".form-group")
          .addClass("hasError");
        phoneError = true;
      } else {
        $(this)
          .siblings("span.error")
          .text("Please check the contact number")
          .fadeIn()
          .parent(".form-group")
          .addClass("hasError");
        phoneError = true;
      }
    }

    // PassWord
    if ($(this).hasClass("pass")) {
      if ($(this).val().length < 8) {
        $(this)
          .siblings("span.error")
          .text("Please type at least 8 charcters")
          .fadeIn()
          .parent(".form-group")
          .addClass("hasError");
        passwordError = true;
      } else {
        $(this)
          .siblings(".error")
          .text("")
          .fadeOut()
          .parent(".form-group")
          .removeClass("hasError");
        passwordError = false;
      }
    }

    // label effect
    if ($(this).val().length > 0) {
      $(this).siblings("label").addClass("active");
    } else {
      $(this).siblings("label").removeClass("active");
    }
  });

  // form switch
  $("a.switch").click(function (e) {
    $(this).toggleClass("active");
    e.preventDefault();

    if ($("a.switch").hasClass("active")) {
      $(this)
        .parents(".form-peice")
        .addClass("switched")
        .siblings(".form-peice")
        .removeClass("switched");
    } else {
      $(this)
        .parents(".form-peice")
        .removeClass("switched")
        .siblings(".form-peice")
        .addClass("switched");
    }
  });

  // Reload page
  $("a.profile").on("click", function () {
    location.reload(true);
  });
});
