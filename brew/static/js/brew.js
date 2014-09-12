$(function() {
    get_brew_selection();
});
function get_brew_selection() {
    $.ajax({
        url: "/brew/brew_selection/",
        type: 'POST',
        data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_brew_selection,
        dataType: 'html'
    });
}
function get_brew_data(pk){
    $.ajax({
        url: "/brew/brew_data/",
        type: 'POST',
        data: {'pk': pk, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: show_brew_data,
        dataType: 'html'
    });
}

function show_brew_selection(data){
    $('#brew_selection').html(data);
}

function show_brew_data(data){
    $('#brew_data').html(data);
}