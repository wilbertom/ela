
$(function () {
    'use strict';

    $('#fileupload').fileupload({
        url: '/files/upload/'
    });

    $('#fileupload').addClass('fileupload-processing');

    $.ajax({
        url: $('#fileupload').fileupload('option', 'url'),
        dataType: 'json',
        context: $('#fileupload')[0]
    }).always(function () {
        $(this).removeClass('fileupload-processing');
    }).done(function (result) {
        $(this).fileupload('option', 'done')
            .call(this, $.Event('done'), {result: result});
    });

    $('#model_form').submit(function( event ) {
      event.preventDefault();

      var form = $(this);

      $.ajax({
         url   : '/experimentmodelview/api/create',
         type  : form.attr('method'),
         data  : form.serialize(),
         success: function(response) {
             $('#fileupload').fileupload({
                formData: {'experiment_id': response.id}
             });

             $('.start').click();

         },
      });
    });

});
