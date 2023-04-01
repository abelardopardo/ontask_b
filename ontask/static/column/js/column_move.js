let send_column_reorder = function(elem, data) {
  data["csrfmiddlewaretoken"] = window.CSRF_TOKEN;
  $.ajax({
    url: elem.attr("data-url"),
    data: data,
    type: 'post',
    dataType: 'json',
    success: function (data) {
      if (typeof data.html_redirect != 'undefined') {
        location.href = data.html_redirect;
      } else {
        $('#column-table').dataTable().api().ajax.reload();
      }
    },
    error: function(jqXHR, textStatus, errorThrown) {
      $('#div-spinner').show();
      location.reload(true);
    }
  });
};
let column_reorder = function(e, settings, details ) {
  let data = {'from_name': settings.aoColumns[details.mapping[details.from]].data,
              'to_name': settings.aoColumns[details.mapping[details.to]].data}
  send_column_reorder($(this), data);
};
var row_reordered = function(e, details, edit) {
  if (details.length == 0) {
    return;
  }
  let idx = 0;
  if (details[0].oldPosition - details[0].newPosition == 1) {
    idx = details.length - 1;
  }
  send_column_reorder(
    $(this),
    {'from_name': details[idx].oldData.trim(),
     'to_name': details[idx].newData.trim()});
};
