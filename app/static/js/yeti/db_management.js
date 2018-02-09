var local_cache = {};
var running_status_displayed = false;
var finishing_status_displayed = false;

function send_db_management_message(company, message, login_info) {
    var sent_info = {
        company: company,
        message: message,
        login_info: login_info
    };

    $.ajax({
        contentType: "application/json",
        data: JSON.stringify(sent_info),
        type: 'POST',
        url: '/db_management',
        dataType: 'json',
        success: function (data, status, request) {
            var this_btn = local_cache['this'];
            var btn_class = $(this_btn).attr('class').split(' ');
            btn_class = btn_class[btn_class.length - 1];
            dis_enable_row(this_btn, btn_class, false);
            local_cache = {};

            if (message === 'delete') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Deleted Successfully',
                    'This database is no more.',
                    'Good',
                    'btn-success'
                );
                // rebuild DB table after any modification operations
                build_db_table();
            }
            else if (message === 'update') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Updated Successfully',
                    'If you have logged in with <b>' + company.toUpperCase() + '</b> then you can just return to main page to start using this updated database, otherwise you need to logout and login again for using this updated database.',
                    'Good',
                    'btn-success'
                );
                // rebuild DB table after any modification operations
                build_db_table();
            }
            else if (message === 'create') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Created Successfully',
                    'If you have logged in with <b>' + company.toUpperCase() + '</b> then you can just return to main page to start using this new database, otherwise you need to logout and login again for using this new database.',
                    'Good',
                    'btn-success'
                );
                // rebuild DB table after any modification operations
                build_db_table();
            }
        },
        error: function() {
            var this_btn = local_cache['this'];
            var btn_class = $(this_btn).attr('class').split(' ');
            btn_class = btn_class[btn_class.length - 1];
            dis_enable_row(this_btn, btn_class, false);
            local_cache = {};

            if (message === 'delete') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Deletion Failed',
                    'The deletion operation is failed.',
                    'OK',
                    'btn-danger'
                );
            }
            else if (message === 'update') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Update Failed',
                    'The update operation is failed, possibly because the account is unusable.',
                    'OK',
                    'btn-danger'
                );
            }
            else if (message === 'create') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Creation Failed',
                    'The creation operation is failed, possibly because the account is unusable.',
                    'OK',
                    'btn-danger'
                );
            }
        }
    });
}


function build_db_table() {
    $.ajax({
        type: 'GET',
        url: '/acquire_db_collection_summary',
        dataType: 'json',
        success: function (data, status, request) {
            // empty existing table, only keep row[0] (header), row[1] and row[2] (hidden template rows)
            for (i = $('#db-table tr').length - 1; i >= 3; i --) {
                $('#db-table tr:nth-child(' + i + ')').remove();
            }

            // if DB is empty, append an empty line
            if (!data.length) {
                add_row('db-table', '/', ['/', '/'], {
                    '/': ['/', '/'],
                    '//': ['/', '/']
                })
            }

            // else, append rows to table
            else {
                for (i = 0; i < data.length; i++) {
                    for (db in data[i]) {
                        var collection_data = data[i][db];
                        var collections = [];
                        var timestamps = {};
                        for (collection in collection_data) {
                            var c;
                            if (collection.includes('Group')) {
                                c = 'Field Definition'
                            }
                            else if (collection.includes('Interface')) {
                                c = 'Interface'
                            }
                            var create_time = collection_data[collection][0];
                            var update_time = collection_data[collection][1];
                            collections.push(c);
                            timestamps[c] = [create_time, update_time]
                        }
                        add_row("db-table", db, collections, timestamps)
                    }
                }
            }
        }
    });
}


function add_row(table, db, collections, timestamps) {
    // build DB table
    if (db && collections && timestamps) {
        var column_count = 0;
    }

    // generate new id for new row
    var new_id = 0;
    $.each($("#" + table + " tr"), function () {
        if (parseInt($(this).data("id")) > new_id) {
            new_id = parseInt($(this).data("id"));
        }
    });
    new_id++;

    // generate selector for "tr"
    var tr;
    var tr2;
    if (table === "db-table") {
        tr = $("<tr></tr>", {
            id: "db" + new_id,
            "data-id": new_id
        });
        if (db && collections && timestamps) {
            tr2 = $("<tr></tr>", {
                id: "db" + new_id,
                "data-id": new_id
            });
        }
    }
    else if (table === 'new-table') {
        tr = $("<tr></tr>", {
            id: "new" + new_id,
            "data-id": new_id
        });
    }

    var collection2 = '';
    // loop through each td and create new elements with new_id
    $.each($("#" + table + " tbody tr:nth(0) td"), function () {
        var current_td = $(this);
        var children = current_td.children();
        var td;

        // add new td (column)s and elementsif it has a name
        if (current_td.data("name") !== undefined) {
            var data_name = $(current_td).data("name");
            if (db && collections && timestamps) {
                column_count += 1;
                if (column_count === 1) {  // existing database
                    td = $("<td></td>", {
                        "data-name": data_name
                    });
                    td.text(db);
                    td.attr('rowspan', 2);
                    td.attr('style', 'font-size:16px;font-weight:bold')
                }
                else if (column_count === 2) {  // collection name
                    var collection1 = collections[0];
                    collection2 = collections[1];
                    td = $("<td></td>", {
                        "data-name": data_name
                    });
                    td.text(collection1);
                    td.attr('style', 'font-size:15px;font-weight:bold')
                }
                else if (column_count === 3) {  // timestamp
                    var timestamp1 = "<b>Created On:</b> " + timestamps[collections[0]][0] + "<br/><b>Updated Since:</b> " + timestamps[collections[0]][1] + "";
                    td = $("<td></td>", {
                        "data-name": data_name
                    });
                    td.html(timestamp1);
                    td.attr('rowspan', 2);
                    td.attr('style', 'font-size:15px')
                }
                else {  // column 4 and 5, two buttons
                    td = $("<td></td>", {
                        "data-name": data_name
                    });
                    td.attr('rowspan', 2);
                }
            }
            else {
                td = $("<td></td>", {
                    "data-name": data_name
                });
                td.attr('align', 'center');
            }

            // update "name" attribute for current td (column)
            var name = $(current_td).find($(children[0]).prop('tagName')).clone().val("");
            name.attr("name", $(current_td).data("name") + new_id);
            name.appendTo($(td));

            // append current td to tr
            td.appendTo(tr);
        }

        // add new td and element directly if it has no name
        else {
            td = $("<td></td>", {
                'text': $("#" + table + " tr").length
            }).appendTo(tr);
        }
    });
    // end of "each column" loop

    if (db && collections && timestamps) {
        var td1 = $("<td></td>", {});
        td1.text(collection2);
        td1.attr('style', 'font-size:15px;font-weight:bold');
        td1.appendTo(tr2);
    }

    // add the tr to table
    if (new_id % 2 && db && collections && timestamps) {
        tr.attr('style', 'background:#fafafa');
        if (db && collections && timestamps) {
            tr2.attr('style', 'background:#fafafa');
        }
    }
    else if (!(new_id % 2) && db && collections && timestamps) {
        tr.attr('style', 'background:#eaf3f3');
        if (db && collections && timestamps) {
            tr2.attr('style', 'background:#eaf3f3');
        }
    }
    else {
        tr.attr('style', 'background:#fafafa');
        if (db && collections && timestamps) {
            tr2.attr('style', 'background:#fafafa');
        }
    }

    tr.appendTo($("#" + table));
    if (db && collections && timestamps) {
        tr2.appendTo($("#" + table));
    }

    // click yellow minus to cancel operation
    tr.find("td button.row-remove").on("click", function () {
        $(this).closest("tr").remove();
        $('#new-table-head').hide();
        $("#add-company").fadeIn();
    });

    // click green plus to add new DB
    tr.find("td button.row-new").on("click", function () {
        var company = $(this).closest("tr").children("td:nth-child(1)").find('input').val();
        var username = $(this).closest("tr").children("td:nth-child(2)").find('input').val();
        var password = $(this).closest("tr").children("td:nth-child(3)").find('input').val();
        var companies = company_list();
        if (!company || !username || !password) {
            show_notification(
                'Please Fill the Form',
                'Please fill the form in order to proceed.',
                'OK',
                'btn-success'
            );
            return false
        }
        else if (companies.indexOf(company.toUpperCase()) > -1) {
            show_notification(
                '< ' + company.toUpperCase() + ' > Already Exists',
                'The target company <b>' + company.toUpperCase() + '</b> already exists in database.',
                'OK',
                'btn-success'
            );
            return false
        }
        else {
            dis_enable_row(this, 'row-new', true);
            local_cache['this'] = this;
            local_cache['n_company'] = company;
            local_cache['n_username'] = username;
            local_cache['n_password'] = password;
            show_confirmation(
                'Create Database <' + company + '>',
                '<p>By confirming, the creation progress of database <b>' + company + '</b> will be initiated and the whole operation will take around 30 minutes to finish.</p><i>(Please make sure that the XPLAN account is correct and not under use, and will not be kicked out by others)</i>',
                'Create',
                'btn-success'
            );
        }
    });

    // click red trash bin to delete a DB
    tr.find("td button.row-delete").on("click", function () {
        var company = $(this).closest("tr").children("td:first").text();
        if (company !== '/') {
            local_cache['d_company'] = company;
            local_cache['this'] = this;
            show_confirmation(
                'Delete Database <' + company + '>',
                '<p>Are you sure?</p><p>The database <b>' + company + '</b> will be deleted. You can create new database via button "<b>Add New Company</b>".</p>',
                'Delete',
                'btn-danger'
            );
        }
    });

    // click blue arrow to update a DB
    tr.find("td button.row-update").on("click", function () {
        var company = $(this).closest("tr").children("td:first").text();
        if (company !== '/') {
            dis_enable_row(this, 'row-update', true);
            local_cache['u_company'] = company;
            local_cache['this'] = this;
            show_confirmation(
                'Update Database <' + company + '>',
                '<p>By filling the form below to initiate the update progress of database <b>' + company + '</b>. The whole operation will take around 30 minutes to finish.</p><i>(Please make sure that the XPLAN account is correct and not under use, and will not be kicked out by others)</i>' +
                '<div class="form-group is-empty"><input name="company-username" placeholder="XPLAN Username for ' + company + '" class="form-control" style="width:65%"/></div>' +
                '<div class="form-group is-empty"><input name="company-password" placeholder="XPLAN Password for ' + company + '" class="form-control" style="width:65%" type="password"/></div>',
                'Update',
                'btn-info'
            );
        }
    });
}


function dis_enable_row(btn, btn_type, disable) {
    var row = $(btn).closest("tr");
    if (btn_type === 'row-update') {
        row.children("td:nth-child(4)").find('button').prop('disabled', disable);
        row.children("td:nth-child(5)").find('button').prop('disabled', disable);
        }
    else if (btn_type === 'row-new') {
        row.children("td:nth-child(1)").find('input').prop('disabled', disable);
        row.children("td:nth-child(2)").find('input').prop('disabled', disable);
        row.children("td:nth-child(3)").find('input').prop('disabled', disable);
        row.children("td:nth-child(4)").find('button').prop('disabled', disable);
        row.children("td:nth-child(5)").find('button').prop('disabled', disable);
    }
}


function company_list() {
    var t_body = $('#db-table-body');
    var list = [];
    for (i = 2; i < t_body.find('tr').length; i += 2) {
        list.push($(t_body.find('tr')[i]).find('td:nth-child(1)').text());
    }
    return list;
}
