$(document).ready(() => {

    // toggle `$el` visibility, and adjust text of the activating button
    // `$buttonEl` accordingly
    const toggleVisible = ($el, $buttonEl) => {
        const show = $el.css('display') === 'none';
        $el.css({ display: show ? '' : 'none' });
        $buttonEl.html(show ? '&#x25b2' : '&#x25bc;');
    };

    // collapse extra composition groupings by default
    jQuery('.composition-extra-groupings').each((i, groupingEl) => {
        const $groupingEl = $(groupingEl);
        if ($groupingEl.children().length === 0) {
            return;
        }

        const $buttonEl = $('<button></button>')
            .attr('type', 'button')
            .attr('class', 'hr-button')
            .attr('title', 'show additional groupings');
        $groupingEl.before($buttonEl);

        toggleVisible($groupingEl, $buttonEl);
        $buttonEl.on('click', () => toggleVisible($groupingEl, $buttonEl));
    });

    // when clicking a role, highlight it in compositions
    util.onClickHighlight($('#roles h3[data-role-id]'), evt => {
        const roleId = $(evt.delegateTarget).data('role-id');
        util.highlight(
            evt, $('#compositions td[data-role-id="' + roleId + '"]'));
    });

    // when clicking a providing role, highlight the role
    util.onClickHighlight($('#roles .providing-role'), evt => {
        const roleId = $(evt.delegateTarget).data('role-id');
        util.highlight(evt, $('#roles h3[data-role-id="' + roleId + '"]'));
    });

    // when clicking a composition, highlight all its roles
    util.onClickHighlight($('#compositions table'), evt => {
        const $els = $([]);
        const roleIds = $(evt.delegateTarget)
            .find('td[data-role-id]')
            .each((i, el) => {
                const roleId = $(el).data('role-id');
                $.merge($els, $('#roles h3[data-role-id="' + roleId + '"]'));
            });
        util.highlight(evt, $els);
    });

});
