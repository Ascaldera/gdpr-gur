odoo.define('website_ascaldera', function(require) {
     'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {
        if (window.location.pathname.includes('/blog/News')){
            document.getElementById("post_type").value = "News";
        }
        else if (window.location.pathname.includes('/blog/Articles')){
            document.getElementById("post_type").value = "Articles";
        }
        else if (window.location.pathname.includes('/blog/Judicial-Practice')){
            document.getElementById("post_type").value = "Judicial-Practice";
        }
        else if (window.location.pathname.includes('/blog/Legislation')){
            document.getElementById("post_type").value = "Legislation";
        }
        else if (window.location.pathname.includes('/blog/Judicial-Practice/practice_slo')){
            document.getElementById("post_type").value = "SLO Information Commissioner's practice";
        }
        else if (window.location.pathname.includes('/blog/Judicial-Practice/judgement_SLO')){
            document.getElementById("post_type").value = "Judgments of the Slovenian Court";
        }
        else if (window.location.pathname.includes('/blog/Judicial-Practice/practice_foreign_oversight')){
            document.getElementById("post_type").value = "The practice of foreign oversight bodies";
        }
        else if (window.location.pathname.includes('/blog/Judicial-Practice/judgement_EU')){
            document.getElementById("post_type").value = "Judgments of the European Court of Justice";
        }
        else if (window.location.pathname.includes('/blog/Judicial-Practice/judgements_escp')){
            document.getElementById("post_type").value = "ECHR judgments";
        }
        else if (window.location.pathname.includes('/blog/Judicial-Practice/judgements_foreign')){
            document.getElementById("post_type").value = "Judgments of foreign courts";
        }
        else if (window.location.pathname.includes('/blog/Legislation/legislation_foreign')){
            document.getElementById("post_type").value = "Foreign legislation";
        }
        else if (window.location.pathname.includes('/blog/Legislation/legislation_slo')){
            document.getElementById("post_type").value = "Slovenian legislation";
        }
        else {
            document.getElementById("post_type").value = "All";
        }

        $('[id^=redirect_gdpr]').on("click",function() {
            var url = $(this).attr('data-id');
            if(url.indexOf('http') != -1){
               window.location.href = url;
            }
            else{window.location.href = 'http://' + url;}
        });

        $('.js_click').on('click', function(e) {
            var post_id = $(this).attr('data-id');
            ajax.jsonRpc('/blog/post', 'call', {
                'post_id': post_id,
            }).then(function (url) {
                window.location.href = url;
            });

        });

        $('#sidebar_arrow').on("click",function(e){
            var visible = $('#sidebar_arrow').attr("data-visible")
            $('#sidebar').toggle(500);
            $('.sidebar_bg').toggle(500);
            if (visible == "True")
            {
                $('.sidebar_icon').animate({'right': '2%'}, 500);
                $('#sidebar_arrow').attr("src","/website_ascaldera/static/src/img/icon-arrow-large-left.svg");
                $('#sidebar_arrow').attr("data-visible","False")
            }
            else
            {
                $('.sidebar_icon').animate({'right': '85%'}, 500);
                $('#sidebar_arrow').attr("src","/website_ascaldera/static/src/img/icon-arrow-large-right.svg");
                $('#sidebar_arrow').attr("data-visible","True")
            }

        })

        $( window ).resize(function() {
            var viewpoint_width = $(window).width();
            if (viewpoint_width > 991){
                var visible = $('#sidebar_arrow').attr("data-visible")
                if (visible == "True")
                {
                    $('#sidebar_arrow').trigger('click')
                }
                setTimeout(function(){
                    $("#sidebar").attr("style",'');
                    $(".sidebar_bg").attr("style",'');
                    $('.sidebar_icon').attr("style",'');
                 }, 700);
                
            }

        });

        $(".selector-lang").change(function () {
            var val = $(this).val();
            var url = encodeURIComponent(val.replace(/[&?]edit_translations[^&?]+/, ''));
            var firstSlash = val.indexOf('/');
            var secondSlash = val.indexOf('/', firstSlash+1);
            var redirect = {
                lang: val.substring(1, secondSlash),
                url: url,
                hash: encodeURIComponent(window.location.hash)
            };
            window.location.href = _.str.sprintf("/website/lang/%(lang)s?r=%(url)s%(hash)s", redirect);
        });



    });

 })
