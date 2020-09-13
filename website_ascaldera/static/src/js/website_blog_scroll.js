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
                            var url = window.location.href;
                            var splitter = url.split('/');
                            var type = false
                            var subtype = false
                            type = splitter[4]
                            var type_end = type.indexOf("?");
                            if (type_end > 0) {
                                type = type.substring(0, type_end);
                            }
                            if (splitter.length > 5) {
                                subtype = splitter[5]
                                var subtype_end = type.indexOf("?");
                                if (subtype_end > 0) {
                                    subtype = subtype.substring(0, subtype_end);
                                }
                            }
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
                    } catch (error) {
                        console.log("" + error);
                    }

                }
            });
        }
    });

})