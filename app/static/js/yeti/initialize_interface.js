function initialize_interface(id){
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
            data: JSON.stringify({ id: id }),
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

// receive running state from backend: interface_streamer()
// once task finished, get result to fill & refresh jstree
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
                    $('#interface-temp').text('/');
                    $('#interface-note').text('Failed in loading interface')
                }
                else {
                    $('#interface-tree').jstree({
                        'core': { 'themes': { 'name': 'proton', 'responsive': true }, "check_callback" : true}
                    });
                    $('#interface-note').text('Waiting for selection');
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

// receive running state from backend: interface_streamer()
// once task finished, get result for appending child to parent & fresh jstree
function update_streamer(status_url, nanobar, status_div, id){
    $.getJSON(status_url, function(data){
        var percent = data['current'] * 100 / data['total'];
        nanobar.go(parseInt(percent));
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            // task finished, state is not 'PROGRESS', and a return from backend is received
            if ('result' in data) {
                nanobar.go(100);
                // error message
                if (data.result.error) {
                    alert(data.result.error);
                    $('#interface-tree').jstree("create_node", id, { id: 'error', text: 'Error' }, "last");

                    $('#interface-note').text('Failed in loading node information').css('display', '');
                    $('#interface-type').css('display', 'none');
                    $('#interface-title').css('display', 'none');
                    $('#interface-entity').css('display', 'none');
                    $('#interface-individual').css('display', 'none');
                    $('#interface-trust').css('display', 'none');
                    $('#interface-superfund').css('display', 'none');
                    $('#interface-company').css('display', 'none');
                    $('#interface-partnership').css('display', 'none');
                }
                // leaf node
                else if (data.result.leaf) {
                    $('#interface-individual label input').removeAttr('checked');
                    $('#interface-trust label input').removeAttr('checked');
                    $('#interface-superfund label input').removeAttr('checked');
                    $('#interface-company label input').removeAttr('checked');
                    $('#interface-partnership label input').removeAttr('checked');

                    info = data.result.leaf;
                    for (group_subgroup in info) {
                        var group_subgroup_array = group_subgroup.split('--');
                        if (group_subgroup_array.length === 2) {
                            // XPLAN item
                            $('#interface-type').text('Variable');
                            $('#interface-title').text(group_subgroup_array[0] + ' - ' +  group_subgroup_array[1])
                        }
                        else if (group_subgroup_array.length === 1) {
                            // Group - Subgroup
                            $('#interface-type').text('XPLAN Item (not variable)');
                            $('#interface-title').text(group_subgroup_array[0])
                        }

                        entities = info[group_subgroup];
                        if (entities.indexOf("individual") > -1) {
                            $('#interface-individual label input').attr('checked', 'checked');
                        }
                        if (entities.indexOf("trust") > -1) {
                            $('#interface-trust label input').attr('checked', 'checked');
                        }
                        if (entities.indexOf("superfund") > -1) {
                            $('#interface-superfund label input').attr('checked', 'checked');
                        }
                        if (entities.indexOf("company") > -1) {
                            $('#interface-company label input').attr('checked', 'checked');
                        }
                        if (entities.indexOf("partnership") > -1) {
                            $('#interface-partnership label input').attr('checked', 'checked');
                        }
                    }
                    $('#interface-note').css('display', 'none');
                    $('#interface-type').css('display', '');
                    $('#interface-title').css('display', '');
                    $('#interface-entity').css('display', '');
                    $('#interface-individual').css('display', '');
                    $('#interface-trust').css('display', '');
                    $('#interface-superfund').css('display', '');
                    $('#interface-company').css('display', '');
                    $('#interface-partnership').css('display', '');
                }
                // update node
                else {
                    var menu_list = data.result.data;
                    for (item in menu_list) {
                        var node = { id: menu_list[item].id, text: menu_list[item].text };
                        $('#interface-tree').jstree("create_node", id, node, "last");
                    }
                    $('#interface-note').text('Waiting for selection').css('display', '');
                    $('#interface-type').css('display', 'none');
                    $('#interface-title').css('display', 'none');
                    $('#interface-entity').css('display', 'none');
                    $('#interface-individual').css('display', 'none');
                    $('#interface-trust').css('display', 'none');
                    $('#interface-superfund').css('display', 'none');
                    $('#interface-company').css('display', 'none');
                    $('#interface-partnership').css('display', 'none');
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
            }, 1000);
        }
    });
}
