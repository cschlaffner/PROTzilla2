$(document).ready(function () {
    // control history section visibility
    let collapseState = sessionStorage.getItem('collapseState');
    // hide history section per default
    if (collapseState === 'collapsed' || collapseState === null) {
        $('#collapseHistory').removeClass('show');
        $('#toggleChevron').removeClass('rotate-icon');
    } else {
        $('#collapseHistory').addClass('show');
        $('#toggleChevron').addClass('rotate-icon');
    }

    $('#toggleChevron').click(function() {
        $(this).toggleClass('rotate-icon');
        let isCollapsed = $(this).attr('aria-expanded') === 'false';
        sessionStorage.setItem('collapseState', isCollapsed ? 'collapsed' : 'expanded');

        // resize window to update plotly plots in history to full width
        if (!isCollapsed) {
            window.dispatchEvent(new Event('resize'));
        }
    });

    // control sidebar visibility
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

    // control file input text
    $(document).on('change', '.file-input', function() {
        let id = $(this).attr("id");
        $('#chosen-' + id).text(this.files[0].name);
    });


    //save forms on change
    $('.calc_form').on( "change", function() {
        var triggeredForm = $(this);
        var formId = triggeredForm.attr('id');
        var index = Number(formId.split("_").pop());
        
        $.ajax({
            url: `/runs/${run_name}/update_form`,  // The URL for the Django view
            type: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()  // CSRF token for security
            },
            data: $(this).serialize(),
            success: function(response) {
                for (let i=0; i<response.count; i++) {
                    $(`#calculationIcon_${index+i} img`).attr('src', `${staticUrl}${response.status}_icon.svg`);
                }
                
            }
        });
    });

    // save current state of accordion in sessionStorage
    function saveAccordionState() {
        const panels = [];
        $(".collapse").each(function () {
            if ($(this).hasClass("show")) {
                panels.push(this.id);
            }
        });
        sessionStorage.setItem("accordionState", JSON.stringify(panels));
    }

    // load accordion state from sessionStorage
    function loadAccordionState() {
        const panels = JSON.parse(sessionStorage.getItem("accordionState")) || [];
        panels.forEach(function (panelId) {
            const panel = $("#" + panelId);
            if (panel.length) {
                panel.addClass("show");
            }
        });
    }

    function updateAccordionIcons() {
        $(".collapse").each(function () {
            const panel = $(this);
            const button = document.querySelector(`[data-bs-target="#${panel.attr("id")}"]`);
            if (button) {
                const icon = button.id === 'sidebar-accordion'
                    ? button.querySelectorAll('svg')[1] // second svg to skip section icon
                    : button.querySelector('svg');
                if (panel.hasClass("show")) {
                    if (icon) icon.classList.add("rotate-icon");
                } else {
                    if (icon) icon.classList.remove("rotate-icon");
                }
            }
        });
    }
        
    loadAccordionState();
    updateAccordionIcons();

    // event listeners save collapse state on show/hide to local storage
    $(".collapse").on("hidden.bs.collapse", saveAccordionState);
    $(".collapse").on("shown.bs.collapse hidden.bs.collapse", function () {
        saveAccordionState(); // Save the current state to sessionStorage
        updateAccordionIcons(); // Update icons after state change
    });
    
});

// control calculate button in footer
function onCalculateClick(element) {
    var form = $(".calc_form")[0];

    if (form.checkValidity()) {
        form.submit();

        // show loading spinner on calculate button
        element.innerHTML = `Calculating <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`;
        element.setAttribute('disabled', true);

    } else {
        form.reportValidity();
    }
}
