function initialize_interface(id, text){
    var div = $('<div></div>');
    $('#progress').append(div);
    var nanobar = new Nanobar({
        // bg: '#CB661A',
        bg: '#e77300',
        target: div[0].childNodes[0]
    });

    if (id === undefined) {
        $.ajax({
            type: 'GET',
            url: '/initialize_interface',
            success: function (data, status, request) {
                nanobar.go(1);
                status_url = request.getResponseHeader('streamer_URL');
                initialization_streamer(status_url, nanobar, div[0]);
            },
            error: function () {
                alert('Unexpected error during initialize_interface()');
            }
        });
    }

    else {
        $.ajax({
            contentType: "application/json",
            data: JSON.stringify({ id: id, text: text }),
            type: 'POST',
            url: '/update_interface',
            success: function (data, status, request) {
                nanobar.go(1);
                status_url = request.getResponseHeader('streamer_URL');
                update_streamer(status_url, nanobar, div[0], id);
            },
            error: function () {
                alert('Unexpected error during update_interface()');
            }
        });
    }
}

function initialization_streamer(status_url, nanobar, status_div) {
    $.getJSON(status_url, function(data){
        var percent = data['current'] * 100 / data['total'];
        nanobar.go(parseInt(percent));
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            // task finished, state is not 'PROGRESS', and a return from backend is received
            if ('result' in data) {
                nanobar.go(100);
                // show result, remove bar, update menu
                if (data.result.error) {
                    alert(data.result.error);
                    $('#interface-tree').jstree({
                        'core': {'themes': { 'name': 'proton', 'responsive': true }, "check_callback" : true, 'data': [{ 'id': 'Error', 'parent': '#', 'text': 'Error' }]}
                    });
                    $('#interface-tree').jstree(true).refresh();
                }
                else {
                    $('#interface-tree').jstree({
                        'core': { 'themes': { 'name': 'proton', 'responsive': true }, "check_callback" : true}
                    });
                    $('#interface-tree').jstree(true).settings.core.data = data.result.data;
                    $('#interface-tree').jstree(true).refresh();
                }
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[0]).text('Result not received, something went wrong.');
            }
        }
        else {
            setTimeout(function() {
                initialization_streamer(status_url, nanobar, status_div);
            }, 666);
        }
    });
}

function update_streamer(status_url, nanobar, status_div, id){
    $.getJSON(status_url, function(data){
        var percent = data['current'] * 100 / data['total'];
        nanobar.go(parseInt(percent));
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            // task finished, state is not 'PROGRESS', and a return from backend is received
            if ('result' in data) {
                nanobar.go(100);
                // show result, remove bar, update menu
                if (data.result.error) {
                    alert(data.result.error);
                    $('#interface-tree').jstree("create_node", id, { id: 'error', text: 'Error' }, "last");
                }
                else {
                    var menu_list = data.result.data;
                    for (item in menu_list) {
                        var node = { id: menu_list[item].id, text: menu_list[item].text };

                        console.warn(node);

                        $('#interface-tree').jstree("create_node", id, node, "last");
                    }
                    //$('#interface-tree').jstree(true).refresh();
                }
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[0]).text('Result not received, something went wrong.');
            }
        }
        else {
            setTimeout(function() {
                update_streamer(status_url, nanobar, status_div, id);
            }, 666);
        }
    });
}
