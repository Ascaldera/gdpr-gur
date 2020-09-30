# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields,_


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _set_signup_uninvited(self):
        for website in self.search([]):
            website.write({'auth_signup_uninvited': 'b2c'})

class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    is_blog_type = fields.Boolean('Is blog type?', default=False)
    blog_type_id = fields.Many2one('blog.post.type',
                                        string='Blog Post Type',
                                        help='Select blog post type')