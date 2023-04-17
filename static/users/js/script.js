let formPassword = document.getElementById('formPassword');
let formImage = document.getElementById('formImage');

formPassword.addEventListener('submit', async (event) => {
    event.preventDefault();

    let pass = document.getElementById('curent_password')
    let newPass1 = document.getElementById('new_password')
    let newPass2 = document.getElementById('new_password_again')

    if ( newPass1.value !== newPass2.value ) {
        alert('Паролі не співпадають');
        return;
    }

    fetch('/user/change/password', {
      method: 'POST',
      body: new FormData(formPassword)
    })
    .then(response => response.json())
    .then(data => {
      if (data.result === true) {
        formPassword.reset();
        alert('Пароль успішно збережено!');
      } else {
        alert('Не вірний пароль користувача');
      }
    })
    .catch(error => {
      console.error('Помилка:', error);
      alert('Виникла помилка при збереженні даних.');
    });
});

formImage.addEventListener('submit', async (event) => {
  event.preventDefault();

  fetch('/user/change/image', {
      method: 'POST',
      body: new FormData(formImage)
    })
    .then(response => response.json())
    .then(data => {  
      if (data.result === true) {
        alert('Фото успішно змінено');
        location.reload();
      } else {
        alert('На фото не видно обличчя');
      }
    })
    .catch(error => {
      console.error('Помилка:', error);
      alert('Виникла помилка при збереженні даних.');
    });
});
