# -*- coding: utf-8 -*-
#V1.3

import heapq

import requests
from dateutil.parser import parse

from odoo import http
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.web.controllers.main import Binary
from odoo.http import request
import base64
from bs4 import BeautifulSoup
import logging
import json
import odoo
from odoo.tools import crop_image, topological_sort, html_escape, pycompat

def check_lang_to_installed(env, website):
    for code in ['sl_SI', 'it_IT', 'en_US']:
        lang = env['res.lang'].search([('code', '=', code)], limit=1)
        if not lang:
            lang = install_lang(env, code)
        if lang and lang not in website.language_ids:
            website.language_ids = [(4, lang.id)]


def install_lang(env, code):
    base_install = env["base.language.install"].create({'lang': code})
    base_install.lang_install()
    env["base.update.translations"].create({'lang': code}).act_update()
    lang = env['res.lang'].search([('code', '=', code)], limit=1)
    return lang

def binary_content(xmlid=None, model='ir.attachment', id=None, field='datas', unique=False,
                   filename=None, filename_field='datas_fname', download=False, mimetype=None,
                   default_mimetype='application/octet-stream', related_id=None, access_mode=None, access_token=None,
                   env=None):
    return request.registry['ir.http'].binary_content(
        xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
        filename_field=filename_field, download=download, mimetype=mimetype,
        default_mimetype=default_mimetype, related_id=related_id, access_mode=access_mode, access_token=access_token,
        env=env)


class Binary(http.Controller):

    @http.route(['/website/image/<model>/<id>/<field>/<int:width>x<int:height>/<string:crop_setting>'
    ], type='http', auth="public", website=False, multilang=False)
    def content_imagecontent_image(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                      filename_field='datas_fname', unique=None, filename=None, mimetype=None,
                      download=None, width=0, height=0, crop=False, related_id=None, access_mode=None,
                      access_token=None, avoid_if_small=False, upper_limit=False, signature=False,crop_setting = "crop", **kw):

        status, headers, content = binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            default_mimetype='image/png', related_id=related_id, access_mode=access_mode, access_token=access_token)

        crop = False
        if crop_setting == 'crop':
            crop = True
        else:
            crop = False

        if headers and dict(headers).get('Content-Type', '') == 'image/svg+xml':  # we shan't resize svg images
            height = 0
            width = 0
        else:
            height = int(height or 0)
            width = int(width or 0)

        if not content:
            content = base64.b64encode(self.placeholder(image='placeholder.png'))
            headers = self.force_contenttype(headers, contenttype='image/png')
            if not (width or height):
                suffix = field.split('_')[-1]
                if suffix in ('small', 'medium', 'big'):
                    content = getattr(odoo.tools, 'image_resize_image_%s' % suffix)(content)

        if crop and not(width or height):
            content = crop_image(content, type='center', size=(width, height), ratio=(1, 1))
        elif (width or height):
            if not upper_limit:
                # resize maximum 500*500
                if width > 1024:
                    width = 1024
                if height > 1024:
                    height = 1024
            content = odoo.tools.image_resize_image(base64_source=content, size=(width or None, height or None),
                                                    encoding='base64', upper_limit=upper_limit,
                                                    avoid_if_small=avoid_if_small)

        image_base64 = base64.b64decode(content)
        headers.append(('Content-Length', len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status_code = status
        return response



class Website(Website):
    """Controller Website."""

    def get_external_post_count(self):
        url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon'
        res = requests.get(url)
        count = 0
        if(res):
            result = res.json()
            count = len(result['_embedded']['documents'])
        return count
    
    @http.route(auth='public')
    def index(self, data={}, **kw):
        """Controller to replace home page with main page.."""
        super(Website, self).index(**kw)
        blog_post = request.env['blog.post']     
        
        fav_tags_1 = request.env['blog.tag'].sudo().search([])
        search_list_first=[]
        search_list_second=[]
        list_first=[]
        list_second=[]
        for f in fav_tags_1:
            list_first.append((f.id,len(f.post_ids)))
            list_second.append((f.id,len(f.post_ids)))
        list_first.sort(key=lambda x: x[1],reverse=True)
        list_second.sort(key=lambda x: x[1],reverse=True)
        if(len(list_first) > 10):
            list_first=list_first[:10]
        if (len(list_second) > 10):
            list_second=list_second[10:]
        for x in list_first:
            search_list_first.append(x[0])
        for x in list_second:
            search_list_second.append(x[0])
        fav_tags=request.env['blog.tag'].sudo().search([('id','in',search_list_first)])
        unfav_tags=request.env['blog.tag'].sudo().search([('id','in',search_list_second)])
        
        """fav_tags = request.env['blog.tag'].sudo().search([])"""
        # Get max three news posts
        news_id = request.env.ref(
            'website_ascaldera.blog_post_type_news')

        most_read_news_post = blog_post.sudo().search(
            [('blog_post_type_id', '=', news_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))], limit=3,order='visits,published_date desc')


        # Get max three article posts
        article_id = request.env.ref(
            'website_ascaldera.blog_post_type_article')

        most_read_article_post = blog_post.sudo().search(
            [('blog_post_type_id', '=', article_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))], order='visits,published_date desc',limit=3)
        # Get max three practice posts
        practice_id = request.env.ref(
            'website_ascaldera.blog_post_type_judicial_practice')

        most_read_practice_post = blog_post.sudo().search(
            [('blog_post_type_id', '=', practice_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))], order='visits,published_date desc', limit=3)
        grid_images_posts = blog_post.sudo().search(
            [('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))],order='published_date desc', limit=7)

        check_lang_to_installed(request.env, request.website)
        
        return request.render("website_ascaldera.main_blog_post", {
            'most_read_news_post': most_read_news_post,
            'most_read_article_post': most_read_article_post,
            'most_read_practice_post': most_read_practice_post,
            'grid_images_posts': grid_images_posts,
            'fav_tags': fav_tags,
            'unfav_tags': unfav_tags,
            'external_post_count': self.get_external_post_count(),
        })


class WebsiteBlog(WebsiteBlog):
    """Controller WebsiteBlog."""

    def get_external_post_count(self):
        url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon'
        res = requests.get(url)
        count = 0;
        if(res):
            result = res.json()
            count = len(result['_embedded']['documents'])
        return count

    def fav_tags_get(self):
        fav_tags = request.env['blog.tag'].sudo().search([])
        search_list=[]
        list=[]
        for f in fav_tags:
            list.append((f.id,len(f.post_ids)))
        list.sort(key=lambda x: x[1],reverse=True)
        if(len(list) > 10):
            list=list[:10]
        for x in list:
            search_list.append(x[0])
        return request.env['blog.tag'].sudo().search([('id','in',search_list)])
    
    def unfav_tags_get(self):
        unfav_tags = request.env['blog.tag'].sudo().search([])
        search_list=[]
        list=[]
        for f in unfav_tags:
            list.append((f.id,len(f.post_ids)))
        list.sort(key=lambda x: x[1],reverse=True)
        if(len(list) > 10):
            list=list[10:]
        for x in list:
            search_list.append(x[0])
        return request.env['blog.tag'].sudo().search([('id','in',search_list)])

    @http.route([
        '/blog',
    ], type='http', auth="public", website=True)
    def blogs(self, **post):
        """Controller to render new template with most visited data."""
        blog_post = request.env['blog.post']
        """fav_tags_1 = request.env['blog.tag'].sudo().search([])
        search_list=[]
        list=[]
        for f in fav_tags_1:
            list.append((f.id,len(f.post_ids)))
        list.sort(key=lambda x: x[1])
        if(len(list) > 1):
            list=list[4:]
        for x in list:
            search_list.append(x[1])
        fav_tags=request.env['blog.tag'].sudo().search([('id','in',search_list)])"""
        
        """fav_tags = request.env['blog.tag'].sudo().search([],limit=3)"""        
        posts = blog_post.sudo().search(
            [('lang', '=', request.env.context.get('lang'))], order='id desc')
        # Get max three news posts
        news_id = request.env.ref(
            'website_ascaldera.blog_post_type_news')
        news_posts_visits = [p.visits for p in blog_post.sudo().search(
            [('blog_post_type_id', '=', news_id.id),
             ('lang', '=', request.env.context.get('lang'))])]
        news_highest_visits = heapq.nlargest(3, news_posts_visits)
        most_read_news_post = blog_post.sudo().search(
            [('blog_post_type_id', '=', news_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang')),
             ('visits', 'in', news_highest_visits)], limit=3)
        # Get max three article posts
        article_id = request.env.ref(
            'website_ascaldera.blog_post_type_article')
        article_posts_visits = [p.visits for p in blog_post.sudo().search(
            [('blog_post_type_id', '=', article_id.id),
             ('lang', '=', request.env.context.get('lang'))])]
        article_highest_visits = heapq.nlargest(3, article_posts_visits)
        most_read_article_post = blog_post.sudo().search(
            [('blog_post_type_id', '=', article_id.id),
             ('website_published', '=', True),
             ('visits', 'in', article_highest_visits),
             ('lang', '=', request.env.context.get('lang'))], limit=3)
        # Get max three practice posts
        practice_id = request.env.ref(
            'website_ascaldera.blog_post_type_judicial_practice')
        practice_posts_visits = [p.visits for p in blog_post.sudo().search(
            [('blog_post_type_id', '=', practice_id.id),
             ('lang', '=', request.env.context.get('lang'))])]
        practice_highest_visits = heapq.nlargest(3, practice_posts_visits)
        most_read_practice_post = blog_post.sudo().search(
            [('blog_post_type_id', '=', practice_id.id),
             ('website_published', '=', True),
             ('visits', 'in', practice_highest_visits),
             ('lang', '=', request.env.context.get('lang'))], limit=3)
        check_lang_to_installed(request.env, request.website)
        return request.render("website_ascaldera.main_blog_post", {
            'posts': posts,
            'most_read_news_post': most_read_news_post,
            'most_read_article_post': most_read_article_post,
            'most_read_practice_post': most_read_practice_post,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(),
        })

    @http.route([
        '''/blog/<model("blog.blog", "[('website_id', 'in', (False, current_website_id))]"):blog>/post/<model("blog.post", "[('blog_id','=',blog[0])]"):blog_post>''',
    ], type='http', auth="public", website=True)
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        """Controller to render new template "blog_post_content"."""
        values = {
            'blog': blog,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'blog_post': blog_post,
            'main_object': blog_post,
            'external_post_count': self.get_external_post_count(),
        }
        response = request.render("website_ascaldera.blog_post_content", values)
        request.session[request.session.sid] = request.session.get(request.session.sid, [])
        if not (blog_post.id in request.session[request.session.sid]):
            request.session[request.session.sid].append(blog_post.id)
            # Increase counter
            blog_post.sudo().write({
                'visits': blog_post.visits + 1,
            })
        return response


    @http.route([
        '''/blog/post/''',
    ], type='json', methods=['POST'], auth='none', website=True)
    def blog_posts(self, post_id):
        blog_post = request.env['blog.post'].sudo().browse(int(post_id))
        url = '/blog/%s/post/%s' % (slug(blog_post.blog_id), slug(blog_post))
        return url

    @http.route([
        '''/blog/tag/<model("blog.tag"):tag_id>''',
    ], type='http', auth="public", website=True)
    def blog_tag(self, tag_id, **post):
        """Controller to fetch blog based on tags."""
        return request.render("website_ascaldera.blog_post_tags", {
            'tag_ids': tag_id,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'blog_post_ids': tag_id.post_ids.filtered(lambda r: r.lang == request.env.context.get('lang')),
            'external_post_count': self.get_external_post_count(),
        })

    @http.route([
        '/blog/search',
    ], type='http', auth="public", website=True)
    def blog_post_search(self, **post):
        values = {'external_post_count': self.get_external_post_count(), }
        if post:
            search_query = post.get('query')
            values.update({'query': search_query})
            post_type = post.get('post_type')
            post_subcategory = post.get('sub_category_main')
            blog_post_pool = request.env['blog.post'].sudo()
            if post_type:
                if post_type in ['News', 'Articles', 'Judicial-Practice', 'Legislation'] and post_subcategory != "SLO Information Commissioner\'s practice":
                    posts = blog_post_pool.search(
                        ['|', '|', ('content', 'ilike', search_query),
                         ('name', 'ilike', search_query),
                         ('subtitle', 'ilike', search_query)])
                    blog_post = posts.filtered(
                        lambda l: l.blog_post_type_id.name == post_type and l.website_published == True)
                    if blog_post:
                        values.update({'blog_post': blog_post})
                elif post_subcategory == 'SLO Information Commissioner\'s practice':
                    url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon'
                    res = requests.get(url)
                    result = 0
                    if(res):
                        result = res.json()
                    count = 0
                    vals = {}
                    if(result != 0):
                        for res in result['_embedded']['documents']:
                            name = res['name']
                            content = res['description']
                            if name.find(search_query) != -1:
                                count += 1
                                vals.update({count: {'name': res['name'],
                                                     'content': res['description'],
                                                     'post_date': parse(res['lastModifiedAt']).strftime('%A, %d. %B %Y'),
                                                     'external_post_link': res['_links']['self']['href'],
                                                     }})
                            elif content.find(search_query) != -1:
                                count += 1
                                vals.update({count: {'name': res['name'],
                                                     'content': res['description'],
                                                     'post_date': parse(res['lastModifiedAt']).strftime('%A, %d. %B %Y'),
                                                     'external_post_link': res['_links']['self']['href'],
                                                     }})
                    return request.render("website_ascaldera.blog_post_search", {
                        'data': vals,
                        'external_post_count': self.get_external_post_count(), })
                else:
                    blog_post = blog_post_pool.search(
                        ['|', '|',
                         ('content', 'ilike', search_query),
                         ('name', 'ilike', search_query),
                         ('subtitle', 'ilike', search_query)])
                    if blog_post:
                        values.update({'blog_post': blog_post})
                    else:
                        url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon'
                        res = requests.get(url)
                        result = 0
                        if(res):
                            result = res.json()
                        count = 0
                        vals = {}
                        if(result != 0):
                            for res in result['_embedded']['documents']:
                                name = res['name']
                                content = res['description']
                                if name.find(search_query) != -1:
                                    count += 1
                                    vals.update({count: {'name': res['name'],
                                                         'content': res['description'],
                                                         'post_date': parse(res['lastModifiedAt']).strftime('%A, %d. %B %Y'),
                                                         'external_post_link': res['_links']['self']['href'],
                                                         'fav_tags': self.fav_tags_get(),
                                                         }})
                                elif content.find(search_query) != -1:
                                    count += 1
                                    vals.update({count: {'name': res['name'],
                                                         'content': res['description'],
                                                         'post_date': parse(res['lastModifiedAt']).strftime('%A, %d. %B %Y'),
                                                         'external_post_link': res['_links']['self']['href'],
                                                         'fav_tags': self.fav_tags_get(),
                                                         }})
                        return request.render("website_ascaldera.blog_post_search", {
                            'data': vals,
                            'external_post_count': self.get_external_post_count(), })
            return request.render("website_ascaldera.blog_post_search", values)


    def _get_blog_post_list(self, type, subtype = False, page=1,_blog_post_per_page =8, **post):
        blog_subtypes = False

        BlogType = request.env['blog.post.type']
        BlogPost = request.env['blog.post']

        blog_types = {
            'News': {'blog_post_type': 'website_ascaldera.blog_post_type_news',
                     'view_id': 'website_ascaldera.blog_post_news', 'title': 'News'},
            'Articles': {'blog_post_type': 'website_ascaldera.blog_post_type_article',
                         'view_id': 'website_ascaldera.blog_post_article', 'title': 'Legislation'},
            'Legislation': {'blog_post_type': 'website_ascaldera.blog_post_type_legislation',
                            'view_id': 'website_ascaldera.blog_post_practice_slo'},
            'Judicial-Practice': {'blog_post_type': 'website_ascaldera.blog_post_type_judicial_practice',
                                  'view_id': 'website_ascaldera.blog_post_judicial_practice'},
        }
        if subtype and (type == 'Judicial-Practice' or type == 'Legislation'):
            blog_subtypes = {
                'practice_foreign_oversight': {'sub_category_main': 'foreign_practice',
                                               'view_id': 'website_ascaldera.blog_post_foreign_practice'},
                'judgement_EU': {'sub_category_main': 'EU_judgments',
                                 'view_id': 'website_ascaldera.blog_post_EU_court'},
                'judgements_escp': {'sub_category_main': 'escp_judgements',
                                    'view_id': 'website_ascaldera.blog_post_ESCP'},
                'judgements_foreign': {'sub_category_main': 'foreign_judgments',
                                       'view_id': 'website_ascaldera.blog_post_foreign_court'},
                'legislation_slo': {'sub_category_main': 'slovenian_legislation',
                                    'view_id': 'website_ascaldera.blog_post_slovenian_legislation'},
                'judgement_SLO': {'sub_category_main': 'SLO_judgments',
                                  'view_id': 'website_ascaldera.blog_post_judgement_SLO'},
                'legislation_foreign': {'sub_category_main': 'foreign_legislation',
                                        'view_id': 'website_ascaldera.blog_post_judgement_SLO'},
                'edpb_guidelines': {'sub_category_main': 'edpb_guidelines',
                                        'view_id': 'website_ascaldera.blog_post_edpb_guidelines'},
                'practice_slo':{'sub_category_main':'slo_practice','view_id':'website_ascaldera.website_ascaldera'}
            }

        domain = [
            ('website_published', '=', True),
            ('lang', '=', request.env.context.get('lang'))]
        view_id = False
        blog_type_id = request.env.ref(blog_types[type]['blog_post_type'])
        # blog_type_id = BlogType.browse(type_id)
        if not subtype:

            domain.append(('blog_post_type_id', '=', blog_type_id.id))
            view_id = blog_types[type]['view_id']
        else:
            domain.append(('sub_category_main', '=', blog_subtypes[subtype]['sub_category_main']))
            view_id = blog_subtypes[subtype]['view_id']

        total = len(BlogPost.sudo().search(domain))
        pager = request.website.pager(
            url='/blog',
            total=total,
            page=page,
            step=8,
        )
        posts = BlogPost.search(domain, offset=(page - 1) * _blog_post_per_page, limit=_blog_post_per_page)
        most_read_posts = BlogPost.search(domain, limit=4,order='visits,published_date desc')
        subtitle = False
        title = ""
        if blog_type_id and len(blog_type_id):
            title = blog_type_id.display_name
        if subtype:
            subtitle = dict(BlogPost._fields['sub_category_main']._description_selection(request.env)).get(blog_subtypes[subtype]['sub_category_main'])
            title = subtitle
        render_values = {
                        'page':page,
                        'type':type,
                         'subtype':subtype,
                         'subtitle': subtitle,
                         'blog_type': blog_type_id,
                         'pager': pager,
                         'posts': posts,
                         'most_read_posts': most_read_posts,
                         'fav_tags': self.fav_tags_get(),
                         'unfav_tags': self.unfav_tags_get(),
                         'external_post_count': self.get_external_post_count(),
                         'additional_title': title
                         }
        return render_values


    @http.route([
        '/blog/<type>',
        '/blog/<type>/<subtype>',
        '/blog/<type>/page/<int:page>',
        '/blog/<type>/<subtype>/page/<int:page>',
    ], type='http', auth="public", website=True)
    def blog_post_list(self, type, subtype = False, page=1, **post):
        render_values = self._get_blog_post_list(type,subtype,page)

        return request.render('website_ascaldera.blog_post_single', render_values)


    @http.route([
        '/blog/full/<type>',
        '/blog/full/<type>/<subtype>',
    ], type='http', auth="public", website=True)
    def full_blog_post_list(self, type, subtype=False, page=1, **post):
        render_values = self._get_blog_post_list(type, subtype, page, 100)

        return request.render('website_ascaldera.blog_post_single', render_values)

    @http.route('/scroll_paginator', type='json', auth='public',website=True)
    def scroll_paginator(self, type, subtype=False, page=1):
        render_values = self._get_blog_post_list(type, subtype, page)
        pager = render_values['pager']
        if pager['page_count'] - page < 0:
            return {'count': 0, 'data_grid': False,'page':page}
        else:
            response = request.env.ref('website_ascaldera.only_posts').render(render_values)
            return {'count': pager['page_count'] - page, 'data_grid': response,'page':page}


    @http.route([
        '/blog/Judicial-Practice/practice_slo_old',
    ], type='http', auth="public", website=True)
    def blog_post_legislation(self, **post):
        """Controller for Legislation  page."""
        url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon&projection=documentDetail'
        res = requests.get(url)
        result = 0
        if(res):
            result = res.json()
        vals = {}
        count = 0
        if(result != 0):
            for res in result['_embedded']['documents']:
                count += 1
                vals.update({count: {'name': res['name'],
                                     'content': BeautifulSoup(base64.b64decode(res['content'])).get_text(),
                                     'post_date': parse(res['lastModifiedAt']).strftime('%A, %d. %B %Y'),
                                     'external_post_link': res['_links']['self']['href'],
                                    }})

        return request.render("website_ascaldera.blog_post_legislation", {
            'data': vals,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(), })

    @http.route('/blog/legislation/content',
                type='http', auth="public", website=True)
    def display_legislation_content(self, **post):
        name = request.params.get('name')
        url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon&projection=documentDetail'
        res = requests.get(url)
        result = 0
        if(res):
            result = res.json()
        if(result != 0):
            for res in result['_embedded']['documents']:
                if res['name'] == name:
                    return request.render(
                        "website_ascaldera.legislation_post_content",
                        {'name': res['name'],
                         'content': base64.b64decode(res['content']),
                         'external_post_link': res['_links']['self']['href'],
                         'external_post_count': self.get_external_post_count(), })


    # END BLOG post type list
    @http.route([
        '/blog/Dpo',
    ], type='http', auth="public", website=True)
    def blog_post_dpo(self, **post):
        """Controller for DPO  page."""
        return request.render("website_ascaldera.blog_post_dpo", {
            'external_post_count': self.get_external_post_count(), })

    @http.route([
        '/blog/Hubapp',
    ], type='http', auth="public", website=True)
    def blog_post_hubapp(self, **post):
        """Controller for HUBAPP  page."""
        return request.render("website_ascaldera.blog_post_hubapp", {
            'external_post_count': self.get_external_post_count(), })