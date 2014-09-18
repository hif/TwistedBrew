var tableSize = 10;
var latest_timestamp = new Date().getTime();
live_feed_timer_interval = 5000

$(function() {
    get_table_head();
    get_table_rows(0, tableSize);
    setTimeout(live_feed_timer, live_feed_timer_interval);
});
function setTableHead(head_html){
    $("#message_live_feed_table thead").html(head_html);
}
function addTableRow(row_html){
    $(row_html).prependTo($("#message_live_feed_table tbody"));
}
function removeTableRow(){
    if($("#message_live_feed_table tbody tr").length >= tableSize){
        $("#message_live_feed_table tbody tr:last").remove();
    }
}
function updateTableRows(row_list){
    for( var n = row_list.length - 1 ; n >= 0 ; n--){
        removeTableRow()
        addTableRow(row_list[n]);
    }
    if($("#message_live_feed_table tbody tr").length == 0){
        addTableRow("<tr><td colspan=3><i>No messages</i></td></tr>")
    }
}
function get_table_head(){
    $.ajax({
            url: "/message_head/",
        type: 'GET',
        success: setTableHead,
        dataType: 'html'
    });
}
function get_table_rows(timestamp, max){
    $.ajax({
            url: "/message_rows/" + timestamp + "/" + max + "/",
        type: 'GET',
        success: updateTableRows,
        dataType: 'json'
    });
}
function live_feed_timer(){
    get_table_rows(latest_timestamp, tableSize);
    latest_timestamp = new Date().getTime();
    setTimeout(live_feed_timer, live_feed_timer_interval);
}