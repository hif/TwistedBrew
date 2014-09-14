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

function show_brew_session_selection(data){
    $('#brew_session_selection').html(data);
}

function show_brew_session_data(data){
    $('#brew_session_data').html(data);
}