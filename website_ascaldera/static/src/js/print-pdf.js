odoo.define('website_ascaldera.print_pdf', function (require) {
    "use strict";
    var ajax = require('web.ajax');

    $(function () {
        $("#pdf").click(function () {
            var head = $("head").html();
            var logo = '<img style="height: 100px;" src="/website_ascaldera/static/src/img/logo_GDPR_GURU.png"/>';
            var title = $(".block-title").find('.text').html();
            var content = $(".raw_content").html();

            var frame = $('<iframe />');
            frame[0].name = "frame";
            $("body").append(frame);
            var frameDoc = frame[0].contentWindow ? frame[0].contentWindow : frame[0].contentDocument.document ? frame[0].contentDocument.document : frame[0].contentDocument;
            frameDoc.document.open();

            //Create a new HTML document.
            frameDoc.document.write('<html><title>' + title + '</title>');
            frameDoc.document.write('<head>'+ head +'</head>')
            frameDoc.document.write('<body>');

            //Append the DIV contents.
            frameDoc.document.write('<br/>');
            frameDoc.document.write(logo);
            frameDoc.document.write('<br/>');
            frameDoc.document.write('<h1>' + title + '</h1>');
            frameDoc.document.write(content);
            frameDoc.document.write('</body></html>');
            frameDoc.document.close();

            setTimeout(function () {
                window.frames["frame"].focus();
                window.frames["frame"].print();
                frame.remove();
            }, 500);
        });
    });

})