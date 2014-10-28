$(function() {
    document.addEventListener("session_selected", change_session, false);
    setTimeout(worker_widget_timer, worker_widget_interval);
});
var worker_session_id = 0;

function change_session(e){
    worker_session_id = e.detail.session_id_elem.value;
    get_worker_widget();
}


function get_worker_widget(){
    $.ajax({
        url: "/session/session_worker_widget/" + worker_session_id,
        type: 'GET',
        data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_worker_widget,
        dataType: 'html'
    });
}

function show_worker_widget(data){
    $('#worker_widget_1').html(data);
}

function worker_widget_timer(){
    if(worker_session_id > 0)
        get_worker_widget();
    setTimeout(worker_widget_timer, worker_widget_interval);
}