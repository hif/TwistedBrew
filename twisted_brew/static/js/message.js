
function message_delete(message_id, table_row){
    $.ajax({
        url: "/message_delete/" + message_id + "/",
        type: 'GET',
    });
    removeTableRow(table_row)
}

function removeTableRow(index){
    $("#message_" + index).remove();
}

function fake(){return 0}