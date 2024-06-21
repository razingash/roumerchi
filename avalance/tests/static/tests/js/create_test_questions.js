$(document).ready(function() {
    let answers_counter = 0;
    const answers_forms_amount = parseInt($('#id_questionanswerchoice_set-TOTAL_FORMS').val());
    $('#add_question_button').click(function() {
        const totalForms = parseInt($('#id_testquestion_set-TOTAL_FORMS').val());
        if (!isNaN(totalForms)) {
            const form_idx = totalForms;
            const new_form = $('#empty_form').clone().removeAttr('id').removeClass('empty-form');
            new_form.find('[for^="id_testquestion_set-"]').each(function(){
                const new_for = $(this).attr('for').replace('__prefix__', form_idx);
                $(this).attr('for', new_for);
            });
            new_form.find('[id^="id_testquestion_set-"]').each(function(){
                const new_id = $(this).attr('id').replace('__prefix__', form_idx);
                $(this).attr('id', new_id);
                const new_name = $(this).attr('name').replace('__prefix__', form_idx);
                $(this).attr('name', new_name);
                $(this).val('');
            });
            new_form.appendTo('#questions_formset').show();
            for (let i = 0; i < answers_forms_amount; i++) {
                const new_form_2 = $('#empty_form_2').clone().removeAttr('id').removeClass('empty-form');

                new_form_2.find('[for^="id_questionanswerchoice_set-"]').each(function(){
                    const new_for = $(this).attr('for').replace('__prefix__', answers_counter);
                    $(this).attr('for', new_for);
                });
                new_form_2.find('[id^="id_questionanswerchoice_set-"]').each(function(){
                    const new_id = $(this).attr('id').replace('__prefix__', answers_counter);
                    $(this).attr('id', new_id);
                    const new_name = $(this).attr('name').replace('__prefix__', answers_counter);
                    $(this).val('');
                    $(this).attr('name', new_name);
                });

                new_form_2.appendTo('#questions_formset').show();
                answers_counter++;
            }
            $('#id_testquestion_set-TOTAL_FORMS').val(totalForms + 1);
        }
    });
    $('#delete_question_button').click(function() {
        const totalForms = parseInt($('#id_testquestion_set-TOTAL_FORMS').val());
        if (!isNaN(totalForms) && totalForms > 0) {
            $('#id_testquestion_set-TOTAL_FORMS').val(totalForms - 1);
            for (let i=-1; i < answers_forms_amount; i++) {
                $('#questions_formset').children('.empty_form').last().remove();
                $('#questions_formset').children('.form__row').last().find('[name$="-DELETE"]').prop('checked', true);
            }
            answers_counter -= answers_forms_amount;
        } else {
            $('#id_testquestion_set-TOTAL_FORMS').val(0);
            answers_counter = 0;
        }
    });
});
