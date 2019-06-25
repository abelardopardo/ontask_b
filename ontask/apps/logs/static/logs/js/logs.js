let loadLogView = function () {
    let btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function() {
        $("#modal-item").modal("show");
      },
      success: function(data) {
        $("#modal-item .modal-content").html(data.html_form);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        $('#div-spinner').show();
        location.reload(true);
      }
    });
}

$(function () {
  // Preview
  $("#log-table").on("click", ".js-log-view", loadLogView);
});
