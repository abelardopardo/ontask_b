var loadForm = function () {
    var btn = $(this);
    console.log('loading form: ' + btn.attr("data-url"));
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      data: {"dst": btn.attr("data-dst")},
      beforeSend: function() {
        $("#modal-item").modal("show");
      },
      success: function(data) {
        $("#modal-item .modal-content").html(data.html_form);
      }
    });

}
var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          if (data.dst == 'refresh') {
            /* $("#item-table tbody").html(data.html_item_list); */
            $("#item-table").html(data.html_item_list);
            $("#modal-item").modal("hide");
          }
          else {
            location.href = data.html_redirect;
          }
        }
        else {
          $("#modal-item .modal-content").html(data.html_form);
        }
      }
    });
    return false;
}


$(window).scroll(function () {
  var top = $(document).scrollTop();
  $('.corporate-jumbo').css({
    'background-position': '0px -'+(top/3).toFixed(2)+'px'
  });
  if(top > 50)
    $('.navbar').removeClass('navbar-transparent');
  else
    $('.navbar').addClass('navbar-transparent');
}).trigger('scroll');

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});