var local_search_cache = {};
$('#search-button').click(function() {
    var variable_table_search = $('#variable-search-table');

    var pattern = $('#search-field').val();
    if (pattern) {
        $('#variable-search-table').css('display', '');
        $('#variable-search-table-head').css('display', '');
        $('#variable-selector-table').css('display', 'none');
        variable_table_search.empty();
        variable_table_search.append('<tr><td class="col-md-3" style="font-family:Arial;font-size:15px">/</td><td class="col-md-3" style="font-family:Arial;font-size:15px">/</td><td class="col-md-6" style="font-family:Arial;color:#009688">Searching ...</td></tr>');

        $.ajax({
            type: 'GET',
            url: '/code/acquire_search/' + pattern,
            dataType: 'json',
            success: function (data, status, request) {
                var search_result = data.search_result;
                if (search_result.length == 0) {
                    variable_table_search.empty();
                    variable_table_search.append('<tr><td class="col-md-3" style="font-family:Arial;font-size:15px">/</td><td class="col-md-3" style="font-family:Arial;font-size:15px">/</td><td class="col-md-6" style="font-family:Arial;color:#009688">(No Search Result)</td></tr>');
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
                        variable_table_search.append('<tr class="x" id="search-result' + String(id) + '"><td class="col-md-3" style="font-family:Arial;font-size:15px">' + group_name + '</td><td class="col-md-3" style="font-family:Arial;font-size:15px">' + subgroup + '</td><td class="col-md-6" style="font-family:Arial;color:#009688">' + var_name + '</td></tr>');
                        local_search_cache[id] = [group_var, subgroup_id, var_var]
                    }
                }

            },
            error: function () {
                alert('Unexpected error in searching context');
            }
        });
    }
    else {
        return false;
    }
});

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
            alert('Unexpected error in sending code text');
        }
    });
});