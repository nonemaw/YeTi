var local_scenario_cache = {};
$.ajax({
    type: 'GET',
    url: '/acquire_snippet_group',
    dataType: 'json',
    success: function(data, status, request) {
        var groups = data.group;
        var snippet_group_selector = $('#snippet-group-selector');
        var flag = 1;
        for (obj in groups) {
            // loop in each object pair ({id: group}) from JSON
            for (key in groups[obj]) {
                // loop in key - value pair of each object
                var group_id = key;
                var group_name = groups[obj][key];
                if (flag) {
                    snippet_group_selector.append('<option value="/" selected="selected">/</option>');
                    snippet_group_selector.append('<option value="' + group_id + '">' + group_name + '</option>');
                    flag = 0;
                }
                else {
                    snippet_group_selector.append('<option value="' + group_id + '">' + group_name + '</option>');
                }
            }
        }
        snippet_group_selector.selectpicker('refresh');
    },
    error: function() {
        alert('Unexpected error in Snippet Group selector');
    }
});


function snippet_scenario_initialization(group_id) {
    local_scenario_cache = {};
    $.ajax({
        type: 'GET',
        url: '/acquire_snippet_scenario/' + group_id,
        dataType: 'json',
        success: function(data, status, request) {
            var scenarios = data.scenario;
            var snippet_scenario_selector = $('#snippet-scenario-selector');
            snippet_scenario_selector.empty();
            var flag = 1;
            for (obj in scenarios) {
                for (key in scenarios[obj]) {
                    console.log(key)
                    var scenario_id = key;
                    var scenario_detail = scenarios[obj][key];
                    local_scenario_cache[scenario_id] = scenario_detail[1];
                    if (flag) {
                        snippet_scenario_selector.append('<option value="' + scenario_id + '">' + scenario_detail[0] + '</option>');
                        snippet_section.setValue(scenario_detail[1]);
                        flag = 0
                    }
                    else {
                        snippet_scenario_selector.append('<option value="' + scenario_id + '">' + scenario_detail[0] + '</option>');
                    }
                }
            }
            snippet_scenario_selector.selectpicker('refresh');
        },
        error: function() {
            alert('Unexpected error in Snippet Scenario selector');
        }
    });
}
