function click_and_send(message) {
    var code = code_section.getValue();
    if (code) {
        var sent_info = {
            message: message,
            code: code
        };
        send_for_formatting(sent_info);
        if (message === 'judge') {
            $('#overlay').fadeIn();
        }
    }
}


function send_for_formatting(sent_info) {
    $.ajax({
        contentType: "application/json",
        data: JSON.stringify(sent_info),
        type: 'POST',
        url: '/code/code_formatting',
        dataType: 'json',
        success: function(data, status, request) {
            // normal case: just display result code
            if (data.code) {
                code_section.setValue(data.code);
            }
            // judge case: show banner based on result
            else if (data.judge_result) {
                $('#overlay').fadeOut();
                var judge_result = data.judge_result;
                if (!judge_result.passed) {
                    /* judge not passed */
                    failed_count += 1;
                    var error_start = judge_result.error_start;
                    var error_end = judge_result.error_end;
                    var spelling = judge_result.spelling;
                    var spelling_last = judge_result.spelling_last;
                    var message = "Error between &lt;line [<span style=\"font-family:courier;font-size:18px;font-weight:bold\">" + error_start[0] + "</span>] position <span style=\"font-family:courier;font-size:18px;font-weight:bold\">" + error_start[1] + "</span>&gt;" +
                              " and &lt;line [<span style=\"font-family:courier;font-size:18px;font-weight:bold\">" +  error_end[0] + "</span>] position <span style=\"font-family:courier;font-size:18px;font-weight:bold\">" + error_end[1] + "</span>&gt;. " +
                              "\nCurrent spelling &lt;<span style=\"font-family:courier;font-size:18px;font-weight:bold\">" + spelling + "</span>&gt;, last processed spelling &lt;<span style=\"font-family:courier;font-size:18px;font-weight:bold\">" + spelling_last + "</span>&gt;. ";
                    if (judge_result.analysis) {
                        var analysis_message = "";
                        if (judge_result.analysis === "end") {
                            analysis_message = "The [<span style=\"font-family:courier;font-size:18px;font-weight:bold\">end</span>] tag on line [<span style=\"font-family:courier;font-size:18px;font-weight:bold\">" + error_start[0] + "</span>] does not match any condition / loop.";
                        }
                        else if (judge_result.analysis === 'condition') {
                            analysis_message = "The condition / loop on line [<span style=\"font-family:courier;font-size:18px;font-weight:bold\">" + error_start[0] + "</span>] might not be closed with an [<span style=\"font-family:courier;font-size:18px;font-weight:bold\">end</span>] tag properly.";

                        }
                        message += analysis_message;
                    }

                    $.notify({
                            icon: 'glyphicon glyphicon-remove-sign',
                            title: "Judge Failed: ",
                            message: message
                        },
                        {
                            placement:{align: 'left'},
                            timer: 0,
                            type: 'failed',
                            animate: {enter: 'animated fadeInLeft', exit: 'animated fadeOutLeft'},
                            offset: {
                                x: 8,
                                y: 51
                            }
                        }
                    );
                }
                else {
                    /* judge passed */
                    success_count += 1;
                    $.notify({
                            icon: 'glyphicon glyphicon-ok-sign',
                            title: "Judge Passed: ",
                            message: "The code should have no syntax error."
                        },
                        {
                            placement:{align: 'left'},
                            type: 'passed',
                            animate: {enter: 'animated fadeInLeft', exit: 'animated fadeOutLeft'},
                            offset: {
                                x: 8,
                                y: 51
                            }
                        }
                    );
                }
            }
        },
        error: function() {
            alert('Unexpected error in sending code content');
        }
    });
}


// https://stackoverflow.com/questions/22581345/click-button-copy-to-clipboard-using-jquery
function copy_to_clipboard(elem) {
    // create hidden text element, if it doesn't already exist
    var targetId = "_hiddenCopyText_";
    var isInput = elem.tagName === "INPUT" || elem.tagName === "TEXTAREA";
    var origSelectionStart, origSelectionEnd;
    if (isInput) {
        // can just use the original source element for the selection and copy
        target = elem;
        origSelectionStart = elem.selectionStart;
        origSelectionEnd = elem.selectionEnd;
    } else {
        // must use a temporary form element for the selection and copy
        target = document.getElementById(targetId);
        if (!target) {
            var target = document.createElement("textarea");
            target.style.position = "absolute";
            target.style.left = "-9999px";
            target.style.top = "0";
            target.id = targetId;
            document.body.appendChild(target);
        }
        target.textContent = elem.textContent;
    }
    // select the content
    var currentFocus = document.activeElement;
    target.focus();
    target.setSelectionRange(0, target.value.length);

    // copy the selection
    var succeed;
    try {
          succeed = document.execCommand("copy");
    } catch(e) {
        succeed = false;
    }
    // restore original focus
    if (currentFocus && typeof currentFocus.focus === "function") {
        currentFocus.focus();
    }

    if (isInput) {
        // restore prior selection
        elem.setSelectionRange(origSelectionStart, origSelectionEnd);
    } else {
        // clear temporary content
        target.textContent = "";
    }
    return succeed;
}
