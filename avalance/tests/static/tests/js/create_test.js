$(document).ready(function() {
    $('#add_criterion_button').click(function() {
        const totalForms = parseInt($('#id_testcriterion_set-TOTAL_FORMS').val());
        if (!isNaN(totalForms)) {
            const form_idx = totalForms;
            const new_form = $('#empty_form').clone().removeAttr('id').removeClass('empty-form');
            new_form.find('[for^="id_testcriterion_set-"]').each(function(){
                const new_for = $(this).attr('for').replace('__prefix__', form_idx);
                $(this).attr('for', new_for);
            });
            new_form.find('[id^="id_testcriterion_set-"]').each(function(){
                const new_id = $(this).attr('id').replace('__prefix__', form_idx);
                $(this).attr('id', new_id);
                const new_name = $(this).attr('name').replace('__prefix__', form_idx);
                $(this).attr('name', new_name);
                $(this).val('');
            });
            new_form.appendTo('#criterions_formset').show();
            $('#id_testcriterion_set-TOTAL_FORMS').val(totalForms + 1);
        }
    });
    $('#delete_criterion_button').click(function() {
        const totalForms = parseInt($('#id_testcriterion_set-TOTAL_FORMS').val());
        if (!isNaN(totalForms) && totalForms > 2) {
            $('#id_testcriterion_set-TOTAL_FORMS').val(totalForms - 1);
            $('#criterions_formset').children('.empty_form').last().remove();
            $('#criterions_formset').children('.form__row').last().find('[name$="-DELETE"]').prop('checked', true);
        } else {
            $('#id_testcriterion_set-TOTAL_FORMS').val(2);
        }
    });

    $('#add_result_button').click(function() {
        const totalForms = parseInt($('#id_testuniqueresult_set-TOTAL_FORMS').val());
        if (!isNaN(totalForms)) {
            const form_idx = totalForms;
            const new_form = $('#empty_form_2').clone().removeAttr('id').removeClass('empty-form');
            new_form.find('[for^="id_testuniqueresult_set-"]').each(function(){
                const new_for = $(this).attr('for').replace('__prefix__', form_idx);
                $(this).attr('for', new_for);
            });
            new_form.find('[id^="id_testuniqueresult_set-"]').each(function(){
                const new_id = $(this).attr('id').replace('__prefix__', form_idx);
                $(this).attr('id', new_id);
                const new_name = $(this).attr('name').replace('__prefix__', form_idx);
                $(this).attr('name', new_name);
                $(this).val('');
            });
            new_form.appendTo('#unique_results_formset').show();
            $('#id_testuniqueresult_set-TOTAL_FORMS').val(totalForms + 1);
        }
    });
    $('#delete_result_button').click(function() {
        const totalForms = parseInt($('#id_testuniqueresult_set-TOTAL_FORMS').val());
        if (!isNaN(totalForms) && totalForms > 2) {
            $('#id_testuniqueresult_set-TOTAL_FORMS').val(totalForms - 1);
            $('#unique_results_formset').children('.empty_form').last().remove();
            $('#unique_results_formset').children('.form__row').last().find('[name$="-DELETE"]').prop('checked', true);
        } else {
            $('#id_testuniqueresult_set-TOTAL_FORMS').val(2);
        }
    });
});