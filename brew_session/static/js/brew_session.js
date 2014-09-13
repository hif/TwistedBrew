$(function() {
    get_brew_session_selection();
});
function get_brew_session_selection() {
    $.ajax({
        url: "/brew_session/brew_session_selection/",
        type: 'POST',
        data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
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

function show_brew_session_selection(data){
    $('#brew_session_selection').html(data);
}

function show_brew_session_data(data){
    $('#brew_session_data').html(data);
}