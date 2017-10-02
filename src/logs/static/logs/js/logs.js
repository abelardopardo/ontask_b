var loadLogView = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function() {
        $("#modal-item").modal("show");
      },
      success: function(data) {
        $("#modal-item .modal-content").html(data.html_form);
      }
    });
}

$(function () {
  // Preview
  $("#log-table").on("click", ".js-log-view", loadLogView);
});
