# Ascaldera - Website

## Version

Odoo 12.0

## Installation

1. Add the module in `addons` path of Odoo configuration.
2. Restart the Odoo server and update the module list.
3. Install module `website_ascaldera`.

## Prerequisites

1. Create Blog Posts with Cover Image,Title,Subtitle,Tags,Content,Listing Content and Blog post type(News,Articles and Judicial-Practice)
2. Go to Website->Configuration->Blogs->Useful Link and create blog links with Title, Link and Content

## Features

1. Design Ascaldera website in Odoo as per demo at: http://demo.ascaldera.com/ggg/
2. Display data of `News,Articles,Judicial-Practice and Legislation` from Odoo backend to website
3. Define `Search section` for blog posts and display: Title, Date, Content and Link.
4. Perform Api call to http://staging.app.gdpr.ascaldera.com//api/v1/documents/search?query=zakon and fetch legislation posts
5. Display `Useful Links` with Title,Description and link at right section.

## Usage

1. Here is the website "sitemap":
	*News: Data from odoo blog post with “Blog Post Type” = news
	*Articles: Data from odoo blog post with “Blog Post Type” = article
	*Judicial practice: Data from odoo blog post with “Blog Post Type” = practice
	*Legislation: Data from odoo blog post with “Blog Post Type” = legislation
2. Top section:
    *Language chooser    
    *Contact number
    *Login: link to odoo login page
    *Signup: link to external register page 
3. Media box: Display last 5 items from blog post in a carousel
4. Section `MOST READ NEWS`: inline listing of blogs with type="news"(3 most viewed blog posts)
5. Section `PROFESSIONAL ARTICLES`: Listing of blogs with type = article - image on the left; title + date + short content on the right
6. Section `JUDICIAL PRACTICES`: Listing of blogs with type = practice - image on the left; title + date + short content on the right
7. Right Section:
	*Add dummy urls for menus: DPO and HUB APP
	*Search: On the left side of the search page, there are "groups". If the  selected "group" is not type = external, search is done in Odoo (just for that group). If type = external, search is done via API. Content is displayed with - image on the left; title + date + short content on the right.
	*FAVORITE TAGS:listing of post tags
	*FROM THE CONTENT:News groups listing with number of items in the brackets
	*E-novice
	*USEFUL LINKS: Links listing with title,date,short content and link
8. Footer: Design footer as per demo link
