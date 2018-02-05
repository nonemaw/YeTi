var local_cache = {};

function send_db_management_message(company, message, login_info) {
    var sent_info;
    if (message === 'create' && login_info) {
        sent_info = {
            company: company,
            message: message,
            login_info: login_info
        };
    }
    else {
        sent_info = {
            company: company,
            message: message,
            login_info: null
        };
    }

    $.ajax({
        contentType: "application/json",
        data: JSON.stringify(sent_info),
        type: 'POST',
        url: '/db_management',
        dataType: 'json',
        success: function (data, status, request) {
            if (message === 'delete') {
                var this_row = local_cache['d_this'];
                $(this_row).closest("tr").next("tr").remove();
                $(this_row).closest("tr").remove();
                // if table is empty (only 1 head row and 2 hidden rows left): add an empty row
                if ($('#db-table tr').length === 3) {
                    add_row('db-table', '/', ['/', '/'], {
                        '/': ['/', '/'],
                        '//': ['/', '/']
                    })
                }
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Deleted Successfully',
                    'This database is no more.',
                    'Good',
                    'btn-success'
                );
            }
            else if (message === 'update') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Updated Successfully',
                    'You can now return to main page to start using the updated database.',
                    'Good',
                    'btn-success'
                );
                // update row's update time:





            }
            else if (message === 'create') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Created Successfully',
                    'You can now login again to use this company.',
                    'Good',
                    'btn-success'
                );
                // add row to table:






            }
            local_cache = {};
        },
        error: function() {
            if (message === 'delete') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Deletion Failed',
                    'The deletion operation is failed',
                    'OK',
                    'btn-danger'
                );
            }
            else if (message === 'update') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Update Failed',
                    'The update operation is failed',
                    'OK',
                    'btn-danger'
                );
            }
            else if (message === 'create') {
                show_notification(
                    'Database < ' + company.toUpperCase() + ' > Creation Failed',
                    'The creation operation is failed',
                    'OK',
                    'btn-danger'
                );
            }
            local_cache = {};
        }
    });
}


function build_db_table() {
    $.ajax({
        type: 'GET',
        url: '/acquire_db_collection_summary',
        dataType: 'json',
        success: function (data, status, request) {
            for (i = 0; i < data.length; i ++) {
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
                    var timestamp1 = "<b>Created On:</b> " + timestamps[collections[0]][0] + "<br><b>Updated Since:</b> " + timestamps[collections[0]][1] + "";
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
        var company = $(this).closest("tr").children("td:first").find('input').val();
        var username = $(this).closest("tr").children("td:nth-child(2)").find('input').val();
        var password = $(this).closest("tr").children("td:nth-child(3)").find('input').val();
        if (!company || !username || !password) {
            return false
        }
        else {
            local_cache['n_company'] = company;
            local_cache['n_username'] = username;
            local_cache['n_password'] = password;
            show_confirmation(
                'Create Database <' + company + '>',
                'By confirming, the progress of database creation will be initiated and the whole operation will take around 30 minutes to finish.',
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
            local_cache['d_this'] = this;
            show_confirmation(
                'Delete Database <' + company + '>',
                'Are you sure? The database <b>' + company + '</b> will be deleted. You can recreate new database via button "<b>Add New Company</b>".',
                'Delete',
                'btn-danger'
            );
        }
    });

    // click blue arrow to update a DB
    tr.find("td button.row-update").on("click", function () {
        var company = $(this).closest("tr").children("td:first").text();
        if (company !== '/') {
            local_cache['u_company'] = company;
            local_cache['u_this'] = this;
            show_confirmation(
                'Update Database <' + company + '>',
                'By confirming, the update progress will be initiated and the whole operation will take around 30 minutes to finish.',
                'Update',
                'btn-info'
            );
        }
    });
}
