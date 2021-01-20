# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _set_signup_uninvited(self):
        for website in self.search([]):
            website.write({'auth_signup_uninvited': 'b2c'})
