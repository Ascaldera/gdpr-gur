/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('website_ascaldera.scroll_paginator', function (require) {
    "use strict";
    
    var ajax = require('web.ajax');

    $(document).ready(function() {
        var count = 10;
        var page = 1;
        var ppg = 8;
        var offset = 0;
        count = parseInt(count);
        page = parseInt(page);
        offset = parseInt(offset);
        var overall_height = $(document).height() -250;
        if ($('#scroll_paginator').length) {
            $(window).scroll(function() {
                if(($(window).scrollTop() + $(window).height() > overall_height) && (count > 0)) {
                    try {
                        if(($(window).scrollTop() + $(window).height() > overall_height) && (count > 0)) {
                            offset = ppg;
                            ppg = ppg + 8;
                            $("div#scroll_paginator").addClass('show');
                            var type = false;
                            var subtype = false;
                            var span_type = $("span#type");
                            var span_subtype = $("span#subtype");
                            if (span_type.length > 0){
                                type = span_type[0].innerText;
                            }
                            if (span_subtype.length > 0){
                                subtype = span_subtype[0].innerText;
                            }
                            if (type != false){
                                if (count > 0){
                                    ajax.jsonRpc("/scroll_paginator", 'call', {
                                    'type': type,
                                    'subtype': subtype,
                                    'page': page + 1
                                        }).then(function (data) {
                                            if ($(window).scrollTop() + $(window).height() > overall_height) {
                                                try {
                                                    if (data) {
                                                        count = data.count;
                                                        var path = window.location.pathname;
                                                        if (data.data_grid) {
                                                            page = page + 1;
                                                        }
                                                        $("#post_elements div.elements-list:last").after(data.data_grid);
                                                        overall_height = $(document).height() - 250;
                                                        if (data.count == 0) {
                                                            $("div#scroll_paginator").removeClass('show');
                                                            $("div#scroll_paginator").addClass('hide');
                                                        }
                                                    }
                                                } catch (error) {
                                                    console.log("" + error);
                                                }
                                            }

                                        }).fail(function (error) {
                                    });
                                }

                            }


                        }
                    } catch (error) {
                        console.log("" + error);
                    }

                }
            });
        }
    });

})