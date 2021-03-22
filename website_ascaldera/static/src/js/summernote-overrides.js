//console.log($("[name='content'] > textarea"));

(function (factory) {
    if (typeof define === 'function' && define.amd) {
      define(['jquery'], factory);
    } else if (typeof module === 'object' && module.exports) {
      module.exports = factory(require('jquery'));
    } else {
      factory(window.jQuery);
    }
  }
  (function ($) {

    const cleaner = {
        action: 'both', 
        newline: '<br>',
        keepHtml: true,
        //keepOnlyTags: ['<p>', '<br>', '<ul>', '<li>', '<b>', '<strong>','<i>', '<a>'], 
        keepClasses: false,
        badTags: ['style', 'script', 'applet', 'embed', 'noframes', 'noscript'],
        badAttributes: ['style', 'start'],
    };

    function cleanText (txt, nlO) {
        var out = txt;
        if (!cleaner.keepClasses) {
        var sS = /(\n|\r| class=(")?Mso[a-zA-Z]+(")?)/g;
            out = txt.replace(sS, ' ');
        }
        var nL = /(\n)+/g;
        out = out.replace(nL, nlO);

        if (cleaner.keepHtml) {
            var cS = new RegExp('<!--(.*?)-->', 'gi');
                out = out.replace(cS, '');
            var tS = new RegExp('<(/)*(meta|link|\\?xml:|st1:|o:|font)(.*?)>', 'gi');
                out = out.replace(tS, '');
            var bT = cleaner.badTags;
            for (var i = 0; i < bT.length; i++) {
                tS = new RegExp('<' + bT[i] + '\\b.*>.*</' + bT[i] + '>', 'gi');
                out = out.replace(tS, '');
            }
            /*
            var allowedTags = cleaner.keepOnlyTags;
            if (typeof(allowedTags) == "undefined") allowedTags = [];
            if (allowedTags.length > 0) {
                allowedTags = (((allowedTags||'') + '').toLowerCase().match(/<[a-z][a-z0-9]*>/g) || []).join('');
                var tags = /<\/?([a-z][a-z0-9]*)\b[^>]*>/gi;
                        out = out.replace(tags, function($0, $1) {
                return allowedTags.indexOf('<' + $1.toLowerCase() + '>') > -1 ? $0 : ''
                });
            }
            */
            var bA = cleaner.badAttributes;
            for (var ii = 0; ii < bA.length; ii++ ) {
                //var aS=new RegExp(' ('+bA[ii]+'="(.*?)")|('+bA[ii]+'=\'(.*?)\')', 'gi');
                var aS = new RegExp(' ' + bA[ii] + '=[\'|"](.*?)[\'|"]', 'gi');
                out = out.replace(aS, '');
                aS = new RegExp(' ' + bA[ii] + '[=0-9a-z]', 'gi');
                out = out.replace(aS, '');
            }
        }
        console.log(out);
        return out;
    };

    $(".note-editable").on("paste", function(e){
        // access the clipboard using the api
        if (cleaner.action == 'both' || cleaner.action == 'paste') {
            e.preventDefault();
            var ua   = window.navigator.userAgent;
            console.log(ua);
            var msie = ua.indexOf("MSIE ");
                msie = msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./);
            var ffox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
            
            if (msie)
                var text = window.clipboardData.getData("Text");
            else {
                var text = e.originalEvent.clipboardData.getData(cleaner.keepHtml ? 'text/html' : 'text/plain');
            }
            if (text) {
                if (msie || ffox)
                    setTimeout(function () {
                        window.document.execCommand('insertHtml', false, cleanText(text, cleaner.newline));
                    }, 10);
                else {
                    window.document.execCommand('insertHtml', false, cleanText(text, cleaner.newline));
                }
            }
            else {
                text = e.originalEvent.clipboardData.getData('text/plain');
                text = text.replace(/\n\r?/g, "<br>");
                window.document.execCommand('insertHtml', false, text);
            }
        }
    });
}));