let loadLogView = function () {
  let btn = $(this);
  previousActiveElement = btn;
  if (btn.is("[class*='dropdown-item']")) {
    previousActiveElement =  btn.parent().siblings()[0];
  }
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

  // Timeline
  $("#timeline").on("click", ".js-log-view", loadLogView);
});
