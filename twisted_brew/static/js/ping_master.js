var pong_pending = false;

function ping_master(){
    if(pong_pending)
        return;
    pong_pending = true;
    $("#ping_master_label")[0].innerText = "pinging master...";
    $.ajax({
            url: "/ping_master/",
        type: 'GET',
        success: pong,
        error: pong,
        dataType: 'html'
    });
}

function pong(data){
    pong_pending = false;
    if(data != "pong")
        $("#ping_master_label")[0].innerText = data;
    else
        $("#ping_master_label")[0].innerText = "master on-line";
}