$(document).ready(() => {

    // when clicking a providing role, highlight the role
    util.onClickHighlight($('#roles .providing-role'), evt => {
        const roleId = $(evt.delegateTarget).data('role-id');
        util.highlight(evt, $('#roles h3[data-role-id="' + roleId + '"]'));
    });

});
