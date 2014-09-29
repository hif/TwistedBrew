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
    setTimeout(operations_timer, operations_interval);
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
    $('#selected_session_details').html(data);
    //update_operations($('#available_sessions').val());
}
function show_session_reset_message(data){
    alert(data);
}
function show_session_archive_message(data){
    alert(data);
    window.location.href = "/session/session_dashboard/"
}
function session_detail_started(data){
    //alert(data);
}
function alert_message(data){
    //alert(data);
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
    clear_operations()
    start_session_detail($('#available_workers').val(),get_selected_session_detail_id());
    close_worker_selection()
}
function close_worker_selection(){
    $('#worker_selection')[0].style.visibility = "hidden";
}
function update_operations(pk){
    $.ajax({
        url: "/session/session_work_status/" + pk,
        type: 'GET',
        data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: set_operations,
        dataType: 'json'
    });
}
function clear_operations(){
    var ops = null;
    ops = $('.operation_pause');
    for( var n = 0 ; n < ops.length ; n++){
        ops[n].style.visibility="hidden";
        ops[n].firstElementChild.firstElementChild.innerHTML="";
    }
    ops = $('.operation_resume');
    for( var n = 0 ; n < ops.length ; n++){
        ops[n].style.visibility="hidden";
        ops[n].firstElementChild.firstElementChild.innerHTML="";
    }
    ops = $('.operation_reset');
    for( var n = 0 ; n < ops.length ; n++){
        ops[n].style.visibility="hidden";
        ops[n].firstElementChild.firstElementChild.innerHTML="";
    }
}

var last_active_detail = -1;
var last_worker_status = -1;
function set_operations(work_status){
    var active_detail = +work_status.active_detail;
    var worker_status = +work_status.worker_status;
    if(active_detail == last_active_detail && worker_status == last_worker_status){
        return;
    }
    clear_operations();
    if(active_detail > 0){
        var ops = $('.operation_assign_worker');
        for( var n = 0 ; n < ops.length ; n++){
            ops[n].style.visibility="hidden";
            ops[n].firstElementChild.firstElementChild.innerHTML="";
        }
        detail_operations = $('#detail_operations_' + work_status.active_detail)[0];
        if(worker_status == 2){
            detail_operations.children[2].style.visibility="visible";
            detail_operations.children[2].firstElementChild.firstElementChild.innerHTML="[resume]"
        }
        else{
            detail_operations.children[1].style.visibility="visible";
            detail_operations.children[1].firstElementChild.firstElementChild.innerHTML="[pause]"
        }
        detail_operations.children[3].style.visibility="visible";
        detail_operations.children[3].firstElementChild.firstElementChild.innerHTML="[reset]"
    }
    else{
        if(last_active_detail != -1)
            get_session_dashboard_details($('#available_sessions').val());
        var ops = $('.operation_assign_worker');
        for( var n = 0 ; n < ops.length ; n++){
            ops[n].style.visibility="visible";
            ops[n].firstElementChild.firstElementChild.innerHTML="[assign worker]";
        }
    }
    last_active_detail = active_detail;
    last_worker_status = worker_status;
}
var operations_interval = 5000;
function operations_timer(){
    if($('#available_sessions').val() > 0){
        update_operations($('#available_sessions').val());
    }
    setTimeout(operations_timer, operations_interval);
}
