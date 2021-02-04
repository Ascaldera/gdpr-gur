# -*- coding: utf-8 -*-
#V1.3

import heapq
from urllib import parse
import requests
from dateutil.parser import parser
import pytz
import babel.dates
import itertools
from collections import OrderedDict
from operator import itemgetter
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
from odoo import http, models, fields, _
from odoo.tools import crop_image, topological_sort, html_escape, pycompat

BLOG_TYPES = {
    'News': {'blog_post_type': 'website_ascaldera.blog_post_type_news','title': 'News'},
    'Articles': {'blog_post_type': 'website_ascaldera.blog_post_type_article', 'title': 'Legislation'},
    'Legislation': {'blog_post_type': 'website_ascaldera.blog_post_type_legislation'},
    'Judicial-Practice': {'blog_post_type': 'website_ascaldera.blog_post_type_judicial_practice'},
}
BLOG_SUBTYPES = {
    'practice_foreign_oversight': {'sub_category_main': 'foreign_practice'},
    'judgement_EU': {'sub_category_main': 'EU_judgments'},
    'judgements_escp': {'sub_category_main': 'escp_judgements'},
    'judgements_foreign': {'sub_category_main': 'foreign_judgments',},
    'legislation_slo': {'sub_category_main': 'slovenian_legislation'},
    'judgement_SLO': {'sub_category_main': 'SLO_judgments'},
    'legislation_foreign': {'sub_category_main': 'foreign_legislation'},
    'edpb_guidelines': {'sub_category_main': 'edpb_guidelines'},
    'practice_slo': {'sub_category_main': 'slo_practice'},
    'publications_and_manuals': {'sub_category_main': 'publications_and_manuals'},
    'opinions': {'sub_category_main': 'opinions'},
    'other_IP_news': {'sub_category_main': 'other_IP_news'},
}


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
             ('lang', '=', request.env.context.get('lang'))], limit=3,order='visits desc,document_date desc')


        # Get max three article posts
        article_id = request.env.ref(
            'website_ascaldera.blog_post_type_article')

        most_read_article_post = blog_post.sudo().search(
            [('blog_post_type_id', '=', article_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))], order='visits desc, document_date desc',limit=3)
    
        # Get max three practice posts
        practice_id = request.env.ref(
            'website_ascaldera.blog_post_type_judicial_practice')

        most_read_practice_post = blog_post.sudo().search(
            [('blog_post_type_id', '=', practice_id.id),
             ('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))], order='visits desc,document_date desc', limit=3)
        grid_images_posts = blog_post.sudo().search(
            [('website_published', '=', True),
             ('lang', '=', request.env.context.get('lang'))],order='document_date desc', limit=7)

        check_lang_to_installed(request.env, request.website)
        
        return request.render("website_ascaldera.main_blog_post", {
            'most_read_news_post': most_read_news_post,
            'most_read_article_post': most_read_article_post,
            'most_read_practice_post': most_read_practice_post,
            'grid_images_posts': grid_images_posts,
            'fav_tags': fav_tags,
            'unfav_tags': unfav_tags,
        })


class WebsiteBlog(WebsiteBlog):
    """Controller WebsiteBlog."""

    def new_blog_nav_list(self, dom=None):

        groups = request.env['blog.post']._read_group_raw(
            dom,
            ['name', 'document_date'],
            groupby=["document_date"], orderby="document_date desc")
        for group in groups:
            (r, label) = group['document_date']


            start, end = r.split('/')
            start = pytz.UTC.localize(fields.Datetime.from_string(start))
            tzinfo = pytz.timezone(request.context.get('tz', 'utc') or 'utc')
            locale = request.context.get('lang') or 'en_US'
            str_year = babel.dates.format_datetime(start, format='YYYY', tzinfo=tzinfo, locale=locale)
            label = str_year
            start = str_year +'-01-01 00:00:00'
            end = str_year + '-12-31 23:59:59'

            group['post_date'] = label
            group['date_begin'] = start
            group['date_end'] = end

            start = pytz.UTC.localize(fields.Datetime.from_string(start))


            group['month'] = babel.dates.format_datetime(start, format='MMMM', tzinfo=tzinfo, locale=locale)
            group['year'] = babel.dates.format_datetime(start, format='YYYY', tzinfo=tzinfo, locale=locale)


        ordered_dist_years = OrderedDict((year, [m for m in months]) for year, months in itertools.groupby(groups, lambda g: g['year']))
        dist_years = {}
        for year in ordered_dist_years:
            if not year in dist_years:
                dist_years[year] = ordered_dist_years[year][0]
        return dist_years

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

    @http.route([ '/blog_orig',], type='http', auth="public", website=True)
    def blogs(self, **post):
        return self.blog()

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

    def _get_blog_post_tag_list(self, tag_ids=False,  page=1, order='document_date desc',types_list = False, year_list=False, _blog_post_per_page=8, ):
        BlogPost = request.env['blog.post']
        BlogType = request.env['blog.post.type']
        domain = [('tag_ids', 'in', tag_ids.ids)]
        domain.append(('website_published', '=', True))
        domain.append(('lang', '=', request.env.context.get('lang')))
        all_posts = BlogPost.sudo().search(domain)

        # Types
        BlogType = request.env['blog.post.type']
        types = BlogType.sudo().search([ ('blog_post_ids', 'in', all_posts.ids)])
        if not types_list:
            types_list = request.httprequest.args.getlist('type')
        types_set = {int(v) for v in types_list}
        type_ids = []
        if types_set and len(types_set):

            # for x in range(0, len(type_set) - 1):
            #     domain += ['|']
            # attrib = None
            type_ids = []
            for value in types_set:
                type_ids.append(value)
            domain += [('blog_post_type_id', 'in', type_ids)]

        # YEARS
        # NEW CODE
        if not year_list:
            year_list = request.httprequest.args.getlist('year')
        year_set = {int(v) for v in year_list}

        years = self.new_blog_nav_list(domain)
        pre_sub_year_domain = []
        year_posts_ids = []
        pre_post_domain = domain
        for year_item in year_set:
            sub_year_domain = []
            if year_item and str(year_item) in years:
                sub_year_domain = []
                sub_year_domain.append(('document_date', '>=', years[str(year_item)]['date_begin']))
                sub_year_domain.append(('document_date', '<', years[str(year_item)]['date_end']))
                year_posts = BlogPost.sudo().search(pre_post_domain + sub_year_domain)
                if year_posts and len(year_posts):
                    year_posts_ids += (year_posts.ids)
        if year_posts_ids and len(year_posts_ids):
            domain.append(('id', 'in', year_posts_ids))

        all_posts = BlogPost.sudo().search(domain)
        posts = BlogPost.sudo().search(domain, offset=(page - 1) * _blog_post_per_page, limit=_blog_post_per_page,order=order)
        total = len(all_posts)
        pager = request.website.pager(
            url='/blog',
            total=total,
            page=page,
            step=_blog_post_per_page,
        )
        title = _("Oznaka:")
        for tag in tag_ids:
            title += " "+tag.name
        values = {
            'tag_ids': tag_ids,
            'list_tag_ids':tag_ids.ids,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'posts': posts,
            'pager': pager,
            'total': total,
            'page': page,
            'count': pager['page_count'] - page,
            'order':order,
            'types':types,
            'types_list':types_list,
            'types_set':types_set,
            'additional_title': title,
            'years':years,
            'year_set':year_set

        }
        return values
    @http.route([
        '''/blog/tag/<model("blog.tag"):tag_id>''',
    ], type='http', auth="public", website=True)
    def blog_tag(self, tag_id, page=1,order='document_date desc', **post):
        """Controller to fetch blog based on tags."""
        values = self._get_blog_post_tag_list(tag_id, page,order)
        return request.render("website_ascaldera.blog_post_tags", values )

    @http.route('/tag_js_call', type='json', auth='public', website=True)
    def tag_js_call(self, tag_ids,page = 1,order='document_date desc'):
        query_def = parse.parse_qs(parse.urlparse(request.httprequest.referrer).query)
        order = False
        type_list = False
        year_list = False
        if 'order' in query_def:
            order = query_def['order'][0]
        if 'type' in query_def:
            type_list = query_def['type_list']
        if 'year' in query_def:
            year_list = query_def['year']

        tag_ids = request.env['blog.tag'].sudo().browse(tag_ids)
        render_values = self._get_blog_post_tag_list(tag_ids, page, order,type_list, year_list)
        pager = render_values['pager']
        if pager['page_count'] - page < 0:
            return {'count': 0, 'data_grid': False, 'page': page}
        else:
            response = request.env.ref('website_ascaldera.only_posts').render(render_values)
            return {'count': pager['page_count'] - page, 'data_grid': response, 'page': page, 'order':order}


    def _get_blog_post_search_list(self, search_query='',blog_post_type = False,page = 1,order='document_date desc',types_list=False, tags_list=False, year_list = False,_blog_post_per_page =8,):
        values = {}
        BlogPost = request.env['blog.post']
        values.update({'query': search_query})
        if page == None or page == '':
            page = 1
        else:
            page = int(page)
        domain = ['|', '|', ('content', 'ilike', search_query),
                  ('name', 'ilike', search_query),
                  ('subtitle', 'ilike', search_query)]

        blog_post_pool = request.env['blog.post'].sudo()

        if blog_post_type  :
            domain.append(('blog_post_type_id', '=', blog_post_type.id))
            post_type = str(blog_post_type.id)
        else:
            post_type = 'All'
        domain.append(('website_published', '=', True))
        domain.append(('lang', '=', request.env.context.get('lang')))
        all_posts = BlogPost.sudo().search(domain)

        # Types
        BlogType = request.env['blog.post.type']
        if not types_list:
            types_list = request.httprequest.args.getlist('type')
        types_set = {int(v) for v in types_list}
        type_ids = []
        type_domain = []
        if types_set and len(types_set):

            # for x in range(0, len(type_set) - 1):
            #     domain += ['|']
            # attrib = None
            type_ids = []
            for value in types_set:
                type_ids.append(value)
            type_domain += [('blog_post_type_id', 'in', type_ids)]



        # TAGS
        BlogTag = request.env['blog.tag']
        if not tags_list:
            tags_list = request.httprequest.args.getlist('tag')
        tags_set = {int(v) for v in tags_list}
        tag_domain = []
        if tags_set and len(tags_set):

            for x in range(0, len(tags_set) - 1):
                tag_domain += ['|']
            attrib = None
            tag_ids = []
            for value in tags_set:
                attrib = value
                tag_ids.append(value)
                tag_domain += [('tag_ids', 'in', value)]
        types = False
        tags = False

        # YEARS
        # NEW CODE
        if not year_list:
            year_list = request.httprequest.args.getlist('year')
        year_set = {int(v) for v in year_list}

        years = self.new_blog_nav_list(domain)
        pre_sub_year_domain = []
        year_posts_ids = []
        pre_post_domain = domain
        for year_item in year_set:
            sub_year_domain = []
            if year_item and str(year_item) in years:
                sub_year_domain = []
                sub_year_domain.append(('document_date', '>=', years[str(year_item)]['date_begin']))
                sub_year_domain.append(('document_date', '<', years[str(year_item)]['date_end']))
                year_posts = BlogPost.sudo().search(pre_post_domain + sub_year_domain)
                if year_posts and len(year_posts):
                    year_posts_ids += (year_posts.ids)
        if year_posts_ids and len(year_posts_ids):
            domain.append(('id', 'in', year_posts_ids))

        values.update({'years': years,'year_set': year_set})

        #NONE
        if not(types_list and len(types_list)) and not(tags_list and len(tags_list)):
            types = BlogType.sudo().search([('blog_post_ids', 'in', all_posts.ids)])
            tags = BlogTag.sudo().search([('post_ids', '!=', False), ('post_ids', 'in', all_posts.ids)])
        #TAG LIST
        elif not(types_list and len(types_list)) and (tags_list and len(tags_list)) :
            tags = BlogTag.sudo().search([('post_ids', '!=', False), ('post_ids', 'in', all_posts.ids)])
            domain += tag_domain
            all_posts = BlogPost.sudo().search(domain)
            types = BlogType.sudo().search([('blog_post_ids', 'in', all_posts.ids)])
        #TYPE LIST
        elif types_list and len(types_list) and not(tags_list and len(tags_list)):
            types = BlogType.sudo().search([('blog_post_ids', 'in', all_posts.ids)])
            domain += type_domain
            all_posts = BlogPost.sudo().search(domain)
            tags = BlogTag.sudo().search([('post_ids', '!=', False), ('post_ids', 'in', all_posts.ids)])

        #TYPE LIST and TAG LIST
        elif types_list and len(types_list) and tags_list and len(tags_list):
            types = BlogType.sudo().search([('blog_post_ids', 'in', all_posts.ids)])
            domain += type_domain
            all_posts = BlogPost.sudo().search(domain)
            domain += tag_domain
            tags = BlogTag.sudo().search([('post_ids', '!=', False), ('post_ids', 'in', all_posts.ids)])

        all_posts = BlogPost.sudo().search(domain)
        values.update({'types': types, 'types_list': types_list, 'types_set': types_set})
        values.update({'tags': tags, 'tags_list': tags_list, 'tags_set': tags_set})

        posts = blog_post_pool.search(domain, order=order, offset=(page - 1) * _blog_post_per_page, limit=_blog_post_per_page)
        total = len(all_posts)
        pager = request.website.pager(
            url='/blog',
            total=total,
            page=page,
            step=8,
        )
        title = _("Search: ")
        if search_query and search_query != "":
            title += search_query
        values.update({'query': search_query, 'page': page, 'pager': pager, 'post_type': post_type, 'total': total,'order':order,'additional_title': title})
        if posts:
            values.update({'posts': posts, })
        return values

    @http.route([
        '/blog/search',
    ], type='http', auth="public", website=True)
    def blog_post_search(self, _blog_post_per_page =8,order = 'document_date desc',**post):
        if post:
            search_query = post.get('query')

            post_type = post.get('post_type')
            blog_post_type = False
            if post_type != None and post_type != 'All':
                try:
                    blog_post_type = request.env['blog.post.type'].browse(int(post_type))
                except:
                    blog_post_type = False

            #page = post.get('page')
            page = 1

            values =self._get_blog_post_search_list(search_query,blog_post_type,page,order)

            return request.render("website_ascaldera.blog_post_search", values)

    @http.route('/search_js_call', type='json', auth='public', website=True)
    def search_js_call(self, search_query='',blog_post_type = False,page = 1,order = 'document_date desc'):
        query_def = parse.parse_qs(parse.urlparse(request.httprequest.referrer).query)
        order = False
        tags_list = False
        year_list = False
        type_list = False
        if 'order' in query_def:
            order = query_def['order'][0]
        if 'tag' in query_def:
            tags_list = query_def['tag']
        if 'year' in query_def:
            year_list = query_def['year']
        if 'type' in query_def:
            type_list = query_def['type']
        if blog_post_type != 'All':
            blog_post_type = request.env['blog.post.type'].browse(int(blog_post_type))
        else:
            blog_post_type = False
        render_values = self._get_blog_post_search_list(search_query,blog_post_type, page, order,type_list, tags_list,year_list)
        pager = render_values['pager']
        if pager['page_count'] - page < 0:
            return {'count': 0, 'data_grid': False, 'page': page}
        else:
            response = request.env.ref('website_ascaldera.only_posts').render(render_values)
            return {'count': pager['page_count'] - page, 'data_grid': response, 'page': page,'order':order}

    def _get_blog_post_list(self, type, subtype = False, page=1,order='document_date desc',tags_list = False, year_list = False,_blog_post_per_page =8, **post):

        BlogType = request.env['blog.post.type']
        BlogPost = request.env['blog.post']

        domain = [
            ('website_published', '=', True),
            ('lang', '=', request.env.context.get('lang'))]

        view_id = False
        blog_type_id = request.env.ref(BLOG_TYPES[type]['blog_post_type'])
        if not subtype:

            domain.append(('blog_post_type_id', '=', blog_type_id.id))
        else:
            domain.append(('sub_category_main', '=', BLOG_SUBTYPES[subtype]['sub_category_main']))



        all_posts = BlogPost.sudo().search(domain)

        most_read_posts = BlogPost.search(domain, limit=4,order='visits desc,document_date desc')
        # TAGS
        BlogTag = request.env['blog.tag']
        tags = BlogTag.sudo().search([('post_ids', '!=', False), ('post_ids', 'in', all_posts.ids)])
        if not tags_list:
            tags_list = request.httprequest.args.getlist('tag')
        tags_set = {int(v) for v in tags_list}
        if tags_set and len(tags_set):

            for x in range(0, len(tags_set)-1):
                domain += ['|']
            attrib = None
            tag_ids = []
            for value in tags_set:
                attrib = value
                tag_ids.append(value)
                domain += [('tag_ids', 'in', value)]

        # YEARS
        # NEW CODE
        if not year_list:
            year_list = request.httprequest.args.getlist('year')
        year_set = {int(v) for v in year_list}

        years = self.new_blog_nav_list(domain)
        pre_sub_year_domain = []
        year_posts_ids = []
        pre_post_domain = domain
        for year_item in year_set:
            sub_year_domain = []
            if year_item and str(year_item) in years:
                sub_year_domain = []
                sub_year_domain.append(('document_date', '>=', years[str(year_item)]['date_begin']))
                sub_year_domain.append(('document_date', '<', years[str(year_item)]['date_end']))
                year_posts = BlogPost.sudo().search(pre_post_domain + sub_year_domain)
                if year_posts and len(year_posts):
                    year_posts_ids += (year_posts.ids)
        if year_posts_ids and len(year_posts_ids):
            domain.append(('id', 'in', year_posts_ids))


        all_posts = BlogPost.sudo().search(domain)
        posts = BlogPost.search(domain, offset=(page - 1) * _blog_post_per_page, order=order, limit=_blog_post_per_page)
        total = len(all_posts)
        pager = request.website.pager(
            url='/blog',
            total=total,
            page=page,
            step=8,
        )
        subtitle = False
        title = ""
        if blog_type_id and len(blog_type_id):
            title = blog_type_id.display_name
        if subtype:
            subtitle = dict(BlogPost._fields['sub_category_main']._description_selection(request.env)).get(BLOG_SUBTYPES[subtype]['sub_category_main'])

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
                         'additional_title': title,
                         'order':order,
                         'tags':tags,
                         'tags_list':tags_list,
                          'tags_set': tags_set,
                         'years': years,
                        'year_set': year_set,
                         }
        return render_values


    @http.route([
        '/blog/<type>',
        '/blog/<type>/<subtype>',
        '/blog/<type>/page/<int:page>',
        '/blog/<type>/<subtype>/page/<int:page>',
    ], type='http', auth="public", website=True)
    def blog_post_list(self, type, subtype = False, page=1,order = False,year=False, **post):
        if order == False and subtype and subtype == 'legislation_foreign':
            order = 'name asc'
        elif order == False:
            order = 'document_date desc'
        render_values = self._get_blog_post_list(type,subtype,page,order)

        return request.render('website_ascaldera.blog_post_single', render_values)




    @http.route('/scroll_paginator', type='json', auth='public',website=True)
    def scroll_paginator(self, type, subtype=False, page=1,order='document_date desc'):
        query_def = parse.parse_qs(parse.urlparse(request.httprequest.referrer).query)
        order = False
        tags_list = False
        year_list = False
        if 'order' in query_def:
            order = query_def['order'][0]
        if 'tag' in query_def:
            tags_list = query_def['tag']
        if 'year' in query_def:
            year_list = query_def['year']

        render_values = self._get_blog_post_list(type, subtype, page, order, tags_list, year_list)

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
                                     'post_date': parser(res['lastModifiedAt']).strftime('%A, %d. %B %Y'),
                                     'external_post_link': res['_links']['self']['href'],
                                    }})

        return request.render("website_ascaldera.blog_post_legislation", {
            'data': vals,
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
             })


    # END BLOG post type list
    @http.route([
        '/blog/Dpo',
    ], type='http', auth="public", website=True)
    def blog_post_dpo(self, **post):
        """Controller for DPO  page."""
        
        return request.redirect('https://www.dataprotection-officer.com/')
        """
        return request.render("website_ascaldera.blog_post_dpo", {
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
        })
        """

    @http.route([
        '/blog/Hubapp',
    ], type='http', auth="public", website=True)
    def blog_post_hubapp(self, **post):
        """Controller for HUBAPP  page."""
        
        return request.redirect('http://staging.app.gdpr.ascaldera.com/#/login')
        """
        return request.render("website_ascaldera.blog_post_hubapp", {
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
        })
        """

    @http.route([
        '/blog/Newsletter',
    ], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def newsletter(self, **post):
        """Controller for Newsletter  page."""

        created = False
        email = post['email']
        contacts_model = request.env['res.partner']
        contact = contacts_model.sudo().search([('email','=', email)])

        if not contact:
            contacts_model.sudo().create({'name': email, 'email': email})
            created = True
        else:
            created = False 

        return request.render("website_ascaldera.blog_post_newsletter", {
            'fav_tags': self.fav_tags_get(),
            'unfav_tags': self.unfav_tags_get(),
            'created': created,
            'contact': contact,
        })