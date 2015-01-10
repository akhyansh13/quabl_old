import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Simpler.settings')
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from models import Post, Simpler, UserForm, UserProfileForm, HighlightDesc, highlightq, highlight, topic, ReqByUser, UserNotification, UserProfile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from functions import show_less_post, show_less_ques, show_less_ans #,hfilter
import json
from django.contrib.auth.models import User
import PIL
from PIL import Image
import urllib

def index(request):
    context = RequestContext(request)

    contextsimplers = Simpler.objects.all().filter(parent_list='contextsimpler')
    context_dict = {'contexts':contextsimplers}

    contextarr = []

    for contextsimpler in contextsimplers:
        highlightset = highlight.objects.all().filter(highlight_parent=contextsimpler)
        hqarr = []
        for h in highlightset:
            hqarr.append(highlightq.objects.all().filter(highlight=h))
        contextarr.append([contextsimpler, highlightset, hqarr])

    context_dict['contarr'] = contextarr

    if request.user.is_authenticated():
        user_profile = UserProfile.objects.get(user=request.user)
        followedposts = user_profile.followed_posts.split(';')
        followed = []
        for fpost in followedposts:
            followed.append(int(fpost))
        context_dict['followed'] = followed
    return render_to_response('SimplerApp/index.html', context_dict, context)

def indexalt(request):
    context = RequestContext(request)

    contextsimplers = Simpler.objects.all().filter(parent_list='contextsimpler')
    context_dict = {'contexts':contextsimplers}

    contextarr = []

    for contextsimpler in contextsimplers:
        highlightset = highlight.objects.all().filter(highlight_parent=contextsimpler)
        hqarr = []
        for h in highlightset:
            hqarr.append(highlightq.objects.all().filter(highlight=h))
        contextarr.append([contextsimpler, highlightset, hqarr])

    context_dict['contarr'] = contextarr

    if request.user.is_authenticated():
        user_profile = UserProfile.objects.get(user=request.user)
        followedposts = user_profile.followed_posts.split(';')
        followed = []
        for fpost in followedposts:
            followed.append(int(fpost))
        context_dict['followed'] = followed
    return render_to_response('SimplerApp/indexalt.html', context_dict, context)

def follow(request):
    context = RequestContext(request)
    post_id = request.GET['post_id']
    user_profile = UserProfile.objects.get(user=request.user)
    followedposts = user_profile.followed_posts.split(';')
    if post_id in followedposts:
        del followedposts[followedposts.index(post_id)]
    else:
        followedposts.insert(-1, post_id)
    user_profile.followed_posts = ';'.join(followedposts)
    user_profile.modified = datetime.now()
    user_profile.save()
    return HttpResponse('success')

def addpost(request):
    context = RequestContext(request)
    context_text = request.GET['txt']
    ptopic = topic.objects.get_or_create(topic = request.GET['topic'])[0]
    p = Post.objects.get_or_create(topic=ptopic, post=context_text ,author=request.user.username, writer=request.user, context=context_text)[0]
    s = Simpler.objects.get_or_create(post=p, question=-1, answer=p.context, simpler_original=p.context, coeficient=1, parent_list='contextsimpler', author=request.user.username, writer=request.user, display=' ')[0]
    return HttpResponse(str(s.id))

def question(request, question_id):
    context = RequestContext(request)
    ques = highlightq.objects.get(id=int(question_id))
    context_dict = {'ques':ques}

    contextsimpler = Simpler.objects.get(id=ques.highlight.highlight_parent.id)
    context_dict['contextsimplerid'] = contextsimpler.id

    answers = Simpler.objects.all().filter(question=question_id)
    context_dict['anscount'] = len(answers)

    highlights = highlight.objects.all()
    questions = highlightq.objects.all()
    highs = highlights.filter(highlight_parent=contextsimpler)
    rquestions = []

    for answer in answers:
        highs = highlights.filter(highlight_parent=answer)
        for high in highs:
            rquestions.extend(questions.filter(highlight=high))

    context_dict['rquestions'] = rquestions
    context_dict['answers'] = answers

    return render_to_response('SimplerApp/question.html', context_dict, context)

def csimpler(request, simpler_id):
    context = RequestContext(request)

    questions = highlightq.objects.all()

    contextsimpler = Simpler.objects.get(id = int(simpler_id))
    context_dict = {'answer':contextsimpler}

    highlights = highlight.objects.all()

    cquestions = []

    highs = highlights.filter(highlight_parent=contextsimpler)
    for high in highs:
            cquestions.extend(questions.filter(highlight=high))

    context_dict['rquestions'] = cquestions

    return render_to_response('SimplerApp/context.html', context_dict, context)

def makesimpler(request):
    context = RequestContext(request)
    questionid = int(request.GET['qid'])
    simpler_text = request.GET['simpler_text']

    ques = highlightq.objects.get(id=questionid)
    post = ques.highlight.highlight_parent.post
    coefficient = ques.highlight.highlight_parent.coeficient + 1
    parent_list = 'parent' + str(ques.highlight.highlight_parent.id) + ques.highlight.highlight_parent.parent_list

    c = Simpler.objects.get_or_create(post=post, question=questionid, answer=simpler_text, simpler_original=simpler_text, coeficient=coefficient, parent_list=parent_list, author=request.user.username, writer=request.user, display=' ')[0]
    return HttpResponse('success')

def register(request):
    context = RequestContext(request)
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)

            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.created = datetime.now()
            profile.modified = datetime.now()
            name_arr = profile.full_name.split(' ')
            count = 0
            for n in name_arr:      #Looks for first word and filters out '' or ' '
                if n != '' and n != ' ':
                    user.first_name = n
                    break
            name_arr.reverse()
            for t in name_arr:
                if t != '' and t != ' ':
                    if t != user.first_name:
                        user.last_name = t
                        break
            profile.save()
            user.save()

            registered = True

            profpic = Image.open(profile.picture.path)  #Primitive image filter.
            profpic = profpic.resize((300,300), PIL.Image.ANTIALIAS)
            profpic.save(profile.picture.path)
            thumbnail = profpic.resize((32,32), PIL.Image.ANTIALIAS)
            thumbnail.save(str(profile.picture.path).replace('profile_images','thumbnails'), 'JPEG')

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
            'SimplerApp/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your Quabl account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid Username or Password.")

    else:
        return render_to_response('SimplerApp/login.html', {}, context)

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/')

def define(request, post_id, simpler_id, answer_part, quabl, cques, highlightx):

    context = RequestContext(request)

    answer_part = answer_part.replace("xqmx", "?")

    cques = cques.replace('xqmx', '?')

    post_id = int(post_id)
    simpler_id = int(simpler_id)
    flag = False

    if answer_part == 'undefined':
        answer_part = ''

    encodedquabl = quabl

    answer_part = answer_part.replace('<span id="blankspace">&nbsp;</span></span>', " ")
    answer_part = answer_part.replace('<span id="noblankspace"></span></span>', "")
    answer_part = answer_part.replace('<span class="highlight-wrapper">&nbsp;', " ")
    answer_part = answer_part.replace('<span class="highlight-wrapper">', "")

    post = Post.objects.get(id=post_id)
    simpler = Simpler.objects.get(id=simpler_id)

    h = highlight.objects.get_or_create(highlight=highlightx, highlight_parent=simpler)[0]

    f = highlightq.objects.get_or_create(highlight=h, req_by = request.user, created = datetime.now(), question = cques)[0]

    simpler.answer = answer_part.replace("idtobesetinview", str(h.id)).replace("texthtmlgoeshere", encodedquabl)

    simpler.modified = datetime.now()
    simpler.save()

    #question = highlightq.objects.get_or_create(highlight=f, question=f.description, created = datetime.now())

    #return HttpResponseRedirect('/request/askforsimpler/postid:' + str(post_id) + ';simplerid:' + str(simpler_id) + ';')

    return HttpResponse(simpler.answer + '<cqdelimit>' + str(simpler.id) + '<cqdelimit>' + cques + '<cqdelimit>' + str(f.highlight.id) + '<cqdelimit>' + str(f.highlight.highlight_parent.id) + '<cqdelimit>' + str(f.id))

def defined(request, h_id, cques):

    context = RequestContext(request)

    h = highlight.objects.get(id=int(h_id))
    f = highlightq.objects.get_or_create(highlight=h, req_by = request.user, created = datetime.now(), question = cques.replace('xqmx', '?'))[0]

    return HttpResponse(str(f.highlight.highlight_parent.id) + '<cqdelimit>' + f.question + '<cqdelimit>' + str(f.highlight.id) + '<cqdelimit>' + str(f.highlight.highlight_parent.id) + '<cqdelimit>' + str(f.id))

def requestbyuser(request, category, description):
    context = RequestContext(request)

    if category == 'back_to_post' or category == 'askforsimpler' or category == 'addsimpler': #or category == 'redirected':
        postid = description.split('postid:')[1].split(';')[0]
        if request.user.is_authenticated():
            c = ReqByUser.objects.get_or_create(user=request.user, category=category, description=description)
            if c[1]:
                c[0].created = datetime.now()
            c[0].modified = datetime.now()
            c[0].frequency = c[0].frequency + 1
            c[0].save()
            return HttpResponseRedirect('/simpler/' + postid + '/' + str(c[0].id) + '/')
        else:
            return HttpResponseRedirect('/simpler/' + postid)

    elif category == 'notifications':
        notif_id = int(description)
        notification = UserNotification.objects.get(id=notif_id)
        post_id = notification.postid
        notification.status = 'read'
        notification.save()
        c = ReqByUser.objects.get_or_create(user=request.user, category=category, description=description)
        if c[1]:
            c[0].created = datetime.now()
        c[0].modified = datetime.now()
        c[0].frequency = c[0].frequency + 1
        c[0].save()
        simpler_id = notification.simplerid
        if simpler_id > -1:
            c = ReqByUser.objects.get_or_create(user=request.user, category='back_to_post', description='postid:' + str(post_id) + ';simplerid:' + str(simpler_id) + ';')
            if c[1]:
                c[0].created = datetime.now()
            c[0].modified = datetime.now()
            c[0].frequency = c[0].frequency + 1
            c[0].save()
            return HttpResponseRedirect('/simpler/' + str(post_id) + '/' + str(c[0].id) + '/')
        else:
                return HttpResponseRedirect('/simpler/' + str(post_id) + '/')

    elif category == 'explore':
        postid = description
        post = Post.objects.get(id=int(postid))
        post.explores = post.explores + 1
        post.save()
        if request.user.is_authenticated():
            c = ReqByUser.objects.get_or_create(user=request.user, category=category, description='postid:' + description)
            if c[1]:
                c[0].created = datetime.now()
            c[0].modified = datetime.now()
            c[0].frequency = c[0].frequency + 1
            c[0].save()
        return HttpResponseRedirect('/simpler/' + postid + '/')

def addanswer(request, qid):
    context = RequestContext(request)
    q = highlightq.objects.get(id=qid)
    #simpler = '<p>' + q.question + '</p>'
    context_dict = {'q':q}
    context_dict['post_id'] = q.highlight.highlight_parent.post.id
    return render_to_response('SimplerApp/addsimpler.html', context_dict, context)

def getUserProfile(request, user_id):
    context = RequestContext(request)
    request_user_id = request.user.id
    request_user = request.user
    user_id_int = int(user_id)
    if request_user_id == user_id_int:
        uprof = UserProfile.objects.get(user=request_user)
        req = {'username':uprof.user.username}
        req['picurl'] = uprof.picture.url
        req['fullname'] = request_user.first_name + " " + request_user.last_name
        req['shortbio'] = uprof.shortbio
        data = json.dumps(req)
    else:
        required_user = User.objects.get(id=user_id_int)
        required_user_profile = UserProfile.objects.get(user=required_user)
        req = {'username':required_user.username}
        req['picurl'] = required_user_profile.picture.url
        req['fullname'] = required_user.first_name + " " + required_user.last_name
        req['shortbio'] = required_user_profile.shortbio
        data = json.dumps(req)
    return HttpResponse(data)

def addpostext(request):
    context = RequestContext(request)
    userreqed = User.objects.get(username='anonymous')
    contextpost = request.GET['context']
    Post.objects.get_or_create(post=contextpost, author = 'anonymous', writer=userreqed, context=contextpost)
    return HttpResponse('successful')

def getthumburl(request, username):
    context = RequestContext(request)
    requser = User.objects.get(username=username)
    requp = UserProfile.objects.get(user=requser)
    return HttpResponse((requp.picture.url).replace('profile_images', 'thumbnails'))
