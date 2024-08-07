document.addEventListener('DOMContentLoaded', function () {
    const testId =  $('meta[name=test-id]').attr('content');
    const url = $('meta[name=test-url]').attr('content');
    const csrfToken = $('meta[name=csrf-token]').attr('content');
    const userUuidTag = $('meta[name=user-uuid]').attr('content');
    $('#verification').on('click', function () {
        $.ajax({
            type: "POST",
            headers: {
                'X-CSRFToken': csrfToken
            },
            url: url,
            data: {
                'csrfmiddlewaretoken': csrfToken,
                'request_type': 'test_validation',
                'test_id': testId,
                'sender_uuid': userUuidTag,
            },
            success: function (response) {
                console.log('success');
                window.location.href = 'http://127.0.0.1:8000/roumerchi/';
            },
            error: function (xhr, status, error) {
                console.error('Error during sending POST request:', error);
            }
        });
    });
});