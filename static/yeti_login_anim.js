// Yeti login animation logic for login/register
// Handles face/hand state based on input focus/type

document.addEventListener('DOMContentLoaded', function() {
  const emailInput = document.getElementById('email-input');
  const passwordInput = document.getElementById('password-input');
  const showCheckbox = document.getElementById('show-password');
  const yetiFace = document.getElementById('yeti-face');
  const yetiFaceClosed = document.getElementById('yeti-face-closed');

  function setFace(state) {
    if (!yetiFace || !yetiFaceClosed) return;
    if (state === 'normal') {
      yetiFace.style.display = 'block';
      yetiFaceClosed.style.display = 'none';
    } else if (state === 'cover') {
      yetiFace.style.display = 'none';
      yetiFaceClosed.style.display = 'block';
    }
  }

  if (emailInput) {
    emailInput.addEventListener('focus', function() {
      setFace('normal');
    });
    emailInput.addEventListener('input', function() {
      setFace('normal');
    });
  }
  if (passwordInput) {
    passwordInput.addEventListener('focus', function() {
      setFace('cover');
    });
    passwordInput.addEventListener('input', function() {
      setFace('cover');
    });
  }
  if (showCheckbox) {
    showCheckbox.addEventListener('change', function() {
      if (showCheckbox.checked) {
        yetiFace.style.display = 'block';
        yetiFaceClosed.style.display = 'none';
        yetiFace.src = '/static/yeti_show.png';
      } else {
        setFace('cover');
      }
    });
  }
  // Default state
  setFace('normal');
});
