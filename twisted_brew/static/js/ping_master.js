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

function fetch_master_info(){
    $.ajax({
            url: "/fetch_master_info/",
        type: 'GET',
        success: master_info,
        error: master_info,
        dataType: 'json',
    });
}

function set_master_info(){
    $("#ping_master_label")[0].innerText = "updating master...";
    $.ajax({
            url: "/set_master_info/",
        type: 'POST',
        data: { "master_ip": $('#master_ip').val(), "master_port": $('#master_port').val(),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: master_set,
        error: master_set,
        dataType: 'json'
    });
}

function master_info(data){
    $.each( data, function( key, val ) {
        if(key == "master_ip"){
            $("#master_ip")[0].value = val;
        }
        if(key == "master_port"){
            $("#master_port")[0].value = val;
        }
  });
}

function master_set(data){
    $("#ping_master_label")[0].innerText = data.responseText;
}