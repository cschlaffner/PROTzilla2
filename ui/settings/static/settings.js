$( document ).ready(function () {
    $("#customFontInput").click(function () {
        const radio = document.getElementById('customFontRadio');
        const input = document.getElementById('customFontInput');
        radio.checked = true;
    })

    $(".action-button").each(function () {
        $(this).click(function () {
            const form = document.getElementById("settings-form");
            form.action = $(this).data("action");
            form.submit();
        });
    });
});