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
    'depends': ['website_blog', 'auth_oauth'],
    'data': [
        'security/ir.model.access.csv',
        'data/blog_data.xml',
        'views/website_blog_views.xml',
        'views/assets.xml',
        'views/website_template.xml',
    ],
    'qweb': ['static/src/xml/template.xml'],
    'installable': True,
    'auto_install': False,
}
