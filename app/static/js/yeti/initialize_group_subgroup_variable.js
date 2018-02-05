var local_var_cache = {};
$.ajax({
    type: 'GET',
    url: '/code/acquire_group',
    dataType: 'json',
    success: function(data, status, request) {
        var groups = data.group;
        var group_selector = $('#group-selector');
        var flag = 1;
        for (obj in groups) {
            // loop in each object pair ({key: value}) from JSON
            for (key in groups[obj]) {
                // loop in key - value pair of each object
                var group_var = key;
                var group_name = groups[obj][key];
                if (flag) {
                    group_selector.append('<option value="' + group_var + '" selected="selected">' + group_name + '</option>');
                    flag = 0;
                }
                else {
                    group_selector.append('<option value="' + group_var + '">' + group_name + '</option>');
                }
            }
        }
        group_selector.selectpicker('refresh');
    },
    error: function() {
        alert('Notice from Group Selector: Information out of date, please login again');
    }
});


function variable_initialization(subgroup_id, local_var_cache) {
    $.ajax({
        type: 'GET',
        url: '/code/acquire_variable/' + subgroup_id,
        dataType: 'json',
        success: function(data, status, request) {
            var variables = data.variable;
            var variable_selector = $('#variable-selector');
            variable_selector.empty();
            var flag = 1;
            if (typeof variables[0] === 'undefined') {
                $('#variable-selector-table').css('display', '');
                $('#var-variable').text('/');
                $('#var-usage').text('/');
                $('#var-type').text('/');
            }
            for (obj in variables) {
                for (key in variables[obj]) {
                    var variable_var = key;
                    var variable_detail = variables[obj][key];
                    local_var_cache[variable_var] = [variable_detail[1], variable_detail[2], variable_detail[3]];
                    // variable_detail == ["Variable Name", "$entity.usage", "Type", "Multi (null or list)"]
                    if (flag) {
                        variable_selector.append('<option value="' + variable_var + '" selected="selected">' + variable_detail[0] + '</option>');
                        $('#variable-search-table').css('display', 'none');
                        $('#variable-search-table-head').css('display', 'none');
                        $('#variable-selector-table').css('display', '');
                        $('#var-variable').text(variable_var);
                        $('#var-usage').text(variable_detail[1]);
                        $('#var-type').text(variable_detail[2]);
                        var multi_choice_table = $('#multi-choice-table');
                        multi_choice_table.empty();
                        if (variable_detail[3] && (Object.keys(variable_detail[3]).length)) {
                            $('#choice-value-title').text('.value');
                            $('#choice-text-title').text('.text');
                            for (index in variable_detail[3]) {
                                multi_choice_table.append('<tr><td class="col-md-5" style="font-family:Consolas">' + String(variable_detail[3][index][0]) + '</td><td class="col-md-7">' + variable_detail[3][index][1] + '</td></tr>');
                            }
                        }
                        else {
                            multi_choice_table.append('<tr><td class="col-md-5" style="font-family:Consolas">/</td><td class="col-md-7">/</td></tr>');
                        }
                        flag = 0;
                    }
                    else {
                        variable_selector.append('<option value="' + variable_var + '">' + variable_detail[0] + '</option>');
                    }
                }
            }
            variable_selector.selectpicker('refresh');
        },
        error: function() {
            alert('Notice from Variable Selector: Information out of date, please login again');
        }
    });
}

function subgroup_initialization(group_var) {
    $.ajax({
        type: 'GET',
        url: '/code/acquire_subgroup/' + group_var,
        dataType: 'json',
        success: function(data, status, request) {
            var subgroups = data.subgroup;
            var subgroup_selector = $('#subgroup-selector');
            var variable_selector = $('#variable-selector');
            subgroup_selector.empty();
            variable_selector.empty();
            var flag = 1;
            for (obj in subgroups) {
                for (key in subgroups[obj]) {
                    var subgroup_id = key;
                    var subgroup_name = subgroups[obj][key];
                    if (flag) {
                        subgroup_selector.append('<option value="' + subgroup_id + '" selected="selected">' + subgroup_name + '</option>');
                        variable_initialization(subgroup_id, local_var_cache);
                        flag = 0
                    }
                    else {
                        subgroup_selector.append('<option value="' + subgroup_id + '">' + subgroup_name + '</option>');
                    }
                }
            }
            subgroup_selector.selectpicker('refresh');
            variable_selector.selectpicker('refresh');
        },
        error: function() {
            alert('Notice from Subgroup Selector: Information out of date, please login again');
        }
    });
}
