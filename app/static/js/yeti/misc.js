function save_misc_on_exit() {
    var sent_info = {
        config: {
            code: code_section.getValue(),
            theme: $('#theme').val(),
            font: $('#font-family').val(),
            font_size: parseInt($('#font-size').val()),
            show_i: $('#show-invisibles').prop('checked'),
            wrap_t: $('#wrap-text').prop('checked')
        },
        statistic: {
            search_count: search_count,
            search_history: search_history,
            judge_count: judge_count,
            failed_count: failed_count,
            success_count: success_count
        }
    };

    // sync ajax, keep wait until upload is done, prevent user's multi-post
    $.ajax({
        async: false,
        contentType: "application/json",
        data: JSON.stringify(sent_info),
        type: 'POST',
        url: '/save_misc',
        dataType: 'json',
        success: function (data, status, request) {},
        error: function() {
            show_notification(
                'Error',
                'Unexpected error in saving configuration and statistic information.',
                'OK',
                'btn-danger'
            );
        }
    });
}


// load config from backend
function load_config() {
    $.ajax({
        type: 'GET',
        url: '/load_config',
        dataType: 'json',
        success: function (data, status, request) {
            // set code
            if (data) {
                if (data.code !== undefined) {
                    code_section.setValue(data.code);
                }
                if (data.theme !== undefined) {
                    code_section.setTheme("ace/theme/" + data.theme);
                    snippet_section.setTheme("ace/theme/" + data.theme);
                    $('#theme').selectpicker('val', data.theme);
                }
                if (data.font !== undefined) {
                    code_section.setOption("fontFamily", data.font);
                    snippet_section.setOption("fontFamily", data.font);
                    $('#font-family').selectpicker('val', data.font);
                }
                if (data.font_size !== undefined) {
                    code_section.setOption("fontSize", data.font_size);
                    $('#font-size').selectpicker('val', data.font_size);
                }
                if (data.show_i !== undefined) {
                    code_section.setOption("showInvisibles", data.show_i);
                    snippet_section.setOption("showInvisibles", data.show_i);
                    if (data.show_i === true) {
                        $('#show-invisibles').attr('checked', 'checked');
                    }
                    else {
                        $('#show-invisibles').removeAttr('checked');
                    }
                }
                if (data.wrap_t !== undefined) {
                    code_section.getSession().setUseWrapMode(data.wrap_t);
                    if (data.wrap_t === true) {
                        $('#wrap-text').attr('checked', 'checked');
                    }
                    else {
                        $('#wrap-text').removeAttr('checked');
                    }
                }
            }
        },
        error: function () {
            show_notification(
                'Error',
                'Unexpected error in loading configurations.',
                'OK',
                'btn-danger'
            );
        }
    });
}


function show_notification(title, body, button_text, button_type) {
    var n = $('#notification');
    var n_content = $('#notification-content');
    var n_title = $('#notification-title');
    var n_body = $('#notification-body');
    var n_btn = $('#notification-btn1');

    if (title !== undefined) {
        n_title.text(title);
        if (button_type && button_type === 'btn-danger') {
            n_title.css('color', '#aa0055');
            n_content.css('background-color', '#fff3f7');
        }
        else if (button_type && button_type === 'btn-info') {
            n_title.css('color', '#0063c5');
            n_content.css('background-color', '#eef9ff');
        }
        else {
            n_title.css('color', '#009688');
            n_content.css('background-color', '#f2fffa');
        }
    }
    if (body !== undefined) {
        n_body.html(body);
    }
    if (button_text !== undefined) {
        n_btn.text(button_text);
        n.attr('datatype', button_text)
    }
    if (button_type !== undefined) {
        n_btn.removeClass("btn-default btn-warning btn-success btn-info btn-danger").addClass(button_type);
    }
    n.modal('show');
}


function show_confirmation(title, body, button_text, button_type) {
    var c = $('#confirmation');
    var c_content = $('#confirmation-content');
    var c_title = $('#confirmation-title');
    var c_body = $('#confirmation-body');
    var c_btn2 = $('#confirmation-btn2');

    if (title !== undefined) {
        c_title.text(title);
        if (button_type && button_type === 'btn-danger') {
            c_title.css('color', '#aa0055');
            c_content.css('background-color', '#fff2f7');
        }
        else if (button_type && button_type === 'btn-info') {
            c_title.css('color', '#0063c5');
            c_content.css('background-color', '#eff9ff');
        }
        else {
            c_title.css('color', '#009688');
            c_content.css('background-color', '#f3fffa');
        }
    }
    if (body !== undefined) {
        c_body.html(body);
    }
    if (button_text !== undefined) {
        c_btn2.text(button_text);
        c.attr('datatype', button_text)
    }
    if (button_type !== undefined) {
        c_btn2.removeClass("btn-default btn-warning btn-success btn-info btn-danger").addClass(button_type);
    }
    c.modal('show');
}


function get_confirmation(callback) {
    var c = $('#confirmation');
    var c_body = $('#confirmation-body');
    var c_btn1 = $('#confirmation-btn1');
    var c_btn2 = $('#confirmation-btn2');

    c_btn1.click(function() {
        c.modal('hide');
        callback(false);
    });

    c_btn2.click(function() {
        // if modal has a form
        // `true` if the form has been fully filled, `false` vise versa
        // the modal will be hidden in callback function
        var inputs = c_body.find('input');
        if (inputs.length) {
            var filled = true;
            inputs.each(function(i) {
                if (!$(this).val()) {
                    filled = false;
                }
            });
            if (filled) {
                callback(true);
            }
            else {
                show_notification(
                    'Please Fill the Form',
                    'Please fill the form in order to proceed.',
                    'OK',
                    'btn-success'
                );
            }
        }
        // if the modal has no form, `true` and hide modal
        else {
            c.modal('hide');
            callback(true);
        }
    });
}
