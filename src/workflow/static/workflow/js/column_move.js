var column_move = function () {
    $.ajax({
      url: $(this).attr("href"),
      type: 'get',
      success: function(data) {
        if ('html_redirect' in data) {
          location.href = data.html_redirect;
        } else {
          location.reload();
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        location.reload();
      }
    });
    return false;
}

$(function () {
  // Moving columns
  $(document).on("click", ".column-move-prev",   column_move);
  $(document).on("click", ".column-move-next",   column_move);
  $(document).on("click", ".column-move-top",    column_move);
  $(document).on("click", ".column-move-bottom", column_move);
});

