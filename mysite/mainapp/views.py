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
    highest_image_pk = 500
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
        print "ohboy"
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

    return render_to_response('image.html', {'image': image, 'image_urls': image_urls})



'''
def get_user_or_create(ip_address):
    try:
        user = real_time_voting.mainapp.models.User.objects.get(ip_address=ip_address)
    except real_time_voting.mainapp.models.User.DoesNotExist:
        print "making a new user" # NOTE: DEBUG
        # make a new user
        user = real_time_voting.mainapp.models.User(ip_address=ip_address)
        user.save()
    return user
        

def main(request):
    # get all events from db
    events = real_time_voting.mainapp.models.Event.objects.all()
    
    return render_to_response('index.html', {'events': events})


def create_event(request):
    return render_to_response('create_event.html', {})

def view_results(request, event__pk):
    votes = real_time_voting.mainapp.models.Vote.objects.order_by('timestamp').filter(timestamp__isnull=False).filter(event__pk=event__pk).reverse()
    event = real_time_voting.mainapp.models.Event.objects.get(pk=event__pk)
    return render_to_response('results.html', {'successful_vote': True, 'votes': votes, 'event': event})

def create_event_do(request):
    name = request.POST['name']
    description = request.POST['description']
    newevent = real_time_voting.mainapp.models.Event(name=name, description=description)
    newevent.save()
    #url_to_redirect_to = reverse(real_time_voting.mainapp.views.event) + "/" + newevent.pk
    url_to_redirect_to = "event/" + str(newevent.pk)
    return HttpResponseRedirect(url_to_redirect_to)

def event(request, event__pk):
    event = real_time_voting.mainapp.models.Event.objects.get(pk=event__pk)
    user = get_user_or_create(request.META.get('REMOTE_ADDR'))
    her_num_votes = len(real_time_voting.mainapp.models.Vote.objects.all().filter(user=user))
    return render_to_response('event.html', {'event': event, 'user': user, 'her_num_votes': her_num_votes})

def process_vote_do(request):
    weight = request.POST['weight']
    event = real_time_voting.mainapp.models.Event.objects.get(pk=request.POST['event__pk'])
    user = get_user_or_create(request.META.get('REMOTE_ADDR'))
    newvote = real_time_voting.mainapp.models.Vote(weight=weight, timestamp=datetime.datetime.now(), event=event, user = user)
    newvote.save()

    #url_to_redirect_to = reverse(real_time_voting.mainapp.views.vote_success)
    url_to_redirect_to = "event/" + str(event.pk)
    return HttpResponseRedirect(url_to_redirect_to)

def process_user_do(request):
    user = get_user_or_create(request.META.get('REMOTE_ADDR'))
    user.name = request.POST['name']
    user.age = request.POST['age']
    user.gender = request.POST['gender']
    user.save()
    from_event__pk = request.POST['from_event__pk']

#    url_to_redirect_to = reverse(real_time_voting.mainapp.views.event)
    url_to_redirect_to = "/event/%s" % from_event__pk
    return HttpResponseRedirect(url_to_redirect_to)
    '''
