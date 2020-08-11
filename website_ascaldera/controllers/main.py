# -*- coding: utf-8 -*-

import heapq

import requests
from dateutil.parser import parse

from odoo import http
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.http import request
import base64
from bs4 import BeautifulSoup
import logging

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


class Website(Website):
    """Controller Website."""

    def get_external_post_count(self):
        url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon'
        res = requests.get(url)
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
        news_posts_visits = [p.visits for p in blog_post.sudo().search(
            [('blog_post_type_id', '=', news_id.id),
             ('lang', '=', request.env.context.get('lang'))])]
        news_highest_visits = heapq.nlargest(3, news_posts_visits)
        most_read_news_post = blog_post.sudo().search(
            [('blog_post_type_id', '=', news_id.id),
             ('website_published', '=', True),
             ('visits', 'in', news_highest_visits),
             ('lang', '=', request.env.context.get('lang'))], limit=3)
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
             ('lang', '=', request.env.context.get('lang')),
             ('visits', 'in', article_highest_visits)], limit=3)
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
            'most_read_news_post': most_read_news_post,
            'most_read_article_post': most_read_article_post,
            'most_read_practice_post': most_read_practice_post,
            'fav_tags': fav_tags,
            'unfav_tags': unfav_tags,
            'external_post_count': self.get_external_post_count(),
        })


class WebsiteBlog(WebsiteBlog):
    """Controller WebsiteBlog."""

    def get_external_post_count(self):
        url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon'
        res = requests.get(url)
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
        return request.render("website_ascaldera.blog_post_content", {
            'blog': blog,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'blog_post': blog_post,
            'main_object': blog_post,
            'external_post_count': self.get_external_post_count(),
        })

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
            blog_post_pool = request.env['blog.post'].sudo()
            if post_type:
                if post_type in ['News', 'Articles', 'Judicial-Practice']:
                    posts = blog_post_pool.search(
                        ['|', '|', ('content', 'ilike', search_query),
                         ('name', 'ilike', search_query),
                         ('subtitle', 'ilike', search_query)])
                    blog_post = posts.filtered(
                        lambda l: l.blog_post_type_id.name == post_type and l.website_published == True)
                    if blog_post:
                        values.update({'blog_post': blog_post})
                elif post_type == 'Legislation':
                    url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon'
                    res = requests.get(url)
                    result = res.json()
                    count = 0
                    vals = {}
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
                        result = res.json()
                        count = 0
                        vals = {}
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

    @http.route([
        '/blog/News',
    ], type='http', auth="public", website=True)
    def blog_post_news(self, **post):
        """Controller for News page."""
        news_id = request.env.ref(
            'website_ascaldera.blog_post_type_news')
        news_ids = request.env['blog.post'].sudo().search(
            [('blog_post_type_id', '=', news_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])

        return request.render("website_ascaldera.blog_post_news", {
            'blog_type': news_ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(),
        })

    @http.route([
        '/blog/Articles',
    ], type='http', auth="public", website=True)
    def blog_post_articles(self, **post):
        """Controller for Article page."""
        article_id = request.env.ref(
            'website_ascaldera.blog_post_type_article')
        article_ids = request.env['blog.post'].sudo().search(
            [('blog_post_type_id', '=', article_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])

        return request.render("website_ascaldera.blog_post_article", {
            'blog_type': article_ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(), })

    #------------------------------------------------------------------------------------------------------
    
    @http.route(['/blog/Legislation',],type='http',auth="public",website=True)
    def blog_post_articles_1(self,**post):
        """Controller for Article page."""
        article_id = request.env.ref(
            'website_ascaldera.blog_post_type_legislation')
        article_ids = request.env['blog.post'].sudo().search(
            [('blog_post_type_id', '=', article_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])

        return request.render("website_ascaldera.blog_post_practice_slo", {
            'blog_type': article_ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(), })
    
    #2
    
    @http.route(['/blog/Judicial-Practice/practice_foreign_oversight',], type='http', auth="public", website=True)
    def blog_post_articles_2(self, **post):
        article_name="foreign_practice"        
        article_ids = request.env['blog.post'].sudo().search([('sub_category_main', '=', article_name),('website_published', '=', True),('lang', '=', request.env.context.get('lang'))])
        return request.render("website_ascaldera.blog_post_foreign_practice", {'blog_type': article_ids,'fav_tags': self.fav_tags_get(),'external_post_count': self.get_external_post_count(), })
    
    #3
    
    @http.route([
        '/blog/Judicial-Practice/judgement_EU',
    ], type='http', auth="public", website=True)
    def blog_post_articles_3(self, **post):
        """Controller for Article page."""
        
        article_name="EU_judgments"        
        
        article_ids = request.env['blog.post'].sudo().search(
            [('sub_category_main', '=', article_name),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])
        return request.render("website_ascaldera.blog_post_EU_court", {
            'blog_type': article_ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(), })
    
    #4
    
    @http.route([
        '/blog/Judicial-Practice/judgements_escp',
    ], type='http', auth="public", website=True)
    def blog_post_articles_4(self, **post):
        """Controller for Article page."""
        
        article_name="escp_judgements"        
        
        article_ids = request.env['blog.post'].sudo().search(
            [('sub_category_main', '=', article_name),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])
        return request.render("website_ascaldera.blog_post_ESCP", {
            'blog_type': article_ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(), })
    
    #5
    
    @http.route([
        '/blog/Judicial-Practice/judgements_foreign',
    ], type='http', auth="public", website=True)
    def blog_post_articles_5(self, **post):
        """Controller for Article page."""
        
        article_name="foreign_judgments"        
        
        article_ids = request.env['blog.post'].sudo().search(
            [('sub_category_main', '=', article_name),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])
        return request.render("website_ascaldera.blog_post_foreign_court", {
            'blog_type': article_ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(), })
    
    #6
    
    @http.route([
        '/blog/Legislation/legislation_foreign',
    ], type='http', auth="public", website=True)
    def blog_post_articles_6(self, **post):
        """Controller for Article page."""
        
        article_name="foreign_legislation"        
        
        article_ids = request.env['blog.post'].sudo().search(
            [('sub_category_main', '=', article_name),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])
        return request.render("website_ascaldera.blog_post_foreign_legislation", {
            'blog_type': article_ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(), })
    
    #7
    
    @http.route([
        '/blog/Legislation/legislation_slo',
    ], type='http', auth="public", website=True)
    def blog_post_articles_7(self, **post):
        """Controller for Article page."""
        
        article_name="slovenian_legislation"        
        
        article_ids = request.env['blog.post'].sudo().search(
            [('sub_category_main', '=', article_name),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])
        return request.render("website_ascaldera.blog_post_slovenian_legislation", {
            'blog_type': article_ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(), })
    #8
    @http.route([
        '/blog/Judicial-Practice/judgement_SLO',
    ], type='http', auth="public", website=True)
    def blog_post_articles_8(self, **post):
        """Controller for Article page."""
        
        article_name="SLO_judgments"        
        
        article_ids = request.env['blog.post'].sudo().search(
            [('sub_category_main', '=', article_name),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])
        return request.render("website_ascaldera.blog_post_judgement_SLO", {
            'blog_type': article_ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'external_post_count': self.get_external_post_count(), })
    
    #------------------------------------------------------------------------------------------------------
    
    @http.route([
        '/blog/Judicial-Practice',
    ], type='http', auth="public", website=True)
    def blog_post_judicial_practice(self, **post):
        """Controller for Judicial Practice  page."""
        judicial_practice_id = request.env.ref(
            'website_ascaldera.blog_post_type_judicial_practice')
        judicial_practice_ids = request.env['blog.post'].sudo().search(
            [('blog_post_type_id', '=', judicial_practice_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))])

        return request.render(
            "website_ascaldera.blog_post_judicial_practice", {
                'blog_type': judicial_practice_ids,
                'fav_tags': self.fav_tags_get(),
                'external_post_count': self.get_external_post_count(), })

    @http.route([
        '/blog/Judicial-Practice/practice_slo',
    ], type='http', auth="public", website=True)
    def blog_post_legislation(self, **post):
        """Controller for Legislation  page."""
        url = 'http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon&projection=documentDetail'
        res = requests.get(url)
        result = res.json()
        vals = {}
        count = 0
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
        result = res.json()
        for res in result['_embedded']['documents']:
            if res['name'] == name:
                return request.render(
                    "website_ascaldera.legislation_post_content",
                    {'name': res['name'],
                     'content': base64.b64decode(res['content']),
                     'external_post_link': res['_links']['self']['href'],
                     'external_post_count': self.get_external_post_count(), })

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