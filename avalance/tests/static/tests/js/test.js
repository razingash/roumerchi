document.addEventListener('DOMContentLoaded', function () {
    const testWalkthrough = document.getElementById('test__walkthrough');
    const testDescription = document.getElementById('test__description');
    const buttonStart = document.querySelector('.button__start');
    const buttonBack = document.querySelector('.back_to_description');
    const questionLists = document.querySelectorAll('.quetions__list');
    const submitButton = document.querySelector('.submit');

    const selectedAnswers = {};
    buttonStart.addEventListener('click', function () {
        testDescription.style.display = 'none';
        testWalkthrough.style.display = 'block';
    });
    buttonBack.addEventListener('click', function () {
        testDescription.style.display = 'block';
        testWalkthrough.style.display = 'none';
    });

    function onAnswerSelected(event) {
        if (event.target.tagName.toLowerCase() === 'input' && event.target.type === 'radio') {
            const questionId = event.target.closest('.quetions__list').id;
            selectedAnswers[questionId] = event.target.nextElementSibling.innerText;

            console.log(selectedAnswers);
        }
    }


    questionLists.forEach(function (list) {
        list.addEventListener('change', onAnswerSelected);
    });


    submitButton.addEventListener('click', function () {
        const unansweredQuestions = Array.from(questionLists).filter(function (list) {
            const questionId = list.id;
            return !selectedAnswers.hasOwnProperty(questionId) || !selectedAnswers[questionId];
        });

        if (unansweredQuestions.length > 0) {
            console.log('Error: not all questions are marked');
            return;
        }

        const answers = [];
        questionLists.forEach(function (list) {
            const questionId = list.id;
            const selectedAnswer = selectedAnswers[questionId] || null;
            answers.push(selectedAnswer);
        });

        const currentUrl = window.location.href;
        const csrfToken = $('meta[name=csrf-token]').attr('content');
        const userId = 1;
        const testId = $('meta[name="test-id"]').attr('content');

        $.post({
            url: currentUrl,
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                'request_type': 'new_walkthrough',
                'test_id': testId,
                'sender_id': userId,
                'selected_answers': answers
            },
            success: function (response) {
                console.log(response)
                console.log('status' + response.status)
                console.log('data' + response.data)
                console.log('message' + response.message)
                if (response && response.status === 200) {
                    $('#unique__result').html(response.message);
                    $('#test__results').css('display', 'block')
                    $('#test__walkthrough').css('display', 'none')

                    $('[data-criterion-result-id]').each(function() {
                        var criterionId = $(this).data('criterion-result-id');
                        var criterionResult = response.criterions[criterionId];
                        var roundedResult = Math.round((100 * criterionResult) / answers.length);
                        $(this).html(roundedResult + " %");
                    });
                    $('[data-criterion-bar-id]').each(function () {
                        var criterionId = $(this).data('criterion-bar-id');
                        var criterionResult = response.criterions[criterionId];
                        var roundedResult = Math.round((100 * criterionResult) / answers.length);
                        $(this).css('width', roundedResult + "%")
                    });
                    console.log('Success');
                    console.log(response.criterions)
                } else {
                    console.error('Error during sending POST request:', response.message);
                }
            },
            error: function (xhr, status, error) {
                console.error('Error during sending POST request:', error);
            }
        });
    });
});