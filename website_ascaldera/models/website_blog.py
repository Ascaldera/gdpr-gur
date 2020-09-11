# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from odoo import api, fields, models
from datetime import date,datetime


@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()


class BlogPostType(models.Model):
    _name = "blog.post.type"

    name = fields.Char(string='Name', translate=True)


class BlogPost(models.Model):
    _inherit = "blog.post"
    _order = 'document_date desc'

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

    def get_date(self):
        for r in self:
            if r.document_date==False and r.create_date:
                r.document_date=r.create_date
    
    #ADDITION
    #------------------------------------------------------------------------------------------------------------------------------
    
    save_name=fields.Char(string='Saved name')
    
    sub_category_main=fields.Selection(string="Subcategory", 
                                       selection=[('foreign_legislation','Foreign legislation'),('slovenian_legislation','Slovenian legislation'),('SLO_commissioner_practice','SLO Information Commissioner\'s practice'),('SLO_judgments','Judgments of the Slovenian Court'),('foreign_practice','The practice of foreign oversight bodies'),('EU_judgments','Judgments of the European Court of Justice'),('escp_judgements','ECHR judgments'),('foreign_judgments','Judgments of foreign courts'), ('edpb_guidelines', 'EDPB guidelines and opinions')])
    sub_category_1=fields.Selection(string="Subcategory", 
                                    selection=[('SLO_commissioner_practice','SLO Information Commissioner\'s practice'), ('SLO_judgments','Judgments of the Slovenian Court'), ('foreign_practice','The practice of foreign oversight bodies'),('EU_judgments','Judgments of the European Court of Justice'),('escp_judgements','ECHR judgments'),('foreign_judgments','Judgments of foreign courts'), ('edpb_guidelines', 'EDPB guidelines and opinions')])
    sub_category_2=fields.Selection(string="Subcategory", 
                                    selection=[('foreign_legislation','Foreign legislation'),('slovenian_legislation','Slovenian legislation')])
    
    #Function to populate the main subcategory selection field or erase data from that field if something else was selected
    #Function to save the name of the blog_post_type_id field
    #------------------------------------------------------------------------------------------------------------------------------
    
    @api.onchange('blog_post_type_id','sub_category_1','sub_category_2')
    def spremeni_podkategorijo(self):
        if self.blog_post_type_id.name=="Judicial-Practice" or self.blog_post_type_id.name=="Sodna praksa":
            self.sub_category_2=[]
            if self.sub_category_1==False:
                self.sub_category_main=[]
        elif self.blog_post_type_id.name=="Legislation" or self.blog_post_type_id.name=="Zakonodaja":
            self.sub_category_1=[]
            if self.sub_category_2==False:
                self.sub_category_main=[]
        else:
            self.sub_category_1=[]
            self.sub_category_2=[]
            self.sub_category_main=[]
        if self.sub_category_1:
            self.sub_category_main=self.sub_category_1
        if self.sub_category_2:
            self.sub_category_main=self.sub_category_2
        if self.blog_post_type_id:
            self.save_name=self.blog_post_type_id
        else:
            self.save_name=""
    
    #------------------------------------------------------------------------------------------------------------------------------
    
    @api.multi
    def _get_text_content(self):
        for post in self:
            soup = BeautifulSoup(post.content)
            post.post_listing_text_content = soup.get_text()


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
