document.addEventListener('DOMContentLoaded', function () {
    const CategoryRadios = document.querySelectorAll('input[name="select_category"]');
    const CategoryReset = document.getElementById('category__reset');
    const CriterionReset = document.getElementById('criterion__reset');
    const CriterionRadios = document.querySelectorAll('input[name="select_criterion"]');
    const SortingReset = document.getElementById('sorting__reset');
    const SortingRadios = document.querySelectorAll('input[name="select_sorting"]');

    const currentUrl = new URL(window.location.href);
    const csrfToken = $('meta[name=csrf-token]').attr('content');
    let criterion_type = null;
    let sorting_type = null;
    let category_type = null;

    $('input[name="select_criterion"]').change(function() {
        criterion_type = $('input[name="select_criterion"]:checked').val();
    });
    $('input[name="select_sorting"]').change(function() {
        sorting_type = $('input[name="select_sorting"]:checked').val();
    });
    $('input[name="select_category"]').change(function() {
        category_type = $('input[name="select_category"]:checked').val();
    });

    CriterionReset.addEventListener('click', function (){
        CriterionRadios.forEach(radio => radio.checked = false);
        criterion_type = null;
    });
    SortingReset.addEventListener('click', function (){
        SortingRadios.forEach(radio => radio.checked = false);
        sorting_type = null;
    });
    CategoryReset.addEventListener('click', function () {
        CategoryRadios.forEach(radio => radio.checked = false);
        category_type = null;
    });

    $('#submit__button').on('click', function () {
        const params = new URLSearchParams();

        if (criterion_type !== null) {
            params.append('criterion_type', criterion_type);
        }
        if (sorting_type !== null) {
            params.append('sorting_type', sorting_type);
        }
        if (category_type !== null) {
            params.append('category_type', category_type);
        }

        if (params.toString()) {
            window.location.href = `${currentUrl.origin}${currentUrl.pathname}?${params.toString()}`;
            $.ajax({
                type: "POST",
                headers: {
                    'X-CSRFToken': csrfToken
                },
                url: currentUrl,
                data: {
                    'request_type': 'advanced_search',
                    'criterion_type': criterion_type,
                    'sorting_type': sorting_type,
                    'category_type': category_type,
                },
                success: function (response) {
                    console.log('success')
                },
                error: function (xhr, status, error) {
                    console.error('Error during sending POST request:', error);
                }
            });
        }
    });
});
