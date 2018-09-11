var column_move = function () {
    $.ajax({
      url: $(this).attr("href"),
      type: 'get',
      success: function(data) {
        if ('html_redirect' in data) {
          location.href = data.html_redirect;
        } else {
          location.reload(true);
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        $('#div-spinner').show();
        location.reload(true);
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

