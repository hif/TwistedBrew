function WorkerWidget(id, interval){
    this.id = id;
    this.interval = interval;
};

WorkerWidget.prototype.run = function(){
    this.get_data();
};

WorkerWidget.prototype.get_data = function(){
    $.ajax({
        url: "/session/worker_widget/" + this.id,
        type: 'GET',
        data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
        success: this.update.bind(this),
        dataType: 'html'
    });
};

WorkerWidget.prototype.update = function(data){
    if(data.length == 0){
        $('#worker_widget_' + this.id).html('Done');
        return;
    }
    $('#worker_widget_' + this.id).html(data);
    setTimeout(this.get_data.bind(this), this.interval);
};
