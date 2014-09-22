
function message_delete(message_id, table_row){
    $.ajax({
        url: "/message_delete/" + message_id + "/",
        type: 'GET',
    });
    removeTableRow(table_row)
}
function fake(){return 0}