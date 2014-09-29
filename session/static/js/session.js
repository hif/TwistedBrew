function get_session_selection() {
    $.ajax({
        url: "/session/session_selection/",
        type: 'POST',
        data: {'init_brew_selection': $('input[name=init_brew_selection]').val(), 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_session_selection,
        dataType: 'html'
    });
}
function get_available_session_options() {
    $.ajax({
        url: "/session/session_available_options/",
        type: 'GET',
        data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_available_session_options,
        dataType: 'html'
    });
}
function get_available_worker_options(worker_type) {
    $.ajax({
        url: "/session/worker_available_options/",
        type: 'POST',
        data: {'worker_type': worker_type, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_available_worker_options,
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
function get_reset_session(pk){
    $.ajax({
        url: "/session/session_reset/" + pk,
        type: 'GET',
        success: show_session_reset_message,
        dataType: 'html'
    });
}
function get_archive_session(pk){
    $.ajax({
        url: "/session/session_archive/" + pk,
        type: 'GET',
        success: show_session_archive_message,
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

function send_detail_command(command, session_detail_id){
    $.ajax({
        url: "/session/send_session_detail_command/",
        type: 'POST',
        data: {'command': command, 'session_detail_id': session_detail_id, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
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
