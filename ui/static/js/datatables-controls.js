$(document).ready(function () {
    let currentPageNumber = 1;
    let rowsPerPageLimit = 10;
    let searchQuery = "";
    let sortColumnIndex = 0;
    let isSortAscending = true;
    const sortUpIcon = `
    <svg class="sort-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-up-fill" viewBox="0 0 16 16">
        <path d="m7.247 4.86-4.796 5.481c-.566.647-.106 1.659.753 1.659h9.592a1 1 0 0 0 .753-1.659l-4.796-5.48a1 1 0 0 0-1.506 0z"/>
    </svg>
    `;
    const sortDownIcon = `
    <svg class="sort-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-down-fill" viewBox="0 0 16 16">
        <path d="M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z"/>
    </svg>
    `;
    const defaultSortIcon = `
    <svg class="sort-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-up" viewBox="0 0 16 16">
        <path d="M3.204 11h9.592L8 5.519zm-.753-.659 4.796-5.48a1 1 0 0 1 1.506 0l4.796 5.48c.566.647.106 1.659-.753 1.659H3.204a1 1 0 0 1-.753-1.659"/>
    </svg>
    `;

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
                        return $("<tr>").append(
                            row.map(cell => {
                                const formattedCell = (typeof cell === "number") ? cell.toFixed(10) : cell || '';
                                return $("<td>").text(formattedCell);
                            })
                        );
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