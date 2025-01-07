$(document).ready(function () {
    let currentPage = 1;
    let perPage = 10;

    function loadTableData(page, rowsPerPage) {
        $.ajax({
            url: RUNS_TABLES_CONTENT_URL,
            data: {
                clean_ids: CLEAN_IDS,
                page: page,
                per_page: rowsPerPage
            },
            type: "GET",
            success: function (response) {
                const columns = response.columns;
                const data = response.data;
                const thead = $("<thead>").append(
                    $("<tr>").append(columns.map(col => $("<th>").text(col)))
                );
                const tbody = $("<tbody>").append(
                    data.map(row => {
                        return $("<tr>").append(row.map(cell => $("<td>").text(cell || '')));
                    })
                );
                $("#datatable").empty().append(thead).append(tbody);

                $('#datatable').DataTable({
                    destroy: true,
                    paging: false,
                    searching: false,
                    info: false, 
                    lengthChange: false,
                    pageLength: rowsPerPage,
                    order: [],
                    language: {
                        search: "Search on Page:"
                    }
                });

                $("#pagination").html('');
                if (response.page > 1) {
                    $("#pagination").append('<button class="btn btn-grey" id="prev-page">Previous</button>');
                }
                if (response.page < response.total_pages) {
                    $("#pagination").append('<button class="btn btn-grey ms-1" id="next-page">Next</button>');
                }

                const startElement = response.start_item;
                const endElement = response.end_item;
                const totalItems = response.total_items;

                $("#page-info").html(
                    `Page ${response.page} of ${response.total_pages}, Showing ${startElement} to ${endElement} of ${totalItems} items`
                );
            }
        });
    }

    loadTableData(currentPage, perPage);

    $(document).on("click", "#prev-page", function () {
        if (currentPage > 1) {
            currentPage--;
            loadTableData(currentPage, perPage);
        }
    });
    $(document).on("click", "#next-page", function () {
        currentPage++;
        loadTableData(currentPage, perPage);
    });

    $(document).on('change', '#rowsPerPage', function() {
        const newRowsPerPage = $(this).val();
        const currentStartItem = (currentPage - 1) * perPage + 1; 
        
        perPage = newRowsPerPage;
        currentPage = Math.ceil(currentStartItem / newRowsPerPage);

        loadTableData(currentPage, perPage);
    });
    $(document).on('change', '#tables_dropdown', function() {
        window.location.href = $(this).val()
    })
});