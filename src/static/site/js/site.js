var loadForm = function () {
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
      },
      error: function(jqXHR, textStatus, errorThrown) {
        location.reload();
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
          location.href = data.html_redirect;
        }
        else {
          $("#modal-item .modal-content").html(data.html_form);
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        location.reload();
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