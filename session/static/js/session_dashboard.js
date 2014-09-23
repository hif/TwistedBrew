$(function() {
    get_available_session_options();
});

function show_available_session_options(data){
    $('#available_sessions').html(data);
    $('#available_sessions').selectedIndex = 0;
    if($('#available_sessions').val() > 0){
        get_session_data($('#available_sessions').val());
    }
}

function show_session_data(data){
    $('#charts').html(data);
}
function session_detail_started(data){
    alert(data);
}
function alert_message(data){
    alert(data);
}