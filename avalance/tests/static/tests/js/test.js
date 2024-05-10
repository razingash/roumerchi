document.addEventListener('DOMContentLoaded', function () {
    const testWalkthrough = document.getElementById('test__walkthrough');
    const testDescription = document.getElementById('test__description');
    const buttonStart = document.querySelector('.button__start');
    const buttonBack = document.querySelector('.back_to_description');

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

    const questionLists = document.querySelectorAll('.quetions__list');

    questionLists.forEach(function (list) {
        list.addEventListener('change', onAnswerSelected);
    });

    const currentUrl = window.location.href
    const csrfToken = $('meta[name=csrf-token]').attr('content');
    const userId = 1
    const testId = $('meta[name="test-id"]').attr('content');
    $('.submit').on('click', function () {
        $.post({
            url: currentUrl,
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                'request_type': 'new_walkthrough',
                'test_id': testId,
                'sender_id': userId
            },
            success: function (response) {
                console.log('success')
            },
            error: function (xhr, status, error) {
                console.error('Error during sending POST request:', error);
            }
        });
    });
});