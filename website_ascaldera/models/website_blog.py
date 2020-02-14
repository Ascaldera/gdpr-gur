# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from odoo import api, fields, models


@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()


class BlogPostType(models.Model):
    _name = "blog.post.type"

    name = fields.Char(string='Name', translate=True)


class BlogPost(models.Model):
    _inherit = "blog.post"

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
