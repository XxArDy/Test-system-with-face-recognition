// Отримати посилання на відеоелемент та кнопки
const cameraFeed = document.getElementById('cameraFeed');
const takePhotoButton = document.getElementById('takePhotoButton');
const photoButton = document.getElementById('photoButton');
const cameraModal = document.getElementById('cameraModal');
const div = document.getElementById('mainDiv');
const photoInput = document.getElementById('photoInput');
// Змінна, в яку буде збережено зображення з камери
let photo = null;

let stream = null;

// Прикріпити відеопотік до відеоелементу
function startCamera() {
  navigator.mediaDevices.getUserMedia({ video: true })
  .then(function (s) {
    stream = s;
  cameraFeed.srcObject = s;
  cameraFeed.play();
  })
  .catch(function (error) {
    console.log("Error starting camera:", error);
  });
}

// Функція, яка відкриває модальне вікно з камерою
function openCameraModal() {
  // Отримати посилання на модальне вікно
  
  div.classList.add("overlay");
  // Показати відеопотік на елементі відео
  startCamera();
  
  // Відкрити модальне вікно
  cameraModal.classList.remove("hidden");
}

// Функція для зйомки фото
function takeSnapshot() {
  // Permitted file types
  var mime_types = ['image/jpeg', 'image/png'];
  

  // Create a canvas element and draw the current video frame on it
  var canvas = document.createElement('canvas');
  canvas.width = cameraFeed.videoWidth;
  canvas.height = cameraFeed.videoHeight;
  var context = canvas.getContext('2d');
  context.drawImage(cameraFeed, 0, 0, canvas.width, canvas.height);

  
  // Convert the canvas image to a Base64 encoded string
  var data_uri = canvas.toDataURL();
  var mime_type = data_uri.split(',')[0].split(':')[1].split(';')[0];
  if (mime_types.indexOf(mime_type) == -1) {
    alert('Invalid file type. Please select a JPEG or PNG file.');
    return;
  }

  photo = data_uri;

  // Set the value of the photoInput input field to the Base64 encoded string
  photoInput.value = photo;

  // Display the photo in the modal
  var photoPreview = document.getElementById('photoPreview');
  photoPreview.setAttribute('src', photo);
  photoPreview.style.display = 'block';
};


function closeModel() {
  div.classList.remove("overlay");
  cameraModal.classList.add("hidden");

  photoInput.setAttribute('value', photo);

  if (stream) {
    stream.getTracks().forEach(function (track) {
      track.stop();
    });
    stream = null;
  }
}

// Обробник події для кнопки Зробити фото
takePhotoButton.addEventListener('click', takeSnapshot);

// Запустити відеопотік при відкриванні модального вікна
photoButton.addEventListener('click', openCameraModal);
