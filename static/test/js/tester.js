// Отримання елементів з DOM
const timeInput = document.getElementById('time');
const timerElement = document.getElementById('timer');
const userIdInput = document.getElementById('user_id');

// Отримання початкового часу з input
let time = parseInt(timeInput.value) * 60;

// Функція, яка оновлює таймер та перевіряє, чи час не вийшов
function updateTimer() {
  // Перевірка, чи час не вийшов
  if (time <= 0) {
    // Якщо час вийшов, відправляємо POST-запит на поточну сторінку з пустою формою та id користувача
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.href;
    const userIdInputClone = userIdInput.cloneNode(true);
    form.appendChild(userIdInputClone);
    document.body.appendChild(form);
    form.submit();
    return;
  }

  // Оновлення елементу з таймером
  const hours = Math.floor(time / 3600).toString().padStart(2, '0');
  const minutes = Math.floor((time % 3600) / 60).toString().padStart(2, '0');
  const seconds = (time % 60).toString().padStart(2, '0');
  timerElement.innerHTML = `${hours}:${minutes}:${seconds}`;

  // Зменшення часу на 1 секунду та очікування наступного оновлення
  time -= 1;
  setTimeout(updateTimer, 1000);
}

// Запуск оновлення таймеру
updateTimer();
