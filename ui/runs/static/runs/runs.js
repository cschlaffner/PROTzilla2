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

    /*// control each step-adding section visibility
    let addStepsState = JSON.parse(sessionStorage.getItem("addStepsState")) || {};
    // hide add-step section per default
    $('id^="add_steps_div_"]').each(function() {
        let section = $(this);
        let sectionId = section.id; 

        // Get the collapse state for this section from the stored addStepsState
        let isCollapsed = addStepsState[sectionId] === 'collapsed';

        // Set the initial visibility based on the state
        if (isCollapsed) {
            section.removeClass('show');
            section.find('.toggleChevronAddStep').removeClass('rotate-icon');
        } else {
            section.addClass('show');
            section.find('.toggleChevronAddStep').addClass('rotate-icon');
        }

        // Attach click event to toggle button
        section.find('.toggleChevronAddStep').on('click', function() {
            $(this).toggleClass('rotate-icon');
            let currentlyCollapsed = $(this).attr('aria-expanded') === 'false';

            // Update the addStepsState object with the new state for this section
            addStepsState[sectionId] = currentlyCollapsed ? 'collapsed' : 'expanded';

            // Save the updated state object to sessionStorage
            sessionStorage.setItem("addStepsState", JSON.stringify(addStepsState));
        });
    });*/

    // control sidebar visibility
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

    // control file input text
    $(document).on('change', '.file-input', function() {
        let id = $(this).attr("id");
        $('#chosen-' + id).text(this.files[0].name);
    });


    // control calculate buttons in footer
    $('#calculate_parameters_submit_form_plot').click(function() {
        $("#calc_form_plot").submit();
    });
    $('#calculate_parameters_submit_form').click(function() {
        $("#calc_form_method").submit();
    });

    // calculate button spinner
    $('.calculateSpinner').on('click', function() {        
        // Change button content to show 'Calculating...' with a spinner
        $(this).html(`
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Calculating...
        `);
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

    /*function loadAccordionState() {
        const panels = JSON.parse(localStorage.getItem("accordionState")) || [];
        $(".collapse").each(function () {
            const panel = $(this);
            const button = document.querySelector(`[data-bs-target="#${panel.attr("id")}"]`);
            if (panel.length) {
                panel.addClass("show"); 
                if (panels.includes(panel.attr("id"))) {
                    // Expand the panel
                    if (button) {
                        const icon = button.id === 'sidebar-accordion'
                            ? button.querySelectorAll('svg')[1] // second svg to skip section icon
                            : button.querySelector('svg');
                        if (icon) icon.classList.add("rotate-icon");
                    }
                } else {
                    //panel.removeClass("show"); // Collapse the panel
                    if (button) {
                        const icon = button.id === 'sidebar-accordion'
                            ? button.querySelectorAll('svg')[1]
                            : button.querySelector('svg');
                        if (icon) icon.classList.remove("rotate-icon");
                    }
                }
            }
        });
    }*/
        

    loadAccordionState();

    // event listeners save collapse state on show/hide to local storage
    $(".collapse").on("shown.bs.collapse", saveAccordionState);
    $(".collapse").on("hidden.bs.collapse", saveAccordionState);

    // event listeners for all add-steps buttons to handle drop-down arrow
    document.querySelectorAll('#add-steps-button, #sidebar-accordion').forEach(button => {
        const targetId = button.getAttribute('data-bs-target');
        const targetElement = document.querySelector(targetId);

        // Listen for collapse events
        targetElement.addEventListener('show.bs.collapse', () => {
            const icon = button.id === 'sidebar-accordion' 
                ? button.querySelectorAll('svg')[1] // second svg to skip section icon
                : button.querySelector('svg');
            icon.classList.add('rotate-icon');
        });
    
        targetElement.addEventListener('hide.bs.collapse', () => {
            const icon = button.id === 'sidebar-accordion' 
                ? button.querySelectorAll('svg')[1] // second svg to skip section icon
                : button.querySelector('svg');
            icon.classList.remove('rotate-icon');
        });
    });
});
