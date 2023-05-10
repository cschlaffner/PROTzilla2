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
    });


    // control sidebar visibility
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

    
    // show file name on upload
    $('#file_path').on('change', function(){
        $('#file-chosen').text(this.files[0].name);
    })
});