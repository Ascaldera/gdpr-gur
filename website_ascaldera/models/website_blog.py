# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from odoo import api, fields, models
from datetime import date,datetime

import requests
import base64
from bs4 import BeautifulSoup
from dateutil.parser import parse
from odoo.modules.module import get_module_resource

@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()


class BlogBlog(models.Model):
    _inherit = "blog.blog"

    def sync_api_blog(self,language=False,url=False,author_id=False,blog_id=False,blog_type_id=False,subtype_selection=False):
        blog_post_object = self.env['blog.post']
        res = requests.get(url)
        result = 0
        if (res):
            result = res.json()
        records = []
        count = 0
        #/website_ascaldera/static/src/img/IP_logo.jpg
        img_path = get_module_resource('website_ascaldera', 'static/src/img', 'informacijski-pooblascenec.jpg')
        img_base = False
        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
                img_base = base64.b64encode(image)
        if (result != 0):
            for res in result['_embedded']['documents']:
                count += 1
                values= {
                                    'name': res['name'].replace('τ','š'),
                                    'blog_id': blog_id,
                                    'blog_post_type_id': blog_type_id.id,
                                    'sub_category_main':subtype_selection,
                                    'content': str(BeautifulSoup(base64.b64decode(res['content']), features="lxml")),
                                    #'content': BeautifulSoup(base64.b64decode(res['content']), features="lxml").get_text(),
                                    'published_date': parse(res['lastModifiedAt']).strftime('%Y-%m-%d %H:%M:%S'),
                                    'document_date': parse(res['createdAt']).strftime('%Y-%m-%d %H:%M:%S'),
                                    'website_published':True,
                                    'api_id': res['id'],
                                    'api_sync': True,
                                    'api_link': res['_links']['self']['href'],
                                    'api_last_modified_at':parse(res['lastModifiedAt']).strftime('%Y-%m-%d %H:%M:%S'),
                                    'lang':language,
                                    'author_id':author_id,
                                    'write_uid':author_id,

                                     }

                if img_base:
                    values['blog_post_cover_image'] = img_base
                records.append(values)

        all_blog_post = []
        for record in records:
            existing_blog_post = blog_post_object.search([('lang','=',language),('api_sync','=',True),('api_id','=',record['api_id'])],limit=1)
            if existing_blog_post and len(existing_blog_post):
                all_blog_post.append(existing_blog_post.id)
                if record['api_last_modified_at'] > str(existing_blog_post.api_last_modified_at):
                    existing_blog_post.write(record)
                else:
                    existing_blog_post.write(record)


            else:
                blot_post_id = blog_post_object.create(record)
                blot_post_id.sub_category_main = subtype_selection
                all_blog_post.append(blot_post_id.id)
        all_posts = blog_post_object.search(
            [('lang', '=', language), ('api_sync', '=', True), ('id', 'in', all_blog_post)])
        all_posts.write( {'website_published': True})
        for post in all_posts:
            post.published_date = post.api_last_modified_at



        blog_post_object.search([('lang', '=', language), ('api_sync', '=', True), ('id','not in', all_blog_post)]).write({'website_published':False})
        blog_post_object.search([('visits', '=', False)]).write({'visits': 0})


    def sync_api_slo_blog(self):
        blog_type_id = self.env.ref('website_ascaldera.blog_post_type_slo_ip')
        self.sync_api_blog('sl_SI','http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon&projection=documentDetail',10,5,blog_type_id,'decisions_ip')



class BlogPostType(models.Model):
    _name = "blog.post.type"

    name = fields.Char(string='Name', translate=True)
    blog_post_ids = fields.One2many('blog.post', 'blog_post_type_id', string='Blog Posts')

class BlogTag(models.Model):
    _inherit = "blog.tag"
    _order = "name"

class BlogPost(models.Model):
    _inherit = "blog.post"
    _order = 'document_date desc'
    visits = fields.Integer('No of Views', copy=False,default=0)
    subscription=fields.Selection(string="Subscription", 
                                    selection=[('private','Private'),('public','Public')], default='private', required=True)

    blog_post_type_id = fields.Many2one('blog.post.type',
                                        string='Blog Post Type',
                                        help='Select blog post type')
    blog_post_cover_image = fields.Binary(string='Cover Image',
                                          attachment=True)
    cover_image_filename = fields.Char(string='Cover Image Filename')
    post_listing_content = fields.Text(
        string='Listing Content', help='Add content for blog post listing')
    post_listing_text_content = fields.Text(compute="_get_text_content")
    external_post_link = fields.Char(string='Link')
    lang = fields.Selection(_lang_get, string='Language',
                            default=lambda self: self.env.lang,
                            help="Select language for blog post content",
                            required=True)
    document_date = fields.Datetime(string="Document Date")
    api_sync = fields.Boolean(string="Api sync",default=False, readonly=True)
    api_id = fields.Integer(string="Api Id", readonly=True, index=True)
    api_link = fields.Char(string="Api link",readonly=True)
    api_last_modified_at = fields.Datetime('Api last modified at')


    def get_date(self):
        for r in self:
            if r.document_date==False and r.create_date:
                r.document_date=r.create_date

    @api.onchange('blog_post_type_id')
    def _show_sub_category(self):
        show_type_ids = [self.env.ref('website_ascaldera.blog_post_type_judicial_practice').id,self.env.ref('website_ascaldera.blog_post_type_legislation').id]
        for record in self:
            if record.blog_post_type_id and len(record.blog_post_type_id) and record.blog_post_type_id.id in show_type_ids:
                record.show_subcategory = True
            else:
                record.show_subcategory = False
    #ADDITION
    #------------------------------------------------------------------------------------------------------------------------------
    
    save_name=fields.Char(string='Saved name')
    
    sub_category_main=fields.Selection(string="Subcategory", 
                                       selection=[('articles_proffesional','Proffesional Articles'), ('publications_and_manuals','Useful Publications and Manuals'),('SLO_judgments','Judgments of the Slovenian Court'),('foreign_practice','The practice of foreign oversight bodies'),('EU_judgments','Judgments of the European Court of Justice'),('escp_judgements','ECHR judgments'),('foreign_judgments','Judgments of foreign courts'), ('edpb_guidelines', 'EDPB guidelines and opinions'), ('decisions_ip', 'Decisions SLO IP'), ('opinions','Opinions'), ('other_IP_news','Other IP News'), ('foreign_legislation','Foreign legislation'),('slovenian_legislation','Slovenian legislation')])
    sub_category_judicialpractice=fields.Selection(string="Subcategory", 
                                    selection=[('SLO_judgments','Judgments of the Slovenian Court'),('EU_judgments','Judgments of the European Court of Justice'),('escp_judgements','ECHR judgments'),('foreign_judgments','Judgments of foreign courts'),('foreign_practice','The practice of foreign oversight bodies'), ('edpb_guidelines', 'EDPB guidelines and opinions')])
    sub_category_legislation=fields.Selection(string="Subcategory", 
                                    selection=[('foreign_legislation','Foreign legislation'),('slovenian_legislation','Slovenian legislation')])
    sub_category_IP=fields.Selection(string="Subcategory", 
                                    selection=[('decisions_ip', 'Decisions SLO IP'), ('opinions','Opinions IP'), ('other_IP_news','Other IP News')])
    sub_category_articles=fields.Selection(string="Subcategory", 
                                    selection=[('articles_proffesional','Proffesional Articles'),('publications_and_manuals','Useful Publications and Manuals')])
    show_subcategory = fields.Boolean('Show sub category',default=_show_sub_category,compute=_show_sub_category)
    
    #Function to populate the main subcategory selection field or erase data from that field if something else was selected
    #Function to save the name of the blog_post_type_id field
    #------------------------------------------------------------------------------------------------------------------------------
    
    @api.onchange('blog_post_type_id','sub_category_judicialpractice','sub_category_legislation', 'sub_category_IP','sub_category_articles')
    def spremeni_podkategorijo(self):
        if self.blog_post_type_id.name=="Judicial-Practice" or self.blog_post_type_id.name=="Pravna praksa":
            self.sub_category_legislation=[]
            self.sub_category_IP=[]
            self.sub_category_articles=[]
            if self.sub_category_judicialpractice == False:
                self.sub_category_main=[]
        elif self.blog_post_type_id.name=="Legislation" or self.blog_post_type_id.name=="Zakonodaja":
            self.sub_category_judicialpractice=[]
            self.sub_category_IP=[]
            self.sub_category_articles=[]
            if self.sub_category_legislation==False:
                self.sub_category_main=[]
        elif self.blog_post_type_id.name=="Articles" or self.blog_post_type_id.name=="Strokovni članki":
            self.sub_category_judicialpractice=[]
            self.sub_category_IP=[]
            self.sub_category_legislation=[]
            if self.sub_category_articles==False:
                self.sub_category_main=[]
        elif self.blog_post_type_id.name=="SLO-Information-Commissioners-Practice" or self.blog_post_type_id.name=="Odločitve SLO IP":
            self.sub_category_judicialpractice=[]
            self.sub_category_legislation=[]
            self.sub_category_articles=[]
            if self.sub_category_IP==False:
                self.sub_category_main=[]
        else:
            self.sub_category_judicialpractice=[]
            self.sub_category_legislation=[]
            self.sub_category_articles=[]
            self.sub_category_IP=[]
            self.sub_category_main=[]
        if self.sub_category_judicialpractice:
            self.sub_category_main=self.sub_category_judicialpractice
        if self.sub_category_legislation:
            self.sub_category_main=self.sub_category_legislation
        if self.sub_category_articles:
            self.sub_category_main=self.sub_category_articles
        if self.sub_category_IP:
            self.sub_category_main=self.sub_category_IP
        if self.blog_post_type_id:
            self.save_name=self.blog_post_type_id
        else:
            self.save_name=""
    
    #------------------------------------------------------------------------------------------------------------------------------




    @api.multi
    def _get_text_content(self):
        for post in self:
            soup = False
            if post.post_listing_content and post.post_listing_content != "":
                soup = BeautifulSoup(post.post_listing_content)
            else:
                soup = BeautifulSoup(post.content)
            if soup:
                text = soup.get_text()
                if len(text) < 260:
                    post.post_listing_text_content = text
                else:
                    new_text = text[0:260]
                    sub_end = new_text.rfind(' ')
                    new_text = new_text[0:sub_end]
                    post.post_listing_text_content = new_text + "..."



class BlogLink(models.Model):
    _name = "blog.link"
    _description = "Useful Links"
    _rec_name = "title"

    title = fields.Char(string='Title', required=True)
    link = fields.Char(
        string='Link', help='Add here external website link (e.g. https://www.google.com).')
    content = fields.Text(
        string='Content', help='Add content for external link.')
    date = fields.Datetime(compute='_compute_post_date', store=True)
    lang = fields.Selection(_lang_get, string='Language',
                            default=lambda self: self.env.lang,
                            help="Select language for useful link content",
                            required=True)

    @api.multi
    @api.depends('create_date')
    def _compute_post_date(self):
        for link in self:
            link.date = link.create_date
