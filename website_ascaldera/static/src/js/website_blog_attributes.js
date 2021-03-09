/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('website_ascaldera.attributes', function (require) {
    "use strict";
    var ajax = require('web.ajax');

    function   _onChangeAttribute(ev) {
        if (!ev.isDefaultPrevented()) {      
            ev.preventDefault();
            if(navigator.userAgent.toLowerCase().indexOf('firefox') > -1) {
                $("#search").clone().appendTo("body").submit(); // FF only
              } else {
                $("#search").submit(); // works under IE and Chrome, but not FF  
              }
        }
    };
    function   _onAttribSection(ev) {
        var self = ev.currentTarget;
        var main_li = $(self).parent("div").parent("div")
        var ul_H = main_li.find("ul").height();

        var main_ul = main_li.find("ul");

        if (main_ul.hasClass("open_ul")) {
            main_ul.removeClass("open_ul");
            $(self).removeClass('te_fa-minus');
            main_ul.toggle('slow');

        } else {
            main_ul.addClass("open_ul");
            $(self).addClass('te_fa-minus');
            main_ul.toggle('slow');
        }
    };

    $(document).ready(function(e) {
        if ($('form.js_attributes input, form.js_attributes select').length) {
            $('form.js_attributes input, form.js_attributes select').on('change', _onChangeAttribute);
        }
        $('.te_attr_title').on('click', _onAttribSection);

        $('#search_tags').on('keyup', function() {
            var value = $(this).val().toLowerCase();
            $('#tags li').filter(function(){
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
       });
    });

})