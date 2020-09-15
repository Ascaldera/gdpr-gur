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
        var page_span = $("span#page");
        if (page_span.length > 0) {
            page = parseInt(page_span[0].innerText);
        }
        offset = parseInt(offset);
        var last_call = 1
        var wait_result = false;
        var end = false;
        var overall_height = document.body.scrollHeight - 400;
        if ($('#scroll_paginator').length) {
            $(window).scroll(function(ev) {
                if ((window.innerHeight + window.scrollY) >= overall_height) {
                    try {
                        if(((window.innerHeight + window.scrollY) >= overall_height) && wait_result == false) {
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
                                    var next_page = page +1;
                                    wait_result = true;
                                    ajax.jsonRpc("/scroll_paginator", 'call', {
                                    'type': type,
                                    'subtype': subtype,
                                    'page': next_page
                                        }).then(function (data) {
                                            try {
                                                if (data && wait_result) {
                                                    if (data.count >= 0){
                                                        count = data.count;
                                                        if (data.data_grid) {
                                                            page = data.page;
                                                            last_call = page;
                                                            $("#post_elements div.elements-list:last").after(data.data_grid);
                                                            overall_height = document.body.scrollHeight - 500;
                                                            $("span#page").innerHTML = page.toString();
                                                            wait_result = false;

                                                        }
                                                        if (data.count == 0){
                                                            overall_height = 9999999999;
                                                            $("div#scroll_paginator").removeClass('show');
                                                            $("div#scroll_paginator").addClass('hide');
                                                            end = true;
                                                            return;
                                                        }

                                                    }

                                                    else{
                                                        $("div#scroll_paginator").removeClass('show');
                                                        $("div#scroll_paginator").addClass('hide');
                                                        return;
                                                    }
                                                }
                                            } catch (error) {
                                                console.log("" + error);
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