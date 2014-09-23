$(function() {
    get_session_selection();
});

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