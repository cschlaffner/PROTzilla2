disable_calc = function (bool) {
    sessionStorage.setItem(run_name + "_disabled_calc", bool)
    $('#calculate_parameters_submit').prop('disabled', bool)
    console.log("disabled_calc", bool)
}

disable_plot = function (bool) {
    sessionStorage.setItem(run_name + "_disabled_plot", bool)
    $('#plot_parameters_submit').prop('disabled', bool)
    console.log("disabled_plot", bool)
}

get_clean_form_data = function (form) {
    let params = new FormData(form);
    params.delete("csrfmiddlewaretoken")
    console.log("form data", params)
    return params
}

set_calc_params = function () {
    let params = get_clean_form_data(document.querySelector('#calc_form'))
    sessionStorage.setItem(run_name + "_calc_params", params.serialize())
    console.log("set calc params", params)
    console.log("set calc params serialized", params.serialize())
    return params
}

set_plot_params = function () {
    let params = get_clean_form_data(document.querySelector('#plot_form'))
    sessionStorage.setItem(run_name + "_plot_params", JSON.stringify(params))
    console.log("plot params", params)
    return params
}

$(document).ready(function () {
    const calc_form = document.querySelector('#calc_form');
    const plot_form = document.querySelector('#plot_form');
    const next_form = document.querySelector('#next_form');
    const back_form = document.querySelector('#back_form');

    if (sessionStorage.getItem(run_name + "_first_load") === "true") {
        disable_calc(false)
        disable_plot(show_plot_button) // not sure if this works correctly!
        sessionStorage.setItem(run_name + "_first_load", "false")
    } else {
        disable_calc(sessionStorage.getItem(run_name + "_disabled_calc"))
        disable_plot(sessionStorage.getItem(run_name + "_disabled_plot"))
    }

    calc_form.addEventListener('submit', function () {
        set_calc_params()
        disable_plot(false)
        disable_calc(true)
        sessionStorage.setItem(run_name + '_calculated', "true")
        sessionStorage.setItem(run_name + "_plotted", "false")
    })

    calc_form.addEventListener('change', function (){
        if (sessionStorage.getItem(run_name + "_calculated") === "true"){
            let current_params = get_clean_form_data(calc_form)
            let calc_params = JSON.parse(sessionStorage.getItem(run_name + "_calc_params"))
            console.log("change calc, calc_params", calc_params)
            for (let [key, value] of calc_params.entries()){
                if (current_params.get(key) !== value){
                    disable_calc(false)
                    disable_plot(true)
                    sessionStorage.setItem(run_name + "_calculated", "false")
                    return
                }
            }
            // all equal
            if (sessionStorage.getItem(run_name + "_plotted")){
                disable_plot(true)
            } // TODO: change event listener on plot form, set "_plotted" to false when change
        }
    })

    plot_form.addEventListener('submit', function (){
        set_plot_params()
        disable_plot(true)
        sessionStorage.setItem(run_name + "_plotted", "true")
    })

    plot_form.addEventListener("change", function () {
        if (sessionStorage.getItem(run_name + "_plotted")){
            let current_params = get_clean_form_data(plot_form)
            let plot_params = JSON.parse(sessionStorage.getItem(run_name + "_plot_params"))
            for (let [key, value] of plot_params.entries()){
                if (current_params.get(key) !== value){
                    disable_plot(false)
                    sessionStorage.setItem(run_name + "_plotted", "false")
                    return
                }
            }
            // same plot params as last plot
            disable_plot(true)
            sessionStorage.setItem(run_name + "_plotted", "true") // this is redundant -> if-case
        }
        else if (sessionStorage.getItem(run_name + "_calculated")){
            disable_plot(false)
        } else {
            disable_plot(true)
        }
    })

    next_form.addEventListener("submit", function () {
        sessionStorage.setItem(run_name + "_first_load", "true")
        sessionStorage.removeItem(run_name + "_calc_params")
        sessionStorage.removeItem(run_name + "_plot_params")
        sessionStorage.removeItem(run_name + "_calculated")
        sessionStorage.removeItem(run_name + "_plotted")
    })

    back_form.addEventListener("submit", function () {
        sessionStorage.setItem(run_name + "_first_load", "true")
        sessionStorage.removeItem(run_name + "_calc_params")
        sessionStorage.removeItem(run_name + "_plot_params")
        sessionStorage.removeItem(run_name + "_calculated")
        sessionStorage.removeItem(run_name + "_plotted")
    })
})
