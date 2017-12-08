var set_qbuilder = function (element_id, qbuilder_options) {
    id_formula_value = $(element_id).val();
    if (id_formula_value != "null" && id_formula_value != "{}") {
      qbuilder_options['rules'] = JSON.parse(id_formula_value);
    }
    $('#builder').queryBuilder(qbuilder_options);
};
var insert_query = function () {
    if (document.getElementById("id_filter") != null) {
      formula = $('#builder').queryBuilder('getRules');
      if (formula == null || !formula['valid']) {
        return false;
      }
      f_text = JSON.stringify(formula, undefined, 2);
      $('#id_filter').val(f_text);
    }
    return true;
}
var loadForm = function () {
    var btn = $(this);
    if ($(this).is('[class*="disabled"]')) {
      return;
    }
    if (document.getElementById("id_content") != null) {
      data = {'action_content': $("#id_content").summernote('code')};
    } else {
      data = {};
    }
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      data: data,
      beforeSend: function() {
        $("#modal-item").modal("show");
      },
      success: function(data) {
        $("#modal-item .modal-content").html(data.html_form);
        if (document.getElementById("id_formula") != null) {
          set_qbuilder('#id_formula', qbuilder_options);
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        location.reload();
      }
    });
}
var saveForm = function () {
    var form = $(this);
    if (document.getElementById("id_formula") != null) {
      formula = $('#builder').queryBuilder('getRules');
      if (formula == null || !formula['valid']) {
        return false;
      }
      f_text = JSON.stringify(formula, undefined, 2);
      $('#id_formula').val(f_text);
    }
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          if (data.html_redirect == "") {
            // If there is no redirect, simply refresh
            window.location.reload(true);
          } else {
            location.href = data.html_redirect;
          }
        }
        else {
          $("#modal-item .modal-content").html(data.html_form);
          if (document.getElementById("id_formula") != null) {
            set_qbuilder('#id_formula', qbuilder_options);
          }
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
