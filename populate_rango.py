import os
from unicodedata import category
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tango_with_django_project.settings")

import django
django.setup()
from rango.models import Category, Page

def populate():

    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.

    python_pages = [
        {'title': 'Official Python Tutorial',
        'url':'http://docs.python.org/3/tutorial/',
        'views':16},
        {'title':'How to Think like a Computer Scientist',
        'url':'http://www.greenteapress.com/thinkpython/',
        'views':876},
        {'title':'Learn Python in 10 Minutes',
        'url':'http://www.korokithakis.net/tutorials/python/',
        'views':69} ]

    django_pages = [
        {'title':'Official Django Tutorial',
        'url':'https://docs.djangoproject.com/en/2.1/intro/tutorial01/',
        'views':9873},
        {'title':'Django Rocks',
        'url':'http://www.djangorocks.com/',
        'views':2340698},
        {'title':'How to Tango with Django',
        'url':'http://www.tangowithdjango.com/',
        'views':4} ]

    other_pages = [
        {'title':'Bottle',
        'url':'http://bottlepy.org/docs/dev/',
        'views':5},
        {'title':'Flask',
        'url':'http://flask.pocoo.org',
        'views':42} ]

    cats = {'Python': {'pages': python_pages, 'views': 128, 'likes': 64},
        'Django': {'pages': django_pages, 'views': 64, 'likes': 32},
        'Other Frameworks': {'pages': other_pages,  'views': 32, 'likes': 16} }

    
    #The code below goes through the cats dictionary, adds each category to the database,
    #then adds each page associated with each category to the database.
    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data['views'], cat_data['likes'])
        for p in cat_data['pages']:
            add_page(c, p['title'], p['url'], views=p['views'])

    #Print out the categories we have added.
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print(f'- {c}: {p}')


#get_or_create() creates a new object unless it already exists and returns (object, created <-- (True or False)) as a tuple, hence the [0]
def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0] #<-----
    p.url=url
    p.views=views
    p.save()
    return p

def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c

#Start execution here!
if __name__ == '__main__':
    print('Starting Rangp population script...')
    populate()
    
#Using __name__ == '__main__' allows the script to be run as a standalone script or imported as a module.
#If the script is run as standalone, it will be __main__ so this will run, if its imported however
#it won't be __main__ so this code won't execute.
    