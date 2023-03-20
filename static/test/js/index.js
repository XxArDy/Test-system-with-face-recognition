const addQuestionBtn = document.getElementById('add-question-btn');
const questionsContainer = document.getElementById('questions-container');

let questionCounter = 0;

addQuestionBtn.addEventListener('click', (event) => {
  event.preventDefault();
  questionCounter++;

  const newQuestion = document.createElement('div');
  newQuestion.classList.add('mb-3', 'border', 'border-secondary', 'p-3');
  newQuestion.id = questionCounter;
  newQuestion.innerHTML = `
  <div class="mb-3">
    <span class="form-label" for="question-${questionCounter}">Запитання ${questionCounter}:</span>
    <input type="text" class="form-control" id="question-${questionCounter}" name="question_${questionCounter}">
  </div>
  <div class="mb-3">
    <button class="add-answer-btn btn btn-primary ms-2"">Додати відповідь</button>
    <button type="button" class="delete-question-btn btn btn-danger ms-2">Видалити запитання</button>
  </div>
  <div class="answers-container">
    <!-- Контейнер для відповідей -->
  </div>
  `;
  questionsContainer.appendChild(newQuestion);

  let answerCounter = 0;
  const addAnswerBtn = newQuestion.querySelector('.add-answer-btn');
  const deleteQuestionBtn = newQuestion.querySelector('.delete-question-btn');

  addAnswerBtn.addEventListener('click', (event) => {
    event.preventDefault();
    answerCounter++;
    const questionId = newQuestion.id;
  
    const newAnswer = document.createElement('div');
    newAnswer.classList.add('mb-3', 'border', 'border-secondary', 'p-3');
    newAnswer.innerHTML = `
      <span for="answer-${questionId}-${answerCounter}" class="form-label">Відповідь ${answerCounter}:</span>
      <input type="text" class="form-control" id="answer-${questionId}-${answerCounter}" name="answer_${questionId}_${answerCounter}">
      <div class="mb-3 form-check">
        <label for="is-correct-${questionId}-${answerCounter}" class="form-check-label">Правильна відповідь?</label>
        <input type="checkbox" id="correct-answer" class="form-check-input" id="is-correct-${questionId}-${answerCounter}" name="is_correct_${questionId}_${answerCounter}">
      </div>
    `;
  
    const removeAnswerButton = document.createElement("button");
    removeAnswerButton.type = "button";
    removeAnswerButton.innerText = "Видалити";
    removeAnswerButton.classList.add("btn", "btn-danger", "ms-2");
    removeAnswerButton.addEventListener("click", () => {
      newAnswer.remove();
    });
  
    newAnswer.appendChild(removeAnswerButton);
    const answersContainer = newQuestion.querySelector('.answers-container'); 
    answersContainer.appendChild(newAnswer);
  });

  deleteQuestionBtn.addEventListener("click", () => {
    newQuestion.remove();
  });
});

