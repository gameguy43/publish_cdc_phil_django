# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
#from mysite.mainapp.models 
import datetime
import sqlalchemy

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
    # TODO: fix the unicode chars
    image['copyright'] = image['copyright'].strip("'").replace('None', '<a href="http://creativecommons.org/licenses/publicdomain/" rel="license">None</a>')

    def categories_to_html(python_list):
        trimmed = python_list.replace("u'", "").strip("\n\\'")[1:] # this last trimming ([1:0]) is cus the first char ends up being an n from an old \n
        if not trimmed:
            return ''
        categories = trimmed.split('\\n')
        categories = map(lambda category: category.split(" ", 1), categories)
        #okay, so now we have a multi-dimensional list.  good.
        retval = "<ul>"
        for spaces, category in categories:
            retval += '<li>' + "&nbsp;"*int(spaces) + category + "</li>\n"
        retval += "</ul>"
        return retval

    image['categories'] = categories_to_html(image['categories'])

    def links_to_html(python_list):
        stripped = python_list.strip('"[]')
        if not stripped:
            return ''
        stripped = stripped.rsplit("')", 1)[0]
        stripped = stripped.split("(u'", 1)[1]
        stripped = stripped.split("'), (u'")
        stripped = map(lambda link: link.split("', u'", 1), stripped)

        #okay, so now we have a multi-dimensional list.  good.
        retval = "<ul>"
        for string, url in stripped:
            retval += '<li><a href="' + url + '">' + string + "</a></li>\n";
        retval += "</ul>"

        return retval

    image['links'] = links_to_html(image['links'])
    image['next_id'] = int(image['id']) + 1
    image['prev_id'] = int(image['id']) - 1

    image['desc'] = image['desc'].decode('utf-8')


    thestr = u'<td><b>In this 1993 image, the front of a women\u2019s clinic revealed a front door that was accessed via a two-step stoop, which made accessibility an issue for the wheelchair-seated man shown here who\u2019d just exited the premises. Visits by individuals having problems with mobility, prompted the installation of a temporary plywood ramp. Though the temporary ramp made access easier for the mobility-challenged, it was constructed in such a way as to make it a dangerous, though short-term solution (see PHIL 9022 - 9025). PHIL image 9027 - 9029 depicted a long-term, permanent solution using a brick, concrete, and metal ramp. It was not the perfect solution, for it lacked adequate maneuvering room near the clinic doorway. It also clearly appeared as an add-on, or after-the-fact solution that protruded into the wide sidewalk, while attempting to blend in with the existing buildings by using brick, colored concrete, and wrought iron rails. Stairs had also been provided.</b><p>\u201cThe Center for Universal Design, CUD, is a national research, information, and technical assistance center that evaluates, develops, and promotes universal design in housing, public and commercial facilities, and related products.\u201d \u201cThe Center conducts original research to learn what design solutions are appropriate for the widest diversity of users, and what tools are most useful to practitioners wishing to successfully practice universal design. The Center collaborates with builders and manufacturers on the development of new design solutions. It also develops publications and instructional materials, and provides information, referrals and technical assistance to individuals with disabilities, families, and professionals nationwide and internationally.\u201c</p></td>'

    image['desc'] = thestr

    return render_to_response('image.html', {'image': image, 'image_urls': image_urls})
