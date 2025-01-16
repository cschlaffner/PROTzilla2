$(document).ready(function () {
    let currentPageNumber = 1;
    let rowsPerPageLimit = 10;
    let searchQuery = "";
    let sortColumnIndex = 0;
    let isSortAscending = true;
    const sortUpIcon = '<i class="sort-icon bi bi-caret-up-fill ms-2"></i>';
    const sortDownIcon = '<i class="sort-icon bi bi-caret-down-fill ms-2"></i>';
    const defaultSortIcon = '<i class="sort-icon bi bi-caret-up ms-2"></i>';

    function loadTableData({isNewSearch = false, isNewSorting = false} = {}) {
        $.ajax({
            url: RUNS_TABLES_CONTENT_URL,
            data: {
                clean_ids: CLEAN_IDS,
                current_page: currentPageNumber,
                rows_per_page: rowsPerPageLimit,
                is_new_search : isNewSearch,
                search_query: searchQuery,
                is_new_sorting : isNewSorting,
                sorting_column_index : sortColumnIndex,
                is_sort_ascending : isSortAscending,
            },
            type: "GET",
            success: function (response) {
                const columns = response.columns;
                const data = response.data;
                const thead = $("<thead>").append(
                    $("<tr>").append(
                        columns.map(col => $("<th>").text(col).append(defaultSortIcon))
                    )
                );
                const tbody = $("<tbody>").append(
                    data.map(row => {
                        return $("<tr>").append(row.map(cell => $("<td>").text(cell || '')));
                    })
                );
  
                $("#datatable").empty().append(thead).append(tbody);
                initializeDataTable(rowsPerPageLimit);

                updatePagination(response);
                updatePageInfo(response);

                $("#search-btn").html("Search");
            }
        });
    }

    function initializeDataTable(rowsPerPage) {
        $('#datatable').DataTable({
            destroy: true,
            paging: false,
            searching: false,
            info: false,
            lengthChange: false,
            ordering: false,
            pageLength: rowsPerPage,
        });
    }

    function updatePagination(response) {
        const pagination = $("#pagination").empty();
        if (response.page > 1) {
            pagination.append('<button class="btn btn-grey" id="prev-page">Previous Page</button>');
        }
        if (response.page < response.total_pages) {
            pagination.append('<button class="btn btn-grey ms-1" id="next-page">Next Page</button>');
        }
    }

    function updatePageInfo(response) {
        const { start_item, end_item, total_items } = response;
        $("#page-info").html(`Page ${response.page} of ${response.total_pages}, Showing ${start_item} to ${end_item} of ${total_items} items`);
    }
    
    loadTableData();
    
    $(document).on("click", "#prev-page", function () {
        if (currentPageNumber > 1) {
            currentPageNumber--;
            loadTableData();
        }
    });

    $(document).on("click", "#next-page", function () {
        currentPageNumber++;
        loadTableData();
    });

    $(document).on('change', '#rowsPerPage', function() {
        rowsPerPageLimit = $(this).val();
        currentPageNumber = Math.ceil(((currentPageNumber - 1) * rowsPerPageLimit + 1) / rowsPerPageLimit);
        loadTableData();
    });

    $(document).on("click", "#search-btn", function () {
        searchQuery = $("#searchInput").val();
        currentPageNumber = 1;

        $(this).html(`
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Searching...
        `);
        loadTableData({isNewSearch: true});
    });

    $(document).on("click", "#datatable thead th", function () {
        const currentTh = $(this);
        sortColumnIndex = $(this).index();

        
        currentTh.siblings().removeClass("sorted_asc sorted_dec").find(".sort-icon").remove().end().append(defaultSortIcon);
        currentTh.find(".sort-icon").remove();

        if (currentTh.hasClass("sorted_asc")) {
            currentTh.removeClass("sorted_asc").addClass("sorted_dec").append(sortDownIcon);
            isSortAscending = false;
        } else {
            currentTh.removeClass("sorted_dec").addClass("sorted_asc").append(sortUpIcon);
            isSortAscending = true;
        }

        loadTableData({isNewSorting: true});
    });

    $(document).on('change', '#tables_dropdown', function() {
        window.location.href = $(this).val();
    })
});