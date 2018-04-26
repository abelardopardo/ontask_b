var show_merge_figure = function() {
    console.log('Hello');
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
  $('#checkAll').click(function () {    
       $('input:checkbox').prop('checked', this.checked);    
   });

  // Delete column
  $("#rowview-table").on("click", ".js-rowview-delete", loadForm)
  $("#modal-item").on("submit", ".js-rowview-delete-form", saveForm)

  $(document).on('change','#id_how_merge', show_merge_figure);
});

window.onload = function(){
  show_merge_figure.call($("#id_how_merge"));
};
