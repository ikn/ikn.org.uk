util = (() => {
    const util = {};

    const SCROLL_TOP_GAP = 6;
    const SCROLL_SHOW_HEIGHT = 100;
    const KEYCODE_ESCAPE = 27;

    // make `$el` visible in the window with the minimal amount of scrolling
    util.scrollIntoViewMinimal = ($el) => {
        const elTop = $el.offset().top;
        const viewTop = $(window).scrollTop();
        const viewBottom = viewTop + window.innerHeight;
        if (elTop < viewTop) {
            window.scrollBy(0, elTop - SCROLL_TOP_GAP - viewTop);
        } else if (elTop + SCROLL_SHOW_HEIGHT > viewBottom) {
            window.scrollBy(0, elTop + 100 - viewBottom);
        }
    };

    // remove highlighting from all elements
    util.removeHighlight = () => {
        $('.highlight').removeClass('highlight');
        window.location.hash = '';
    };

    $(document).keyup(evt => {
        if (evt.keyCode === KEYCODE_ESCAPE) {
            util.removeHighlight();
        }
    });

    // highlight elements in `$els`, triggered by the click event `evt`
    util.highlight = (evt, $els) => {
        util.removeHighlight();
        $els.addClass('highlight');
        if ($els.length > 0) {
            util.scrollIntoViewMinimal($($els[0]));
        }
        evt.preventDefault();
    };

    // when any element in `$els` is clicked, call the function `handler` as an
    // event handler
    util.onClickHighlight = ($els, handler) => {
        $els.find('[title]').css({ cursor: 'pointer' });
        $els.css({ cursor: 'pointer' }).on('click', handler);
    };

    return util;
})();
