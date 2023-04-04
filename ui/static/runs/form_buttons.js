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
    let formDataArray = form.serializeArray()
    let formDataDict = {};
    for (let i = 0; i < formDataArray.length; i++) {
        let fieldName = formDataArray[i].name;
        let fieldValue = formDataArray[i].value;
        formDataDict[fieldName] = fieldValue;
    }
    console.log("bla")
    console.log("form data", formDataDict)
    delete formDataDict["csrfmiddlewaretoken"]
    return formDataDict
}

set_calc_params = function (form) {
    let params = get_clean_form_data(form)
    sessionStorage.setItem(run_name + "_calc_params", JSON.stringify(params))
    console.log("set calc params", params)
    return params
}

set_plot_params = function (form) {
    let params = get_clean_form_data(form)
    sessionStorage.setItem(run_name + "_plot_params", JSON.stringify(params))
    console.log("set plot params", params)
    return params
}

$(document).ready(function () {
    const calc_form = document.querySelector('#calc_form');
    const plot_form = document.querySelector('#plot_form');
    const next_form = document.querySelector('#next_form');
    const back_form = document.querySelector('#back_form');

    // server gib mir calc_params
    // gib mir plot_params

    if (sessionStorage.getItem(run_name + "_first_load") === "true") {
        console.log("first load")
        disable_calc(false)
        disable_plot(true)
        sessionStorage.setItem(run_name + "_first_load", "false")
    } else {
        console.log("disable plot:", sessionStorage.getItem(run_name + "_disabled_plot"))
        disable_calc(sessionStorage.getItem(run_name + "_disabled_calc"))
        disable_plot(sessionStorage.getItem(run_name + "_disabled_plot"))
    }

    calc_form.addEventListener('submit', function () {
        set_calc_params($(this))
        disable_plot(false)
        disable_calc(true)
        sessionStorage.setItem(run_name + '_calculated', "true")
        sessionStorage.setItem(run_name + "_plotted", "false")
    })

    calc_form.addEventListener('change', function () {
        if (!JSON.parse(sessionStorage.getItem(run_name + "_calc_params"))) {
            return
        }
        let current_params = get_clean_form_data($(this))
        let calc_params = JSON.parse(sessionStorage.getItem(run_name + "_calc_params"))

        for (let key in calc_params) {
            if (calc_params.hasOwnProperty(key)) {
                let value = calc_params[key]
                if (current_params[key] !== value) {
                    disable_calc(false)
                    disable_plot(true)
                    sessionStorage.setItem(run_name + "_calculated", "false")
                    sessionStorage.setItem(run_name + "_plotted", "false")
                    // console.log("unequal: current vs prev")
                    return
                }
            }
        }
        sessionStorage.setItem(run_name + "_calculated", "true")
        disable_calc(true)

        if (sessionStorage.getItem(run_name + "_plotted") === "true") {
            disable_plot(true)
        } else {
            $('#plot_form').trigger("change")
        }

    })

    plot_form.addEventListener('submit', function () {
        set_plot_params($(this))
        disable_plot(true)
        sessionStorage.setItem(run_name + "_plotted", "true")
    })

    plot_form.addEventListener("change", function () {
        console.log("change plot form")

        // if (!JSON.parse(sessionStorage.getItem(run_name + "_plot_params"))) {
        //     return
        // }
        if (!JSON.parse(sessionStorage.getItem(run_name + "_calculated"))) {
            disable_plot(true)
            sessionStorage.setItem(run_name + "_plotted", "false")
            console.log("json parse")
            return
        }

        let current_params = get_clean_form_data($(this))
        let plot_params = JSON.parse(sessionStorage.getItem(run_name + "_plot_params"))

        for (let key in plot_params) {
            if (plot_params.hasOwnProperty(key)) {
                let value = plot_params[key]
                if (current_params[key] !== value) {
                    disable_plot(false)
                    sessionStorage.setItem(run_name + "_plotted", "false")
                    return
                }
            }
        }
        disable_plot(true)
        sessionStorage.setItem(run_name + "_plotted", "true") // this is redundant -> if-case ??
        console.log("end of plot change")
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
