
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
var local_interface_table1_cache = {};
var local_interface_table2_cache = {};
var local_interface_group_table_cache = {};
var current_subugroup = undefined;

// function initialize_interface(id){
//     var div = $('<div></div>');
//     $('#progress').append(div);
//     var nanobar = new Nanobar({
//         // bg: '#CB661A',
//         bg: '#e77300',
//         target: div[0].childNodes[0]
//     });
//
//     if (id === undefined) {
//         $.ajax({
//             type: 'GET',
//             url: '/initialize_interface',
//             success: function (data, status, request) {
//                 nanobar.go(1);
//                 status_url = request.getResponseHeader('streamer_URL');
//                 initialization_streamer(status_url, nanobar, div[0]);
//             },
//             error: function () {
//                 alert('Unexpected error during initialize_interface()');
//             }
//         });
//     }
//
//     else {
//         $.ajax({
//             contentType: "application/json",
//             data: JSON.stringify({ id: id }),
//             type: 'POST',
//             url: '/update_interface',
//             success: function (data, status, request) {
//                 nanobar.go(1);
//                 status_url = request.getResponseHeader('streamer_URL');
//                 update_streamer(status_url, nanobar, div[0], id);
//             },
//             error: function () {
//                 alert('Unexpected error during update_interface()');
//             }
//         });
//     }
// }
//
// // receive running state from backend: interface_streamer()
// // once task finished, get result to fill & refresh jstree
// function initialization_streamer(status_url, nanobar, status_div) {
//     $.getJSON(status_url, function(data){
//         var percent = data['current'] * 100 / data['total'];
//         nanobar.go(parseInt(percent));
//         if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
//             // task finished, state is not 'PROGRESS', and a return from backend is received
//             if ('result' in data) {
//                 nanobar.go(100);
//                 // show result, remove bar, update menu
//                 if (data.result.error) {
//                     alert(data.result.error);
//                     $('#interface-temp').text('/');
//                     inote.text('Failed in loading interface')
//                 }
//                 else {
//                     itree.jstree({
//                         'core': { 'themes': { 'name': 'proton', 'responsive': true }, "check_callback" : true}
//                     });
//                     inote.text('Waiting for selection');
//                     itree.jstree(true).settings.core.data = data.result.data;
//                     itree.jstree(true).refresh();
//                 }
//             }
//             else {
//                 // something unexpected happened
//                 $(status_div.childNodes[0]).text('Result not received, something went wrong.');
//             }
//         }
//         else {
//             setTimeout(function() {
//                 initialization_streamer(status_url, nanobar, status_div);
//             }, 666);
//         }
//     });
// }
//
// // receive running state from backend: interface_streamer()
// // once task finished, get result for appending child to parent & fresh jstree
// function update_streamer(status_url, nanobar, status_div, id){
//     $.getJSON(status_url, function(data){
//         var percent = data['current'] * 100 / data['total'];
//         nanobar.go(parseInt(percent));
//         if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
//             // task finished, state is not 'PROGRESS', and a return from backend is received
//             if ('result' in data) {
//                 nanobar.go(100);
//                 // error message
//                 if (data.result.error) {
//                     alert(data.result.error);
//                     $('#interface-tree').jstree("create_node", id, { id: 'error', text: 'Error' }, "last");
//
//                     inote.text('Failed in loading node information').show();
//                     itype.hide();
//                     ititle.hide();
//                     ientity.hide();
//                     iindividual.hide();
//                     itrust.hide();
//                     isuperfund.hide();
//                     icompany.hide();
//                     ipartnership.hide();
//                     $('#interface-xplan-table1-head').hide();
//                     $('#interface-xplan-table2-head').hide();
//                     $('#interface-group-table-head').hide();
//                 }
//                 // leaf node
//                 else if (data.result.leaf_basic) {
//                     iindividual.find('label, input').removeAttr('checked');
//                     itrust.find('label, input').removeAttr('checked');
//                     isuperfund.find('label, input').removeAttr('checked');
//                     icompany.find('label, input').removeAttr('checked');
//                     ipartnership.find('label, input').removeAttr('checked');
//
//                     var basic_info = data.result.leaf_basic;
//                     for (item in basic_info) {
//                         var group_subgroup_array = item.split('--');
//
//                         // Group - Subgroup
//                         if (group_subgroup_array.length === 2) {
//                             $('#interface-table-row').css('height', '0');
//                             $('#interface-xplan-table1-head').hide();
//                             $('#interface-xplan-table2-head').hide();
//                             $('#interface-group-table-head').hide();
//                             itype.text('Variable');
//                             ititle.text('[' + group_subgroup_array[0] + '] ' +  group_subgroup_array[1]);
//                             ititle.show();
//                         }
//
//                         // XPLAN collection
//                         else if (group_subgroup_array.length === 1) {
//                             // XPLAN collection got some variables
//                             if (data.result.leaf_xplan) {
//                                 $('#interface-type').text('XPLAN Item Collection: ' + group_subgroup_array[0]);
//                                 $('#interface-title').hide();
//                                 $('#interface-group-table-head').hide();
//                                 var interface_xplan_table1 = $('#interface-xplan-table1');
//                                 var interface_xplan_table2 = $('#interface-xplan-table2');
//                                 interface_xplan_table1.empty();
//                                 interface_xplan_table2.empty();
//
//                                 var xplan_info = data.result.leaf_xplan;
//                                 local_interface_table1_cache = {};
//                                 local_interface_table2_cache = {};
//                                 for (table in xplan_info) {
//                                     if (table === 'table1') {
//                                         var _id1 = 0;
//                                         $('#interface-xplan-table1-title').text('List View');
//                                         $('#interface-table-row').css('height', '200px');
//                                         for (variable in xplan_info[table]) {
//                                             ++_id1;
//                                             interface_xplan_table1.append('<tr class="t1" id="tableone_' + String(_id1) + '"><td>' + xplan_info[table][variable] + '</td></tr>');
//                                             local_interface_table1_cache[_id1] = xplan_info[table][variable];
//                                         }
//                                         $('#interface-xplan-table1-head').show();
//                                     }
//                                     else if (table === 'table2') {
//                                         var _id2 = 0;
//                                         $('#interface-xplan-table2-title').text('Edit View');
//                                         for (variable in xplan_info[table]) {
//                                             ++_id2;
//                                             interface_xplan_table2.append('<tr class="t2" id="tabletwo_' + String(_id2) + '"><td>' + xplan_info[table][variable] + '</td></tr>');
//                                             local_interface_table2_cache[_id2] = xplan_info[table][variable];
//                                         }
//                                         $('#interface-xplan-table2-head').show();
//                                     }
//                                 }
//                                 // if XPLAN collection/group has a known subgroup
//                                 if (data.result.subgroup) {
//                                     current_subugroup = data.result.subgroup;
//                                 }
//                                 else {
//                                     current_subugroup = undefined;
//                                 }
//                             }
//                             // a Group got some variables
//                             else if (data.result.leaf_group) {
//                                 $('#interface-xplan-table1-head').hide();
//                                 $('#interface-xplan-table2-head').hide();
//                                 $('#interface-type').text('Group Collection: ' + group_subgroup_array[0]);
//                                 $('#interface-title').hide();
//                                 $('#interface-group-table-title').css('display', '').text('Group View');
//                                 $('#interface-table-row').css('height', '200px');
//                                 var interface_group_table = $('#interface-group-table');
//                                 var group_info = data.result.leaf_group;
//                                 interface_group_table.empty();
//
//                                 local_interface_group_table_cache = {};
//                                 var _id3 = 0;
//                                 for (group in group_info) {
//                                     for (variable in group_info[group]) {
//                                         ++ _id3;
//                                         interface_group_table.append('<tr class="g" id="tablethree_' + String(_id3) + '"><td>' + group_info[group][variable] + '</td></tr>');
//                                         local_interface_group_table_cache[_id3] = group_info[group][variable];
//                                     }
//                                 }
//                                 $('#interface-group-table-head').show();
//                             }
//                             // an empty XPLAN colelction
//                             else {
//                                 $('#interface-type').text('XPLAN Item Collection: ' + group_subgroup_array[0]);
//                                 $('#interface-xplan-table1').empty().append('<tr><td>/</td></tr>');
//                                 $('#interface-xplan-table2-head').hide();
//                                 $('#interface-group-table-head').hide();
//                                 $('#interface-table-row').css('height', '30px');
//                                 $('#interface-xplan-table1-title').text('(Collection is Empty)');
//                                 $('#interface-xplan-table1-head').show();
//                                 $('#interface-group-table-title').hide();
//                             }
//                             ititle.hide();
//                         }
//
//                         var entities = basic_info[item];
//                         if (entities.indexOf("individual") > -1) {
//                             iindividual.find('label, input').attr('checked', 'checked');
//                         }
//                         if (entities.indexOf("trust") > -1) {
//                             itrust.find('label, input').attr('checked', 'checked');
//                         }
//                         if (entities.indexOf("superfund") > -1) {
//                             isuperfund.find('label, input').attr('checked', 'checked');
//                         }
//                         if (entities.indexOf("company") > -1) {
//                             icompany.find('label, input').attr('checked', 'checked');
//                         }
//                         if (entities.indexOf("partnership") > -1) {
//                             ipartnership.find('label, input').attr('checked', 'checked');
//                         }
//                     }
//                     inote.hide();
//                     itype.show();
//                     ientity.show();
//                     iindividual.show();
//                     itrust.show();
//                     isuperfund.show();
//                     icompany.show();
//                     ipartnership.show();
//                 }
//                 // not a leaf, update node
//                 else {
//                     var menu_list = data.result.data;
//                     for (item in menu_list) {
//                         var node = { id: menu_list[item].id, text: menu_list[item].text };
//                         $('#interface-tree').jstree("create_node", id, node, "last");
//                     }
//                     inote.text('Waiting for selection').show();
//                     itype.hide();
//                     ititle.hide();
//                     ientity.hide();
//                     iindividual.hide();
//                     itrust.hide();
//                     isuperfund.hide();
//                     icompany.hide();
//                     ipartnership.hide();
//                     $('#interface-xplan-table1-head').hide();
//                     $('#interface-xplan-table2-head').hide();
//                     $('#interface-group-table-head').hide();
//                 }
//             }
//             else {
//                 // something unexpected happened
//                 $(status_div.childNodes[0]).text('Result not received, something went wrong.');
//             }
//         }
//         else {
//             setTimeout(function() {
//                 update_streamer(status_url, nanobar, status_div, id);
//             }, 1000);
//         }
//     });
// }

function initialize_interface(id){
    if (id === undefined) {
        $.ajax({
            type: 'GET',
            url: '/code/acquire_interface',
            dataType: 'json',
            success: function (data, status, request) {
                var root_nodes = data.root_nodes;
                itree.jstree({
                    core: {
                        themes: {'name': 'proton', 'responsive': true},
                        check_callback: true,
                        data: root_nodes
                    },
                    types: {
                        root: {icon: "/static/img/jstree_icons/root.png"},
                        // root: {icon: "glyphicon glyphicon-folder-close"},
                        other: {icon: "/static/img/jstree_icons/full.png"},
                        variable: {icon: "/static/img/jstree_icons/var.png"},
                        group: {icon: "/static/img/jstree_icons/group.png"},
                        xplan: {icon: "/static/img/jstree_icons/xplan.png"},
                        gap: {icon: "/static/img/jstree_icons/gap.png"},
                        title: {icon: "/static/img/jstree_icons/title.png"},
                        wizard: {icon: "/static/img/jstree_icons/wizard.png"},
                        default: {}
                    },
                    plugins: ["search", "themes", "types"]
                })
                // }).on(
                //         'open_node.jstree', function (e, data) {
                //             data.instance.set_icon(data.node, "glyphicon glyphicon-folder-open");
                //         }
                //     ).on(
                //         'close_node.jstree', function (e, data) {
                //             data.instance.set_icon(data.node, "glyphicon glyphicon-folder-close");
                //         }
                //     );
            },
            error: function () {
                show_notification(
                'Error',
                'Login information out of date, please login again.',
                'OK',
                'btn-danger'
                );
            }
        });
    }

    else if (!/^client_[0-9]+/.test(id)) {
        $.ajax({
            contentType: "application/json",
            data: JSON.stringify({ id: id }),
            type: 'POST',
            url: '/code/acquire_leaf',
            dataType: 'json',
            success: function (data, status, request) {
                iindividual.find('label, input').removeAttr('checked');
                itrust.find('label, input').removeAttr('checked');
                isuperfund.find('label, input').removeAttr('checked');
                icompany.find('label, input').removeAttr('checked');
                ipartnership.find('label, input').removeAttr('checked');

                var leaf_content = data.leaf;
                var leaf_name = leaf_content.text;
                var basic_info = leaf_content.page.leaf_basic;
                var group_subgroup_array = leaf_name.split('--');

                // Group - Subgroup
                if (group_subgroup_array.length === 2 || leaf_content.leaf_type === 'variable') {
                    $('#interface-table-row').css('height', '0');
                    $('#interface-xplan-table1-head').hide();
                    $('#interface-xplan-table2-head').hide();
                    $('#interface-group-table-head').hide();
                    itype.text('Variable');
                    if (group_subgroup_array.length === 2) {
                        ititle.text('[' + group_subgroup_array[0] + '] ' + group_subgroup_array[1]);
                    }
                    else if (group_subgroup_array.length === 1) {
                        ititle.text('[ / ] ' + group_subgroup_array[0]);
                    }
                    ititle.show();
                }

                // XPLAN collection
                else if (group_subgroup_array.length === 1) {
                    // XPLAN collection got some variables
                    if (leaf_content.page.leaf_xplan) {
                        itype.text('XPLAN Item Collection: ' + group_subgroup_array[0]);
                        ititle.hide();
                        $('#interface-group-table-head').hide();
                        var interface_xplan_table1 = $('#interface-xplan-table1');
                        var interface_xplan_table2 = $('#interface-xplan-table2');
                        interface_xplan_table1.empty();
                        interface_xplan_table2.empty();

                        var xplan_info = leaf_content.page.leaf_xplan;
                        local_interface_table1_cache = {};
                        local_interface_table2_cache = {};
                        for (table in xplan_info) {
                            if (table === 'table1') {
                                var _id1 = 0;
                                $('#interface-xplan-table1-title').text('List View');
                                $('#interface-table-row').css('height', '30vh');
                                for (variable in xplan_info[table]) {
                                    ++_id1;
                                    interface_xplan_table1.append('<tr class="t1" id="tableone_' + String(_id1) + '"><td>' + xplan_info[table][variable] + '</td></tr>');
                                    local_interface_table1_cache[_id1] = xplan_info[table][variable];
                                }
                                $('#interface-xplan-table1-head').show();
                            }
                            else if (table === 'table2') {
                                var _id2 = 0;
                                $('#interface-xplan-table2-title').text('Edit View');
                                for (variable in xplan_info[table]) {
                                    ++_id2;
                                    interface_xplan_table2.append('<tr class="t2" id="tabletwo_' + String(_id2) + '"><td>' + xplan_info[table][variable] + '</td></tr>');
                                    local_interface_table2_cache[_id2] = xplan_info[table][variable];
                                }
                                $('#interface-xplan-table2-head').show();
                            }
                        }
                        // if XPLAN collection/group has a known subgroup
                        if (leaf_content.page.leaf_xplan.subgroup) {
                            current_subugroup = leaf_content.page.leaf_xplan.subgroup;
                        }
                        else {
                            current_subugroup = undefined;
                        }
                    }
                    // a Group got some variables
                    else if (leaf_content.page.leaf_group) {
                        $('#interface-xplan-table1-head').hide();
                        $('#interface-xplan-table2-head').hide();
                        $('#interface-type').text('Group Collection: ' + group_subgroup_array[0]);
                        $('#interface-title').hide();
                        $('#interface-group-table-title').css('display', '').text('Group View');
                        $('#interface-table-row').css('height', '30vh');
                        var interface_group_table = $('#interface-group-table');
                        var group_info = leaf_content.page.leaf_group;
                        interface_group_table.empty();

                        local_interface_group_table_cache = {};
                        var _id3 = 0;
                        for (group in group_info) {
                            for (variable in group_info[group]) {
                                ++ _id3;
                                interface_group_table.append('<tr class="g" id="tablethree_' + String(_id3) + '"><td>' + group_info[group][variable] + '</td></tr>');
                                local_interface_group_table_cache[_id3] = group_info[group][variable];
                            }
                        }
                        $('#interface-group-table-head').show();
                    }
                    // an empty XPLAN colelction
                    else {
                        $('#interface-type').text('XPLAN Item Collection: ' + group_subgroup_array[0]);
                        $('#interface-xplan-table1').empty().append('<tr><td>/</td></tr>');
                        $('#interface-xplan-table2-head').hide();
                        $('#interface-group-table-head').hide();
                        $('#interface-table-row').css('height', '30px');
                        $('#interface-xplan-table1-title').text('(Collection is Empty)');
                        $('#interface-xplan-table1-head').show();
                        $('#interface-group-table-title').hide();
                    }
                    ititle.hide();
                }

                var entities = basic_info.entities;
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

                inote.hide();
                itype.show();
                ientity.show();
                iindividual.show();
                itrust.show();
                isuperfund.show();
                icompany.show();
                ipartnership.show();
            },
            error: function () {
                show_notification(
                'Error',
                'Unexpected error occurred during updating leaf page.',
                'OK',
                'btn-danger'
                );
            }
        });
    }
}

// click on interface table if the table is not empty - xplan table1
$('#interface-xplan-table1').on('click','.t1',function(event){
    // get table's row id, replace all leading non-digits with nothing
    var result_row_id = $(event.currentTarget).attr('id').replace( /^\D+/g, '');
    var var_var = local_interface_table1_cache[result_row_id];
    if (current_subugroup !== undefined) {
        var pattern = current_subugroup + ':' + var_var;
        search(pattern, 5);
    }
});

// click on interface table if the table is not empty - xplan table2
$('#interface-xplan-table2').on('click','.t2',function(event){
    // get table's row id, replace all leading non-digits with nothing
    var result_row_id = $(event.currentTarget).attr('id').replace( /^\D+/g, '');
    var var_var = local_interface_table2_cache[result_row_id];
    if (current_subugroup !== undefined) {
        var pattern = current_subugroup + ':' + var_var;
        search(pattern, 5);
    }
});

// click on interface table if the table is not empty - group table
$('#interface-group-table').on('click','.g',function(event){
    // get table's row id, replace all leading non-digits with nothing
    var result_row_id = $(event.currentTarget).attr('id').replace( /^\D+/g, '');
    var var_var = local_interface_group_table_cache[result_row_id];
    var current_subugroup = var_var;

    if (/\[.+\]/.test(var_var)) {
        var_var = /\[.+\] *(.+)/.exec(var_var)[1];
        current_subugroup = /\[(.+)\] *.+/.exec(current_subugroup)[1];
    }
    var pattern = current_subugroup + ':' + var_var;
    search(pattern, 5);
});

// click on a interface variable name
ititle.on('click', function(){
    var title = ititle.text();
    var variable = '_NONE';
    var current_subugroup = '/';

    if (/\[.+\]/.test(title)) {
        var re_result = /\[ *(.+) *\] *(.+)/.exec(title);
        current_subugroup = re_result[1];
        variable = re_result[2];
    }
    if (variable !== '_NONE') {
        var pattern = '';
        if (current_subugroup !== '/') {
            pattern = current_subugroup + ':' + variable;
        }
        else {
            pattern = variable;
        }
        search(pattern, 5);
    }
    return false;
});
