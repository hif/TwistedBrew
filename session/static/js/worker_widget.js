$(function() {
    get_worker_widget(3, 1);
});

function get_worker_widget(worker_id, session_detail_id){
    $.ajax({
        url: "/session/worker_widget/" + worker_id + "/" + session_detail_id,
        type: 'GET',
        data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_worker_widget,
        dataType: 'html'
    });
}

function show_worker_widget(data){
    $('#worker_widget_1').html(data);
}