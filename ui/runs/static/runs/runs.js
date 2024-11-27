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
    $('.form').on( "change", function() {
        var triggeredForm = $(this);
        var formId = triggeredForm.attr('id');
        var index = formId.split("_").pop();
        console.log(formId,index)
        
        $.ajax({
            url: `/runs/${run_name}/display_not_calculated`,  // The URL for the Django view
            type: 'POST',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()  // CSRF token for security
            },
            data: $(this).serialize(),
            success: function(response) {
                $(`#myCircle_${index}`).attr("fill", response === "incomplete" ? "red" : (response === "complete" ? "green":"yellow"));
            }
        });
    });
    
});

