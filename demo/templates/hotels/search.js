$(document).ready(function () {
    var celery_task_id;
    var selected_city;
    var modal_alert = function(title, body) {
        $el = $('#modal_alert');
        $el.modal('hide');
        $('#modal_alert .modal-title').html(title);
        $('#modal_alert .modal-body p').html(body);
        $el.modal('show');
    };

    var hotels_grid_options = {
        order: [],
        paging: false,
        scrollY: '50vh',
        scrollCollapse: true,
        select: {
            style:    'multi',
            selector: 'td:first-child'
        },
        dom: 'lfr<"save-btn btn btn-primary btn-sm">tip',
        fnInitComplete: function(){
           $('.save-btn').text('Save selected').click(function(e) {
                e.preventDefault();
                data = $('#hotels_grid').DataTable().rows('.selected').data().toArray();
                if ( data.length ) {
                    $.ajax({
                        type: "POST",
                        url: "/fastapi/save-selected-hotels/",
                        data: JSON.stringify( {city_id: selected_city, data: data} ),
                        contentType: "application/json",
                        processData: false,
                        success: function(data) {
                            modal_alert('SUCCESS', 'Data is sent to Consumer and will be stored in Database, see results <a href="{{ selected_hotels_url }}">here</a>')
                        },
                        error: function(data) {
                            modal_alert('FAILURE', 'Something went wrong, try to repeat later')
                        }
                    });
                }
                else {
                    modal_alert('WARNING', 'Please select rows')
                }
            })
        },
        columns: [
            { data: null, targets: 0, defaultContent: '', orderable: false, className: 'select-checkbox' },
            { data: 'id', className: "text-right" },
            { data: 'name' },
            { data: 'stars', className: "text-right" },
            { data: 'rank', className: "text-right" },
            { data: 'reviews', className: "text-right" },
            { data: 'description', render: function ( data, type, row ) {
                subs = data != null && data.length > 20 ? data.substr( 0, 20 ) +'…' : data;
                return '<span title="' + data + '">' + subs + '</span>'} }
        ]
    };
    var hotels_table = $('#hotels_grid');
    hotels_datatable = hotels_table.DataTable(hotels_grid_options);

    ws_protocol = location.protocol == 'https:' ? 'wss' : 'ws'
    let ws_url = ws_protocol + '://' + window.location.host + '/fastapi/ws';
    var ws = new WebSocket(ws_url);
    ws.onmessage = function(event) {
        const msg = $.parseJSON(event.data);
        if (msg.hasOwnProperty('tasks')) {
            if (msg.tasks && msg.tasks.hasOwnProperty(celery_task_id)) {
                task_data = msg.tasks[celery_task_id];
                $('#master_task_status').text(task_data.overview.master_task_status);
                if (task_data.overview.hasOwnProperty('child_tasks_statuses')) {
                    $('#pending').text(task_data.overview.child_tasks_statuses.PENDING);
                    $('#success').text(task_data.overview.child_tasks_statuses.SUCCESS);
                    $('#failure').text(task_data.overview.child_tasks_statuses.FAILURE);
                    $('#total').text(task_data.overview.child_tasks_statuses.TOTAL);
                };
                $('#task_progress').css({width: task_data.progress + '%'});

                if (task_data.progress == 100) {
                    $('.tasks-loading').removeClass('spinner-border');
                    hotels_datatable.clear();
                    hotels_datatable.rows.add(task_data.results).draw();

                    if (task_data.overview.master_task_status == 'FAILURE') {
                        modal_alert('FAILURE', 'Something went wrong, probably source site is unavailable,  try to repeat later');
                    }
                }
            }
        }
    };

    $("#search_celery").click(function(e) {
        e.preventDefault();
        $('.results-loading').removeClass('spinner-border');
        $('.tasks-loading').addClass('spinner-border');
        $('#celery_tasks').slideDown(200);
        $('#master_task_status').text();
        $('#pending,#success,#failure,#total').empty();
        $('#task_progress').css({width: '0%'});
        hotels_datatable.clear()
        hotels_datatable.draw();

        selected_city = $("[name=city]").chosen().val();
        data = {
            "query": $("[name=city] option:selected").text(),
            "page": $("input[name=page]").val()
        };

        $.ajax({
            type: "POST",
            url: "/fastapi/search-hotels-using-celery/",
            data: JSON.stringify( data ),
            contentType: "application/json",
            processData: false,
            success: function(data) {
                celery_task_id = data
            },
            error: function(data) {
                $('.tasks-loading').removeClass('spinner-border');
                modal_alert('FAILURE', 'Something went wrong, try to repeat later');
            }
        });
    })

    $("#search_asyncio").click(function(e) {
        e.preventDefault();
        $('#celery_tasks').slideUp(200);
        $('.tasks-loading').removeClass('spinner-border');
        hotels_datatable.clear().draw();

        selected_city = $("[name=city]").chosen().val();
        data = {
            "query": $("[name=city] option:selected").text(),
            "page": $("input[name=page]").val()
        };

        $('.results-loading').addClass('spinner-border');
        $.ajax({
            type: "POST",
            url: "/fastapi/search-hotels-using-asyncio/",
            data: JSON.stringify( data ),
            contentType: "application/json",
            processData: false,
            success: function(data) {
                $('.results-loading').removeClass('spinner-border');
                hotels_datatable.rows.add(data).draw()
            },
            error: function(data) {
                $('.results-loading').removeClass('spinner-border');
                modal_alert('FAILURE', 'Something went wrong, probably source site is unavailable, try to repeat later');
            }
        });
    });
})
