# -*- coding: utf-8 -*-

{
    'name': 'Website Ascaldera',
    'summary': 'Design Website Blog and its post',
    'description': """
This module develops website sitemap with different blog posts of type:

* News
* Articles
* Judicial practice
* Legislation
    """,
    'category': 'Website',
    'version': '12.0.1.0.0',
    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'depends': ['website_blog', 'auth_oauth', 'mass_mailing', 'website_sale_digital'],
    'data': [
        'security/ir.model.access.csv',
        'data/website_menu.xml',

        'data/blog_data.xml',
        'views/website_blog_views.xml',
        'views/assets.xml',
        'views/website_template.xml',
        'views/website_menu.xml',

    ],
    'qweb': ['static/src/xml/template.xml'],
    'installable': True,
    'auto_install': False,
}
