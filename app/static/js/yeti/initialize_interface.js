
var itree = $('#interface-tree');
var inote = $('#interface-note');
var itype = $('#interface-type');
var ititle = $('#interface-title');
var ientity = $('#interface-entity');
var iindividual = $('#interface-individual');
var itrust = $('#interface-trust');
var isuperfund = $('#interface-superfund');
var icompany = $('#interface-company');
var ipartnership = $('#interface-partnership');
var local_interface_table_cache = {};

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
                    inote.text('Failed in loading interface')
                }
                else {
                    itree.jstree({
                        'core': { 'themes': { 'name': 'proton', 'responsive': true }, "check_callback" : true}
                    });
                    inote.text('Waiting for selection');
                    itree.jstree(true).settings.core.data = data.result.data;
                    itree.jstree(true).refresh();
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

                    inote.text('Failed in loading node information').css('display', '');
                    itype.css('display', 'none');
                    ititle.css('display', 'none');
                    ientity.css('display', 'none');
                    iindividual.css('display', 'none');
                    itrust.css('display', 'none');
                    isuperfund.css('display', 'none');
                    icompany.css('display', 'none');
                    ipartnership.css('display', 'none');
                    $('#interface-collection-table-head').css('display', 'none');
                }
                // leaf node
                else if (data.result.leaf_basic) {
                    iindividual.find('label, input').removeAttr('checked');
                    itrust.find('label, input').removeAttr('checked');
                    isuperfund.find('label, input').removeAttr('checked');
                    icompany.find('label, input').removeAttr('checked');
                    ipartnership.find('label, input').removeAttr('checked');

                    var basic_info = data.result.leaf_basic;
                    for (item in basic_info) {
                        var group_subgroup_array = item.split('--');

                        if (group_subgroup_array.length === 2) {
                            // Group - Subgroup
                            $('#interface-collection-table-head').css('display', 'none');
                            itype.text('Variable');
                            ititle.text('[' + group_subgroup_array[0] + '] ' +  group_subgroup_array[1]);
                            ititle.css('display', '');
                        }

                        else if (group_subgroup_array.length === 1) {
                            // XPLAN collection
                            $('#interface-type').text('XPLAN Collection: ' + group_subgroup_array[0]);
                            $('#interface-title').css('display', 'none');
                            var interface_collection_table = $('#interface-collection-table');
                            interface_collection_table.empty();

                            if (data.result.leaf_collection) {
                                $('#interface-collection-table-title').text(group_subgroup_array[0]);
                                var collection_info = data.result.leaf_collection;
                                for (item in collection_info) {
                                    local_interface_table_cache = {};
                                    var _id = 0;
                                    for (name in collection_info[item]) {
                                        ++_id;
                                        interface_collection_table.append('<tr class="y" id="collection_' + String(_id) + '"><td class="col-md-3" style="padding:2px;padding-left:15px;font-size:14px;font-weight:bold">' + collection_info[item][name] + '</td></tr>');
                                        local_interface_table_cache[_id] = [collection_info[item][name]]
                                    }
                                }
                            }
                            else {
                                $('#interface-collection-table-title').text('(Collection is Empty)');
                                interface_collection_table.append('<tr><td class="col-md-3" style="padding:2px;padding-left:15px;font-size:14px;font-weight:bold">/</td></tr>');
                            }
                            $('#interface-collection-table-head').css('display', '');
                            ititle.css('display', 'none');
                        }

                        var entities = basic_info[item];
                        if (entities.indexOf("individual") > -1) {
                            iindividual.find('label, input').attr('checked', 'checked');
                        }
                        if (entities.indexOf("trust") > -1) {
                            itrust.find('label, input').attr('checked', 'checked');
                        }
                        if (entities.indexOf("superfund") > -1) {
                            isuperfund.find('label, input').attr('checked', 'checked');
                        }
                        if (entities.indexOf("company") > -1) {
                            icompany.find('label, input').attr('checked', 'checked');
                        }
                        if (entities.indexOf("partnership") > -1) {
                            ipartnership.find('label, input').attr('checked', 'checked');
                        }
                    }
                    inote.css('display', 'none');
                    itype.css('display', '');
                    ientity.css('display', '');
                    iindividual.css('display', '');
                    itrust.css('display', '');
                    isuperfund.css('display', '');
                    icompany.css('display', '');
                    ipartnership.css('display', '');
                }
                // update node
                else {
                    var menu_list = data.result.data;
                    for (item in menu_list) {
                        var node = { id: menu_list[item].id, text: menu_list[item].text };
                        $('#interface-tree').jstree("create_node", id, node, "last");
                    }
                    inote.text('Waiting for selection').css('display', '');
                    itype.css('display', 'none');
                    ititle.css('display', 'none');
                    ientity.css('display', 'none');
                    iindividual.css('display', 'none');
                    itrust.css('display', 'none');
                    isuperfund.css('display', 'none');
                    icompany.css('display', 'none');
                    ipartnership.css('display', 'none');
                    $('#interface-collection-table-head').css('display', 'none');
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

// click on interface table if the table is not empty
$('#interface-collection-table').on('click','.y',function(event){
    // get table's row id, replace all leading non-digits with nothing
    var result_row_id = $(event.currentTarget).attr('id').replace( /^\D+/g, '');
    var var_var = local_interface_table_cache[result_row_id][0];




});
