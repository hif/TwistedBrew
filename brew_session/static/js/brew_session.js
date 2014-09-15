$(function() {
    get_brew_session_selection();
});
function get_brew_session_selection() {
    $.ajax({
        url: "/brew_session/brew_session_selection/",
        type: 'POST',
        data: {'init_brew_selection': $('input[name=init_brew_selection]').val(), 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_brew_session_selection,
        dataType: 'html'
    });
}
function get_brew_session_data(pk){
    $.ajax({
            url: "/brew_session/brew_session_data/",
        type: 'POST',
        data: {'pk': pk, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_brew_session_data,
        dataType: 'html'
    });
}
function get_create_session(){
    $.ajax({
        url: "/brew_session/brew_session_create/",
        type: 'GET',
        success: show_brew_session_data,
        dataType: 'html'
    });
}
function get_delete_session(pk){
    $.ajax({
        url: "/brew_session/brew_session_delete/" + pk + "/",
        type: 'GET',
        success: show_brew_session_data,
        dataType: 'html'
    });
}
function get_update_session(pk){
    $.ajax({
        url: "/brew_session/brew_session_update/" + pk + "/",
        type: 'GET',
        success: show_brew_session_data,
        dataType: 'html'
    });
}
function get_update_session_detail(pk){
    $.ajax({
        url: "/brew_session/brew_session_detail_update/" + pk + "/",
        type: 'GET',
        success: show_brew_session_data,
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
        url: "/brew_session/start_session_detail/",
        type: 'POST',
        data: {'worker_id': worker_id, 'session_detail_id': session_detail_id, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: session_detail_started,
        dataType: 'html'
    });
}

function send_brewmaster(command){
    $.ajax({
        url: "/brew_session/send_brewmaster/",
        type: 'POST',
        data: {'command': command, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: alert_message,
        dataType: 'html'
    });
}

function send_brewworker(command, worker_id){
    $.ajax({
        url: "/brew_session/send_brewworker/",
        type: 'POST',
        data: {'command': command, 'worker_id': worker_id, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: alert_message,
        dataType: 'html'
    });
}

function show_brew_session_selection(data){
    $('#brew_session_selection').html(data);
}

function show_brew_session_data(data){
    $('#brew_session_data').html(data);
}
function session_detail_started(data){
    alert(data);
}
function alert_message(data){
    alert(data);
}