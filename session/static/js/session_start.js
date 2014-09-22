function get_session_selection() {
    $.ajax({
        url: "/session/session_selection/",
        type: 'POST',
        data: {'init_brew_selection': $('input[name=init_brew_selection]').val(), 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_session_selection,
        dataType: 'html'
    });
}
function get_session_data(pk){
    $.ajax({
            url: "/session/session_data/",
        type: 'POST',
        data: {'pk': pk, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_session_data,
        dataType: 'html'
    });
}
function get_create_session(){
    $.ajax({
        url: "/session/session_create/",
        type: 'GET',
        success: show_session_data,
        dataType: 'html'
    });
}
function get_delete_session(pk){
    $.ajax({
        url: "/session/session_delete/" + pk + "/",
        type: 'GET',
        success: show_session_data,
        dataType: 'html'
    });
}
function get_update_session(pk){
    $.ajax({
        url: "/session/session_update/" + pk + "/",
        type: 'GET',
        success: show_session_data,
        dataType: 'html'
    });
}
function get_update_session_detail(pk){
    $.ajax({
        url: "/session/session_detail_update/" + pk + "/",
        type: 'GET',
        success: show_session_data,
        dataType: 'html'
    });
}
function start_session_detail(worker_id, session_detail_id){
    if(worker_id == 0)
    {
        alert("No worker selected");
        return;
    }
    $.ajax({
        url: "/session/session_detail_start/",
        type: 'POST',
        data: {'worker_id': worker_id, 'session_detail_id': session_detail_id, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: session_detail_started,
        dataType: 'html'
    });
}

function send_master_command(command){
    $.ajax({
        url: "/session/send_master_command/",
        type: 'POST',
        data: {'command': command, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: alert_message,
        dataType: 'html'
    });
}

function send_worker_command(command, worker_id){
    $.ajax({
        url: "/session/send_worker_command/",
        type: 'POST',
        data: {'command': command, 'worker_id': worker_id, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: alert_message,
        dataType: 'html'
    });
}

function show_session_selection(data){
    $('#session_selection').html(data);
}

function show_session_data(data){
    $('#session_data').html(data);
}
function session_detail_started(data){
    alert(data);
}
function alert_message(data){
    alert(data);
}