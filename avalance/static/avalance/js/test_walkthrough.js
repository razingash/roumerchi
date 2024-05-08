document.addEventListener('DOMContentLoaded', function () {
    const questions = [
        {
            text: 'как вы относитесь к государственному регулированию экономики?',
            answers: [
                'полное государственное вмешательство',
                'среднее государственное вмешательство',
                'не уверен',
                'минимальное государственное вмешательство',
                'абсолютное отсутствие государственного вмешательства',
            ],
        },
        {
            text: 'Какой любимый цвет?',
            answers: ['красный', 'зеленый', 'синий', 'желтый'],
        },
        {
            text: 'удаленно или в офисе?',
            answers: ['удаленно', 'в офисе', 'гибридный формат'],
        },
    ];
    let currentQuestionIndex = 0;

    const questionElement = document.querySelector('.test__question');
    const questionListElement = document.getElementById('question_1');
    const previousButton = document.querySelector('.previous_question_button');
    const selectedAnswers = [];

    function displayQuestion(index) {
        if (index < 0 || index >= questions.length) {
            console.warn('Нет больше вопросов.');
            return;
        }

        const currentQuestion = questions[index];

        questionElement.innerText = currentQuestion.text;

        questionListElement.innerHTML = '';

        currentQuestion.answers.forEach((answer, i) => {
            const label = document.createElement('label');
            label.className = 'quetion__item';
            label.id = `answer_${i + 1}`;

            const input = document.createElement('input');
            input.type = 'checkbox';
            input.className = 'test__quetion__checkbox';
            input.checked = selectedAnswers[index] === answer;

            const answerDiv = document.createElement('div');
            answerDiv.className = 'quetion__answer';
            answerDiv.innerText = answer;

            label.appendChild(input);
            label.appendChild(answerDiv);
            questionListElement.appendChild(label);
        });
    }

    function onAnswerSelected(event) {
        if (event.target.tagName.toLowerCase() === 'input') {
            const label = event.target.parentElement;
            const selectedAnswer = label.querySelector('.quetion__answer').innerText;

            selectedAnswers[currentQuestionIndex] = selectedAnswer;

            currentQuestionIndex += 1;
            displayQuestion(currentQuestionIndex);
        }
    }

    questionListElement.addEventListener('change', onAnswerSelected);
    window.onload = () => {
        displayQuestion(currentQuestionIndex);
    };

    previousButton.addEventListener('click', () => {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex -= 1;
            displayQuestion(currentQuestionIndex);
        }
    });
});