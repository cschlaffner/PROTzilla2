$( document ).ready(function () {
    let formHasChanged = false;
    const sectionId = document.getElementById('settings-form').dataset.sectionId;

    $("#settings-form :input").on("change input", function () {
        formHasChanged = true;
    });

    $("#cancel, #settings-icon").click(function (e) {
        if(formHasChanged) {
            e.preventDefault();
            $("#unsavedChangesModal").modal("show");
        }
    });

    $("#customFontInput").click(function () {
        $("#customFontRadio").prop("checked", true);
    });

    $(".action-button").each(function () {
        $(this).click(function () {
            const form = document.getElementById("settings-form");
            form.action = $(this).data("action");
            form.submit();
        });
    });
});