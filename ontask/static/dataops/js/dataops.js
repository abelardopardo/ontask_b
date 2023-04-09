var show_merge_figure = function() {
    var option = $(this).val();
    if (option == 'inner') {
        $("#merge_inner").show();
    } else {
        $("#merge_inner").hide();
    }

    if (option == 'outer') {
        $("#merge_outer").show();
    } else {
        $("#merge_outer").hide();
    }

    if (option == 'left') {
        $("#merge_left").show();
    } else {
        $("#merge_left").hide();
    }

    if (option == 'right') {
        $("#merge_right").show();
    } else {
        $("#merge_right").hide();
    }

    return;
}

$(function () {
  $("#checkAll").click(function () {
       $("input[id*='id_upload_']").prop("checked", this.checked);
  });

  // Delete column
  $("#rowview-table").on("click", ".js-rowview-delete", loadForm)
  $("#modal-item").on("submit", ".js-rowview-delete-form", saveForm)

  $(document).on('change','#id_how_merge', show_merge_figure);

  $("#plugin-admin-table").on("click", ".js-plugin-diagnose", loadForm);

  $("#transform-table, #plugin-admin-table").on(
  "click", ".js-plugin-show-description", loadForm);

  // Toggle plugin is_enabled
  $("#plugin-admin-table").on("change", ".plugin-toggle", toggleCheckBox);
});

window.onload = function(){
  if (document.getElementById("id_how_merge") != null) {
    show_merge_figure.call($("#id_how_merge"));
  }
  if (document.getElementById("id_columns") != null) {
    set_element_select("#id_columns");
  }
  setDateTimePickers();
};
$(document).ready(function() {
  if (location.hash) {
    $("a[href='" + location.hash + "']").tab("show");
  }
  $(document.body).on("click", "a[data-bs-toggle]", function(event) {
    location.hash = this.getAttribute("href");
  });
});
$(window).on("popstate", function() {
  let anchor = location.hash || $("a[data-bs-toggle='tab']").first().attr("href");
  $("a[href='" + anchor + "']").tab("show");
});
$('#dataops-get-plugin-info-to-run form').validate({
    ignore: ".ignore",
    invalidHandler: function(e, validator){
        if(validator.errorList.length) {
          $('#dataops-get-plugin-info-tabs a[href="#' + jQuery(validator.errorList[0].element).closest(
            ".tab-pane").attr('id') + '"]').tab('show')
          $('#div-spinner').hide();
        }
    }
});
