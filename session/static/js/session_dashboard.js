$(function() {
    session_selected_event = new CustomEvent(
        "session_selected",{
            detail: {
                session_id_elem: $('#available_sessions')[0],
            },
            bubbles: true,
            cancelable: true
        }
    );
    get_available_session_options();
});
var selected_session_detail_id = 0;
var session_selected_event=null
function set_selected_session_detail_id(id){
    selected_session_detail_id = id;
}
function get_selected_session_detail_id(id){
    return selected_session_detail_id;
}

function show_available_session_options(data){
    $('#available_sessions').html(data);
    $('#available_sessions').selectedIndex = 0;
    if($('#available_sessions').val() > 0){
        get_session_dashboard_details($('#available_sessions').val());
    }

}
function get_session_dashboard_details(pk){
    $.ajax({
        url: "/session/session_dashboard_details/",
        type: 'POST',
        data: {'pk': pk, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_session_details,
        dataType: 'html'
    });
    document.dispatchEvent(session_selected_event);
}
function show_session_details(data){
    $('#charts').html(data);
}
function session_detail_started(data){
    alert(data);
}
function alert_message(data){
    alert(data);
}
function show_available_worker_options(data){
    $('#available_workers').html(data);
    $('#available_workers').selectedIndex = 0;
}
function open_worker_selection(detail_id, worker_type){
    set_selected_session_detail_id(detail_id);
    get_available_worker_options(worker_type);
    $('#worker_selection')[0].style.visibility = "visible";
}
function start_worker_from_selection(){
    start_session_detail($('#available_workers').val(),get_selected_session_detail_id());
    $('#detail_operations_' + get_selected_session_detail_id()).html('')
    close_worker_selection()
}
function close_worker_selection(){
    $('#worker_selection')[0].style.visibility = "hidden";
}