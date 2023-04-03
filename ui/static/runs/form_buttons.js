// script to deactivate plot button if calc_params change so a new plot cannot be generated with old data
let isFirstFormSubmitted = false;
let calc_params = null;

get_clean_form_data = function (form) {
    let params = new FormData(form);
    params.delete("csrfmiddlewaretoken")
    return params
}

disable_calc = function (bool) {
    sessionStorage.setItem("disabled_calc", bool)
    $('#calculate_parameters_submit').prop('disabled', bool);
}

$(document).ready(function () {
    const calc_form = document.querySelector('#calc_form');
    calc_params = get_clean_form_data(calc_form)
    disable_calc(sessionStorage.getItem("disabled_calc"))

    calc_form.addEventListener('submit', function () {
        isFirstFormSubmitted = true;
        calc_params = get_clean_form_data(calc_form)

        $('#plot_parameters_submit').prop('disabled', false);

        disable_calc(true)
        alert("enable plot, disable calc")
    });

    calc_form.addEventListener('change', function () {
        console.error("change")
        let current_params = get_clean_form_data(calc_form)

        let plot_submit = $('#plot_parameters_submit');
        for (let [key, value] of calc_params.entries()) {
            if (current_params.get(key) !== value) {
                plot_submit.prop('disabled', true);
                disable_calc(false)
                console.log("disable plot, enable calc")
                return
            }
        }
        plot_submit.prop('disabled', false);
        disable_calc(true)
        console.log("enable plot, disable calc")
    });
});
