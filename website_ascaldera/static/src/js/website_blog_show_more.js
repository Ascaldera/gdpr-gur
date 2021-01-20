/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('website_ascaldera.show_more', function (require) {
    "use strict";
    var ajax = require('web.ajax');

    function show_next_page(event) {
        event.preventDefault();
        $("div#show_more").removeClass('show');
        $("div#show_more").addClass('hide');
        $("div#scroll_paginator").removeClass('hide');
        $("div#scroll_paginator").addClass('show');
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
    function search_show_next_page(event) {
        event.preventDefault();
        $("div#show_more_search").removeClass('show');
        $("div#show_more_search").addClass('hide');
        $("div#scroll_paginator").removeClass('hide');
        $("div#scroll_paginator").addClass('show');
        var type = false;
        var page = 1;
        var span_type = $("input#post_type")[0].value;
        var page_span = $("input#page")[0].value;
        var query_span = $("input#search_query")[0].value;
        if (span_type.length > 0){
             if (span_type != 'All'){
                type = parseInt(span_type);
            }
             else{
                 type = span_type
             }
        }
        if (page_span.length > 0) {
            page = parseInt(page_span);
        }
        var next_page = page + 1;
        var count = 0;
        var last_call = 1;
        var wait_result = false;

        ajax.jsonRpc("/search_js_call", 'call', {
                                    'search_query': query_span,
                                    'blog_post_type': type,
                                    'page': next_page}).then(function (data) {
                try {
                    if (data) {
                        if (data.count >= 0){
                            count = data.count;

                            if (data.data_grid) {

                                page = data.page;
                                last_call = page;
                                $("#post_elements div.elements-list:last").after(data.data_grid);

                                $("input#page")[0].value = page.toString();

                                wait_result = false;

                                $("div#show_more_search").removeClass('hide');
                                $("div#show_more_search").addClass('show');
                                $("div#scroll_paginator").removeClass('show');
                                $("div#scroll_paginator").addClass('hide');

                            }
                            if (data.count == 0){

                                $("div#show_more_search").removeClass('show');
                                $("div#show_more_search").addClass('hide');
                                return;
                            }

                        }

                        else{
                            $("div#show_more_search").removeClass('show');
                            $("div#show_more_search").addClass('hide');
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

    function tag_show_next_page(event) {
        event.preventDefault();
        $("div#show_more_tag").removeClass('show');
        $("div#show_more_tag").addClass('hide');
        $("div#scroll_paginator").removeClass('hide');
        $("div#scroll_paginator").addClass('show');
        var type = false;
        var page = 1;

        var page_span = $("span#page");

        if (page_span.length > 0) {
            page = parseInt(page_span[0].innerText);
        }
        var tag_ids = false;
        var tag_ids_span = $("span#tag_ids");
        if (tag_ids_span.length > 0) {
            tag_ids = JSON.parse( tag_ids_span[0].innerText );
        }
        var next_page = page + 1;
        var count = 0;
        var last_call = 1;
        var wait_result = false;
        // tag_ids = 81;
        ajax.jsonRpc("/tag_js_call", 'call', {
                                    'tag_ids': tag_ids,
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

                                wait_result = false;

                                $("div#show_more_tag").removeClass('hide');
                                $("div#show_more_ta").addClass('show');
                                $("div#scroll_paginator").removeClass('show');
                                $("div#scroll_paginator").addClass('hide');

                            }
                            if (data.count == 0){

                                $("div#show_more_tag").removeClass('show');
                                $("div#show_more_tag").addClass('hide');
                                return;
                            }

                        }

                        else{
                            $("div#show_more_tag").removeClass('show');
                            $("div#show_more_tag").addClass('hide');
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


    $(document).ready(function(e) {



        if ($('#show_more').length) {
            $('#show_more').on('click', show_next_page);
        }
         if ($('#show_more_search').length) {
            $('#show_more_search').on('click', search_show_next_page);
        }
          if ($('#show_more_tag').length) {
            $('#show_more_tag').on('click', tag_show_next_page);


        }
    });

})