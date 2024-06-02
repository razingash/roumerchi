document.addEventListener('DOMContentLoaded', function () {
    const testWalkthrough = document.getElementById('test__walkthrough');
    const testDescription = document.getElementById('test__description');
    const testEndedResult = document.getElementById('test__ended');
    const buttonStart = document.querySelector('.button__start');
    const buttonBack = document.querySelector('.back_to_description');
    const questionLists = document.querySelectorAll('.quetions__list');
    const submitButton = document.querySelector('.submit');
    const testId =  $('meta[name=test-id]').attr('content');
    const csrfToken = $('meta[name=csrf-token]').attr('content');
    const userUuidTag = $('meta[name=user-uuid]').attr('content');

    const selectedAnswers = {};
    buttonStart.addEventListener('click', function () {
        testDescription.style.display = 'none';
        testWalkthrough.style.display = 'flex';
        testEndedResult.style.display = 'none';
    });
    buttonBack.addEventListener('click', function () {
        testDescription.style.display = 'block';
        testWalkthrough.style.display = 'none';
        testEndedResult.style.display = 'flex';
    });

    function onAnswerSelected(event) {
        if (event.target.tagName.toLowerCase() === 'input' && event.target.type === 'radio') {
            const questionId = event.target.closest('.quetions__list').id;
            selectedAnswers[questionId] = event.target.nextElementSibling.innerText;

            /*console.log(selectedAnswers);*/

            const checkboxItems = event.target.closest('.quetions__list').querySelectorAll('.checkbox__item');
            checkboxItems.forEach(function(item) {
                item.classList.remove('state_1');
            });
            event.target.closest('.quetion__item').querySelector('.checkbox__item').classList.add('state_1');

            sessionStorage.setItem(testId, JSON.stringify(selectedAnswers));
            /*console.log(sessionStorage);*/
        }
    }

    function getSavedAnswers(testId) {
        const savedAnswers = sessionStorage.getItem(testId);

        if (savedAnswers) {
            console.log(JSON.parse(savedAnswers))
            return JSON.parse(savedAnswers);
        }
        return {};
    }

    const savedAnswers = getSavedAnswers(testId);
    for (const [questionId, answerText] of Object.entries(savedAnswers)) {
        const questionList = document.getElementById(questionId);
        if (questionList) {
            const radioInputs = questionList.querySelectorAll('input[type="radio"]');
            radioInputs.forEach(radio => {
                if (radio.nextElementSibling.innerText === answerText) {
                    /* it's really hard to bypass browser restrictions((
                    radio.dispatchEvent(new Event('click', { bubbles: true }));
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                    radio.setAttribute('checked', 'checked');
                    radio.checked = true;
                    */
                    radio.closest('.quetion__item').querySelector('.checkbox__item').classList.add('state_2');
                }
            });
        }
    }

    questionLists.forEach(function (list) {
        list.addEventListener('change', onAnswerSelected);
    });

    const endedCriterionBars = document.querySelectorAll('.bar__progress__ended');
    let totalValues = 0;
    endedCriterionBars.forEach(function (bar) {
        totalValues += parseInt(bar.dataset.criterionPastBarValueId);
    });
    endedCriterionBars.forEach(function(bar) {
        let value = parseInt(bar.dataset.criterionPastBarValueId);
        /*console.log(value, totalValues)*/
        let percentage = Math.round((value / totalValues) * 100);
        bar.style.width = percentage + '%';
        let criterionResult = bar.closest('.diagram__item').querySelector('.diagram__result');
        criterionResult.innerHTML = percentage + '%';
    });

    submitButton.addEventListener('click', function () {
        const unansweredQuestions = Array.from(questionLists).filter(function (list) {
            const questionId = list.id;
            return !selectedAnswers.hasOwnProperty(questionId) || !selectedAnswers[questionId];
        });

        if (unansweredQuestions.length > 0) {
            console.log('Error: not all questions are marked');
            const firstUnansweredQuestion = unansweredQuestions[0];
            firstUnansweredQuestion.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        const answers = [];
        questionLists.forEach(function (list) {
            const questionId = list.id;
            const selectedAnswer = selectedAnswers[questionId] || null;
            answers.push(selectedAnswer);
        });

        const sessionUUID = sessionStorage.getItem('sessionUUID');
        const url = new URL(window.location.href);
        url.searchParams.set('gu', sessionUUID);
        console.log(url)
        let userUuid;
        if (userUuidTag) {
            userUuid = userUuidTag;
        } else {
            userUuid = sessionStorage.getItem('sessionUUID');
        }
        $.post({
            url: url,
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                'request_type': 'new_walkthrough',
                'test_id': testId,
                'sender_uuid': userUuid,
                'selected_answers': answers
            },
            success: function (response) {
                console.log(response)
                console.log('status ' + response.status)
                console.log('data ' + response.data)
                console.log('message ' + response.message)
                if (response && response.status === 200) {
                    $('#unique__result').html(response.message);
                    $('#test__results').css('display', 'flex')
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
                    if (testEndedResult) {
                        testEndedResult.parentNode.removeChild(testEndedResult);
                    }
                    console.log('Success');
                    sessionStorage.removeItem(testId);
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