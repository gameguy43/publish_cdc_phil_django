# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
#from mysite.mainapp.models 
import datetime
import sqlalchemy
import json

from django.conf import settings

import random


def get_metadata_db_connection():
    return sqlalchemy.create_engine(settings.METADATA_ENGINE)


def index(request):
    return render_to_response('index.html')

def about(request):
    return render_to_response('index.html')

def view_random(request):
    highest_image_pk = 12049
    # TODO: actually write code to figure out the above
    random_image_pk = random.randrange(highest_image_pk)
    url_to_redirect_to = "view/" + str(random_image_pk)
    return HttpResponseRedirect(url_to_redirect_to)

def view_image(request, image__pk):
    db_connection = get_metadata_db_connection()
    image_tuples = db_connection.execute("select * from phil where id = %s" % image__pk).fetchone().items()
    image = {}
    image.update(image_tuples)

    if not image['url_to_lores_img']:
        referrer = request.META.get('HTTP_REFERER')
        if not referrer.find('/view/') == (-1):
            prev_id = int(referrer.rstrip('/').rsplit('/', 1)[1])
            # if they hit the previous button
            if int(image__pk) < prev_id:
                url_to_redirect_to = "/view/" + str(int(image__pk)-1)
            # if they hit the next button
            # (or something fishy is going on)
            else:
                url_to_redirect_to = "/view/" + str(int(image__pk)+1)
        else:
            url_to_redirect_to = "/view_random" 
            
        return HttpResponseRedirect(url_to_redirect_to)

    def floorify(id):
        ## mod 100 the image id numbers to make smarter folders
        floor = id - id % 100
        floored = str(floor).zfill(5)[0:3]+"XX"
        return floored
    floorified = floorify(image['id'])
    id_zfilled = str(image['id']).zfill(5)
    image_urls = {
        'hires':  settings.RELATIVE_DATA_ROOT + 'hires/' + floorified + "/" + id_zfilled + ".tif",
        'lores':  settings.RELATIVE_DATA_ROOT + 'lores/' + floorified + "/" + id_zfilled + ".jpg",
        'thumb':  settings.RELATIVE_DATA_ROOT + 'thumbs/' + floorified + "/" + id_zfilled + ".jpg",
    }

    # add link rel=license
    image['copyright'] = image['copyright'].strip("'").replace('None', '<a href="http://creativecommons.org/licenses/publicdomain/" rel="license">None</a>')


    def links_to_html(json_str):
        parsed = json.loads(json_str)
        retval = "<ul>"
        for string, url in parsed:
            retval += '<li><a href="' + url + '">' + string + "</a></li>\n";
        retval += "</ul>"
        return retval

    def categories_to_html(json_str):
        retval = "<ul>"
        parsed = json.loads(json_str)
        def print_with_spaces(dictionary, spaces):
            retval = ''
            if dictionary:
                for key in dictionary.keys():
                    retval += "<li>" + "&nbsp;"*spaces + key + "</li>\n"
                    retval += print_with_spaces(dictionary[key], spaces+1)
            return retval
        retval += print_with_spaces(parsed, 0)
        retval += "</ul>"
        return retval

    if image['links']:
        image['links'] = links_to_html(image['links'])
    if image['categories']:
        image['categories'] = categories_to_html(image['categories'])

    image['next_id'] = int(image['id']) + 1
    image['prev_id'] = int(image['id']) - 1

    return render_to_response('image.html', {'image': image, 'image_urls': image_urls})
