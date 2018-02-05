var drop_down = $('.dropdown-toggle');

drop_down.click(function () {
    $(this).next('.dropdown-menu').slideToggle(250);
});

drop_down.focusout(function () {
    $(this).next('.dropdown-menu').slideUp(250);
});
