/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('website_ascaldera.show_more', function (require) {
    "use strict";
    var ajax = require('web.ajax');

    function show_next_page(event) {
        var type = false;
        var subtype = false;
        var page = 1;
        var span_type = $("span#type");
        var span_subtype = $("span#subtype");
        if (span_type.length > 0){
                                type = span_type[0].innerText;
                            }
        if (span_subtype.length > 0){
            subtype = span_subtype[0].innerText;
        }
        var page_span = $("span#page");
        if (page_span.length > 0) {
            page = parseInt(page_span[0].innerText);
        }
        var next_page = page + 1;
        var count = 0;
        var last_call = 1;
        var wait_result = false;
        $("div#show_more").removeClass('show');
        $("div#show_more").addClass('hide');
        $("div#scroll_paginator").removeClass('hide');
        $("div#scroll_paginator").addClass('show');
        ajax.jsonRpc("/scroll_paginator", 'call', {
                                    'type': type,
                                    'subtype': subtype,
                                    'page': next_page}).then(function (data) {
                try {
                    if (data) {
                        if (data.count >= 0){
                            count = data.count;

                            if (data.data_grid) {

                                page = data.page;
                                last_call = page;
                                $("#post_elements div.elements-list:last").after(data.data_grid);

                                $("span#page")[0].innerHTML = page.toString();
                                console.log(page_span[0].innerText);
                                wait_result = false;

                                $("div#show_more").removeClass('hide');
                                $("div#show_more").addClass('show');
                                $("div#scroll_paginator").removeClass('show');
                                $("div#scroll_paginator").addClass('hide');

                            }
                            if (data.count == 0){

                                $("div#show_more").removeClass('show');
                                $("div#show_more").addClass('hide');
                                return;
                            }

                        }

                        else{
                            $("div#show_more").removeClass('show');
                            $("div#show_more").addClass('hide');
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

    $(document).ready(function() {



        if ($('#show_more').length) {
            $('#show_more').on('click', show_next_page);

        }
    });

})