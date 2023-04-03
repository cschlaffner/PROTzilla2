// script to deactivate plot button if calc_params change so a new plot cannot be generated with old data
let isFirstFormSubmitted = false;
let calc_params = null;
let disabled_calc = false

$(document).ready(function () {
    const calc_form = document.querySelector('#calc_form');

    calc_params = new FormData(calc_form);
    calc_params.delete("csrfmiddlewaretoken")

    calc_form.addEventListener('submit', function () {
        isFirstFormSubmitted = true;
        calc_params = new FormData(calc_form);
        calc_params.delete("csrfmiddlewaretoken")
        $('#plot_parameters_submit').prop('disabled', false);
        disabled_calc = true
        $('#calculate_parameters_submit').prop('disabled', disabled_calc);
        alert("enable plot, disable calc")
    });

    calc_form.addEventListener('change', function () {
        console.error("change")
        let current_params = new FormData(calc_form);
        current_params.delete("csrfmiddlewaretoken")

        let plot_submit = $('#plot_parameters_submit');
        let calc_submit = $('#calculate_parameters_submit')
        for (let [key, value] of calc_params.entries()) {
            if (current_params.get(key) !== value) {
                plot_submit.prop('disabled', true);
                disabled_calc = false
                calc_submit.prop('disabled', disabled_calc)
                console.log("disable plot, enable calc")
                return
            }
        }
        plot_submit.prop('disabled', false);
        disabled_calc = true
        calc_submit.prop('disabled', disabled_calc);
        console.log("enable plot, disable calc")
    });
});
