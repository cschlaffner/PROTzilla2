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
        console.log("changed");
        let id = $(this).attr("id");
        $('#chosen-' + id).text(this.files[0].name);
    });
});