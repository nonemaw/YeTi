var local_search_cache = {}; // will be used globally

function search(pattern, count) {
    pattern = pattern.replace('/', ' ').trim();
    var regex = /\[([0-9]+)\]$/;
    if (regex.test(pattern)) {
        count = regex.exec(pattern)[1];
        pattern = /(.*)\[[0-9]+\]$/.exec(pattern)[1].trim();
    }

    var variable_table_search = $('#variable-search-table');
    variable_table_search.css('display', '');
    $('#variable-search-table-head').css('display', '');
    $('#variable-selector-table').css('display', 'none');
    variable_table_search.empty();
    variable_table_search.append('<tr><td class="col-md-3" style="font-family:Arial;font-size:15px;padding:5px;">/</td><td class="col-md-4" style="font-family:Arial;font-size:15px;padding:5px;">/</td><td class="col-md-5" style="font-family:Arial;font-weight: bold;color:#009688;padding:5px;">Searching ...</td></tr>');

    sent_info = {
        pattern: pattern,
        count: count
    };

    $.ajax({
        contentType: "application/json",
        data: JSON.stringify(sent_info),
        type: 'POST',
        url: '/code/acquire_search',
        dataType: 'json',
        success: function (data, status, request) {
            var search_result = data.search_result;
            if (search_result.length === 0) {
                variable_table_search.empty();
                variable_table_search.append('<tr><td class="col-md-3" style="font-family:Arial;font-size:15px;">/</td><td class="col-md-4" style="font-family:Arial;font-size:15px;padding:5px;">/</td><td class="col-md-5" style="font-family:Arial;font-weight: bold;color:#009688;padding:5px;">(No Search Result)</td></tr>');
            }
            else {
                variable_table_search.empty();
                local_search_cache = {};
                var id = 0;
                for (obj in search_result) {
                    ++id;
                    var group_var = search_result[obj][0];
                    var group_name = search_result[obj][1];
                    var subgroup_id = search_result[obj][2];
                    var subgroup = search_result[obj][3];
                    var var_var = search_result[obj][4];
                    var var_name = search_result[obj][5];
                    variable_table_search.append('<tr class="x" id="search-result' + String(id) + '"><td class="col-md-3" style="font-family:Arial;font-size:15px;padding:5px;">' + group_name + '</td><td class="col-md-4" style="font-family:Arial;font-size:15px;padding:5px;">' + subgroup + '</td><td class="col-md-5" style="font-family:Arial;font-weight: bold;color:#009688;padding:5px;">' + var_name + '</td></tr>');
                    local_search_cache[id] = [group_var, subgroup_id, var_var]
                }
            }

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

// click on search result
$('#variable-search-table').on('click','.x',function(event){
    // get table's row id, replace all leading non-digits with nothing
    var result_row_id = $(event.currentTarget).attr('id').replace( /^\D+/g, '');
    var subgroup_id = local_search_cache[result_row_id][1];
    var var_var = local_search_cache[result_row_id][2];

    sent_info = {
        subgroup_id : subgroup_id,
        var_var : var_var
    };

    $.ajax({
        contentType: "application/json",
        data: JSON.stringify(sent_info),
        type: 'POST',
        url: '/code/acquire_search_result',
        dataType: 'json',
        success: function(data, status, request) {
            var variable = data.variable;
            $('#variable-search-table').css('display', 'none');
            $('#variable-search-table-head').css('display', 'none');
            $('#variable-selector-table').css('display', '');
            $('#var-variable').text(var_var);
            $('#var-usage').text(variable[0]);
            $('#var-type').text(variable[1]);
            var multi_choice_table = $('#multi-choice-table');
            multi_choice_table.empty();
            if (variable[2] && (Object.keys(variable[2]).length)) {
                $('#choice-value-title').text('Value');
                $('#choice-text-title').text('Text');
                for (index in variable[2]) {
                    multi_choice_table.append('<tr><td class="col-md-5" style="font-family:Consolas">' + String(variable[2][index][0]) + '</td><td class="col-md-7">' + variable[2][index][1] + '</td></tr>');
                }
            }
            else {
                multi_choice_table.append('<tr><td class="col-md-5" style="font-family:Consolas">/</td><td class="col-md-7">/</td></tr>');
            }
        },
        error: function() {
            show_notification(
                'Error',
                'Unexpected error occurred during acquiring detailed search result.',
                'OK',
                'btn-danger'
            );
        }
    });
});

// update table when a variable of search result is selected
$('#variable-selector').on('change', function(){
    $('#variable-search-table').css('display', 'none');
    $('#variable-search-table-head').css('display', 'none');
    $('#variable-selector-table').css('display', '');
    var var_detail = local_var_cache[$('#variable-selector option:selected').val()];
    $('#var-variable').text($('#variable-selector option:selected').val());
    $('#var-usage').text(var_detail[0]);
    $('#var-type').text(var_detail[1]);
    var multi_choice_table = $('#multi-choice-table');
    multi_choice_table.empty();
    if (var_detail[2] && (Object.keys(var_detail[2]).length)) {
        $('#choice-value-title').text('Value');
        $('#choice-text-title').text('Text');
        for (index in var_detail[2]) {
            multi_choice_table.append('<tr><td class="col-md-5" style="font-family:Consolas">' + String(var_detail[2][index][0]) + '</td><td class="col-md-7">' + var_detail[2][index][1] + '</td></tr>');
        }
    }
    else {
        multi_choice_table.append('<tr><td class="col-md-5" style="font-family:Consolas">/</td><td class="col-md-7">/</td></tr>');
    }
});