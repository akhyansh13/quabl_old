import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Simpler.settings')
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from models import Post, Simpler, UserForm, UserProfileForm, HighlightDesc, highlightq, highlight, topic, UserNotification, UserProfile, Link, activity, firstloginform, fback
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from functions import show_less_post, show_less_ques, show_less_ans #,hfilter
import json
from django.contrib.auth.models import User
import PIL
from PIL import Image
import urllib
from django.core.cache import cache

def tour(request):
    context = RequestContext(request)
    return render_to_response('SimplerApp/tour.html', context)

def page404(request):
    return render(request,'SimplerApp/404.html')

def page500(request):
    return render(request,'SimplerApp/500.html')

def page403(request):
    return render(request,'SimplerApp/403.html')

def page400(request):
    return render(request,'SimplerApp/400.html')


@login_required
def index(request):
    context = RequestContext(request)

    cache.clear()

    uprofile = UserProfile.objects.get(user=request.user)

    contextsimplers = Simpler.objects.all().filter(parent_list='contextsimpler')
    context_dict = {'contexts':contextsimplers}

    actqueryset = activity.objects.all()[::-1]
    actquerysetnew = []

    for act in actqueryset:
        if act.created > uprofile.last_seen:
            actquerysetnew.append(act)

    context_dict['newact'] = actquerysetnew
    context_dict['act'] = actqueryset

    contextarr = []

    for contextsimpler in contextsimplers:
        highlightset = highlight.objects.all().filter(highlight_parent=contextsimpler)
        hqarr = []
        for h in highlightset:
            hqarr.append(highlightq.objects.all().filter(highlight=h))
        contextarr.append([contextsimpler, highlightset, hqarr])

    contextarr = contextarr[::-1]

    context_dict['contarr'] = contextarr

    context_dict['last'] = uprofile.last_seen

    context_dict['uprofile'] = uprofile

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

    contextarr = contextarr[::-1]

    context_dict['contarr'] = contextarr
    return render_to_response('SimplerApp/indexalt.html', context_dict, context)

def follow(request):
    context = RequestContext(request)
    post_id = request.GET['post_id']
    p = Post.objects.get(id=int(post_id))
    if request.user in p.followers.all():
        p.followers.remove(request.user)
    else:
        p.followers.add(request.user)
    return HttpResponse('success')

def addpost(request):
    context = RequestContext(request)
    context_text = request.GET['txt']
    ptopic = topic.objects.get_or_create(topic = request.GET['topic'])[0]
    p = Post.objects.get_or_create(topic=ptopic, post=context_text ,author=request.user.username, writer=request.user, context=context_text)[0]
    s = Simpler.objects.get_or_create(post=p, question=-1, answer=p.context, simpler_original=p.context, coeficient=1, parent_list='contextsimpler', writer=request.user)[0]
    l = Link.objects.get_or_create(atext = request.GET['atext'], href = request.GET['link'], simpler=s, post=p)[0]
    p.followers.add(request.user)
    return HttpResponse(str(s.id))

@login_required
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

@login_required
def sutton(request):
    context = RequestContext(request)

    answers = []
    for i in range(804, 1107):
        if Simpler.objects.filter(id=i).exists():
            answers.append(Simpler.objects.get(id=i))

    context_dict = {'anscount': len(answers)}

    highlights = highlight.objects.all()
    questions = highlightq.objects.all()
    rquestions = []

    for answer in answers:
        highs = highlights.filter(highlight_parent=answer)
        for high in highs:
            rquestions.extend(questions.filter(highlight=high))

    context_dict['rquestions'] = rquestions
    context_dict['answers'] = answers

    return render_to_response('SimplerApp/content.html', context_dict, context)

@login_required
def suttonscroll(request, scrollto):
    context = RequestContext(request)

    answers = Simpler.objects.all().filter(question=-100)
    context_dict = {'anscount': len(answers)}

    highlights = highlight.objects.all()
    questions = highlightq.objects.all()
    rquestions = []

    for answer in answers:
        highs = highlights.filter(highlight_parent=answer)
        for high in highs:
            rquestions.extend(questions.filter(highlight=high))

    context_dict['rquestions'] = rquestions
    context_dict['answers'] = answers

    context_dict['scrollto'] = scrollto

    return render_to_response('SimplerApp/content.html', context_dict, context)


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

def makesimpler(request):                       #View that takes care of addition of answers.
    context = RequestContext(request)
    questionid = int(request.GET['qid'])
    simpler_text = request.GET['simpler_text']

    ques = highlightq.objects.get(id=questionid)
    post = ques.highlight.highlight_parent.post
    coefficient = ques.highlight.highlight_parent.coeficient + 1
    parent_list = 'parent' + str(ques.highlight.highlight_parent.id) + ' ' + ques.highlight.highlight_parent.parent_list

    c = Simpler.objects.get_or_create(post=post, question=questionid, answerto = ques.question , answer=simpler_text, simpler_original=simpler_text, coeficient=coefficient, parent_list=parent_list, writer=request.user)[0]
    l = Link.objects.get_or_create(atext = request.GET['atext'], href = request.GET['link'], simpler=c)[0]

    post.followers.add(request.user)

    actobj = activity.objects.create(user=request.user, question = ques, answer=c)
    #actobj = activity.objects.create(activity='<span class="getup" data='+ str(request.user.id) +'><a href="javascript:;">' + request.user.username + '</a></span><span class="notiftext"> added an answer. </span>' + '<div><span class="activitycontext">' + ques.highlight.highlight_parent.answer + '</span><span class="floatques">'+ ques.question +'</span></div><div class="activityques " data-id="'+ str(ques.id) +'" data-highlight="' + str(ques.highlight.id) + '" data-parent="' + str(ques.highlight.highlight_parent.id) + '"><a href="/question/'+ str(ques.id) +'/">' + ques.question + '</a></div><div class="activityans " data-ansid="' + str(c.id) + '">'+ c.answer + '</div>')

    #for u in post.followers.all():
        #if u != request.user:
            #UserNotification.objects.create(user=u, notification=request.user.username + ' added an answer to <div class="notifquestion notiflink" data-id="' + str(ques.id) + '">' + ques.question + '</div>', status="unread", created = datetime.now(), modified = datetime.now())

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
            try:
                if 'picture' in request.FILES:
                    profile.picture = request.FILES['picture']
                    profpic = Image.open(profile.picture.url)  #Primitive image filter.
                    profpic = profpic.resize((300,300), PIL.Image.ANTIALIAS)
                    profpic.save(profile.picture.url)
                    thumbnail = profpic.resize((32,32), PIL.Image.ANTIALIAS)
                    thumbnail.save(str(profile.picture.path).replace('profile_images','thumbnails'), 'JPEG')
            except:
                pass
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
            Post.objects.get(post='Sutton RL book.').followers.add(user)    #The new user gets RL notifications.
            registered = True

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
        if User.objects.filter(username=request.POST['username']).exists():
            username = request.POST['username']
        else:
            username = request.POST['username'].upper()

        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                if not request.user.email:
                    return HttpResponseRedirect('/firstlogin/')
                else:
                    return HttpResponseRedirect('/cs670/')
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

def define(request, post_id, simpler_id):

    context = RequestContext(request)

    answer_part = request.GET['answer_part'].replace("xqmx", "?")

    cques = request.GET['cques'].replace('xqmx', '?')

    anon = User.objects.get(username="Anonymous")

    post_id = int(post_id)
    simpler_id = int(simpler_id)
    flag = False

    if answer_part == 'undefined':
        answer_part = ''

    encodedquabl = request.GET['qh']

    answer_part = answer_part.replace('<span id="blankspace">&nbsp;</span></span>', " ")
    answer_part = answer_part.replace('<span id="noblankspace"></span></span>', "")
    answer_part = answer_part.replace('<span class="highlight-wrapper">&nbsp;', " ")
    answer_part = answer_part.replace('<span class="highlight-wrapper">', "")

    post = Post.objects.get(id=post_id)
    simpler = Simpler.objects.get(id=simpler_id)

    h = highlight.objects.get_or_create(highlight=request.GET['highlight'], highlight_parent=simpler)[0]

    if cques.find(' xanonx') == -1:
        if cques.find(' xassignx') == -1:
            f = highlightq.objects.get_or_create(highlight=h, req_by = request.user, question = cques)[0]
            actobj = activity.objects.create(user=request.user, question = f)
        else:
            f = highlightq.objects.get_or_create(highlight=h, req_by = request.user, question = cques.replace(' xassignx', ''), assignment='y')[0]
            actobj = activity.objects.create(user=request.user, question = f)
            #actobj = activity.objects.create(activity='<span class="getup" data="'+ str(request.user.id) +'"><a href="javascript:;">' + request.user.username + '</a></span><span class="notiftext"> has a question. </span>' + '<div class="activityques " data-id="'+ str(f.id) +'" data-parent="' + str(f.highlight.highlight_parent.id) + '"><a href="/question/'+ str(f.id) +'/">' + f.question + '</a></div>')
    else:
        f = highlightq.objects.get_or_create(highlight=h, req_by = anon, question = cques.replace(' xanonx', ''))[0]
        actobj = activity.objects.create(user=anon, question = f)
        #actobj = activity.objects.create(activity='Anonymous<span class="notiftext"> has a question. </span>' + '<div class="activityques " data-id="'+ str(f.id) +'" data-parent="' + str(f.highlight.highlight_parent.id) + '"><a href="/question/'+ str(f.id) +'/">' + f.question + '</a></div>')

    simpler.answer = answer_part.replace("idtobesetinview", str(h.id)).replace("texthtmlgoeshere", encodedquabl)

    simpler.save()

    #question = highlightq.objects.get_or_create(highlight=f, question=f.description, created = datetime.now())

    #return HttpResponseRedirect('/request/askforsimpler/postid:' + str(post_id) + ';simplerid:' + str(simpler_id) + ';')

    h.highlight_parent.post.followers.add(request.user)


    #for u in h.highlight_parent.post.followers.all():
        #if u != request.user:
            #UserNotification.objects.create(user=u, notification=f.req_by.username + ' added a question on <div data-id="'+ str(f.id) +'" class="simplernotif notiflink">' + h.highlight_parent.answer + '</div>', status='unread', created = datetime.now(), modified = datetime.now())

    return HttpResponse(simpler.answer + '<cqdelimit>' + str(simpler.id) + '<cqdelimit>' + f.question + '<cqdelimit>' + str(f.highlight.id) + '<cqdelimit>' + str(f.highlight.highlight_parent.id) + '<cqdelimit>' + str(f.id))

def defined(request, h_id, cques):

    context = RequestContext(request)

    h = highlight.objects.get(id=int(h_id))

    anon = User.objects.get(username="Anonymous")

    if cques.find(' xanonx') == -1:
        if cques.find(' xassignx') == -1:
            f = highlightq.objects.get_or_create(highlight=h, req_by = request.user, question = cques.replace('xqmx', '?'))[0]
            actobj = activity.objects.create(user=request.user, question = f)
        else:
            f = highlightq.objects.get_or_create(highlight=h, req_by = request.user, question = cques.replace('xqmx', '?').replace(' xassignx', ''), assignment='y')[0]
            actobj = activity.objects.create(user=request.user, question = f)
    else:
        f = highlightq.objects.get_or_create(highlight=h, req_by = anon, question = cques.replace('xqmx', '?').replace(' xanonx', ''))[0]
        actobj = activity.objects.create(user=anon, question = f)

    h.highlight_parent.post.followers.add(request.user)

    #for u in h.highlight_parent.post.followers.all():
        #if u != request.user:
            #UserNotification.objects.create(user=u, notification=f.req_by.username + ' added a question on <div data-id="'+ str(f.id) +'"class="simplernotif notiflink">' + h.highlight_parent.answer + '</div>', status='unread', created = datetime.now(), modified = datetime.now())

    return HttpResponse(str(f.highlight.highlight_parent.id) + '<cqdelimit>' + f.question + '<cqdelimit>' + str(f.highlight.id) + '<cqdelimit>' + str(f.highlight.highlight_parent.id) + '<cqdelimit>' + str(f.id))

def getUserProfile(request, user_id):
    context = RequestContext(request)
    request_user_id = request.user.id
    request_user = request.user
    user_id_int = int(user_id)
    if request_user_id == user_id_int:
        uprof = UserProfile.objects.get(user=request_user)
        req = {'username':uprof.user.username}
        if uprof.picture:
            req['picurl'] = uprof.picture.url
        else:
            req['picurl'] = '/quablmedia/profile_images/default.jpeg'
        req['fullname'] = request_user.first_name + " " + request_user.last_name
        req['shortbio'] = uprof.shortbio
        data = json.dumps(req)
    else:
        required_user = User.objects.get(id=user_id_int)
        required_user_profile = UserProfile.objects.get(user=required_user)
        req = {'username':required_user.username}
        if required_user_profile.picture:
            req['picurl'] = required_user_profile.picture.url
        else:
            req['picurl'] = '/quablmedia/profile_images/default.jpeg'
        req['fullname'] = required_user.first_name + " " + required_user.last_name
        req['shortbio'] = required_user_profile.shortbio
        data = json.dumps(req)
    return HttpResponse(data)

def addpostext(request):
    context = RequestContext(request)
    userreqed = User.objects.get(username='anonymous')
    contextpost = request.GET['context']
    Post.objects.get_or_create(post=contextpost, writer=userreqed, context=contextpost)
    return HttpResponse('successful')

def getthumburl(request, username):
    context = RequestContext(request)
    requser = User.objects.get(username=username)
    requp = UserProfile.objects.get(user=requser)
    if requp.picture:
        return HttpResponse((requp.picture.url).replace('profile_images', 'thumbnails'))
    else:
        return HttpResponse('/quablmedia/thumbnails/default.jpeg')

def upvote(request, type, id):
    context = RequestContext(request)
    if type=='ans':
        reqed = Simpler.objects.get(id = int(id))
    else:
        reqed = highlightq.objects.get(id = int(id))
    if request.user in reqed.upvoters.all():
        reqed.upvoters.remove(request.user)
        return HttpResponse('unupvoted')
    else:
        reqed.upvoters.add(request.user)
        return HttpResponse('upvoted')

def ucheck(request, type, id):
    context = RequestContext(request)
    if type=='ans':
        reqed = Simpler.objects.get(id = int(id))
    else:
        reqed = highlightq.objects.get(id = int(id))
    if request.user in reqed.upvoters.all():
        return HttpResponse('upvoted')
    else:
        return HttpResponse('unupvoted')

def lastseen(request):
    context = RequestContext(request)
    uprofile = UserProfile.objects.get(user=request.user)
    uprofile.last_seen = datetime.now()
    uprofile.save()
    return HttpResponse('success')

def firstlogin(request):
    context = RequestContext(request)

    if request.method == 'POST':

        profile_form = firstloginform(data=request.POST)

        # If the two forms are valid...
        if profile_form.is_valid():

            profile = profile_form.save(commit=False)
            request.user.username = profile.username
            request.user.set_password(profile.password)
            request.user.email = profile.email
            request.user.save()
            UserProfile.objects.get_or_create(user=request.user)
            return HttpResponseRedirect('/done/')

        else:
            print profile_form.errors


    else:
        profile_form = firstloginform()

    return render_to_response(
            'SimplerApp/firstlogin.html',
            {'profile_form': profile_form},
            context)


def done(request):
    context = RequestContext(request)
    return render_to_response('SimplerApp/tourprime.html', context)

@login_required
def sutton1(request):
    context = RequestContext(request)

    answers = []
    for i in range(1134, 1467):
        if Simpler.objects.filter(id=i).exists():
            answers.append(Simpler.objects.get(id=i))

    context_dict = {'anscount': len(answers)}

    highlights = highlight.objects.all()
    questions = highlightq.objects.all()
    rquestions = []

    for answer in answers:
        highs = highlights.filter(highlight_parent=answer)
        for high in highs:
            rquestions.extend(questions.filter(highlight=high))

    context_dict['rquestions'] = rquestions
    context_dict['answers'] = answers

    return render_to_response('SimplerApp/content.html', context_dict, context)

@login_required
def sutton2(request):
    context = RequestContext(request)

    answers = []
    for i in range(1469, 1827):
        if Simpler.objects.filter(id=i).exists():
            answers.append(Simpler.objects.get(id=i))

    context_dict = {'anscount': len(answers)}

    highlights = highlight.objects.all()
    questions = highlightq.objects.all()
    rquestions = []

    for answer in answers:
        highs = highlights.filter(highlight_parent=answer)
        for high in highs:
            rquestions.extend(questions.filter(highlight=high))

    context_dict['rquestions'] = rquestions
    context_dict['answers'] = answers

    return render_to_response('SimplerApp/content.html', context_dict, context)

@login_required
def sutton2scroll(request, scrollto):
    context = RequestContext(request)

    answers = []
    for i in range(1469, 1827):
        if Simpler.objects.filter(id=i).exists():
            answers.append(Simpler.objects.get(id=i))

    context_dict = {'anscount': len(answers)}

    highlights = highlight.objects.all()
    questions = highlightq.objects.all()
    rquestions = []

    for answer in answers:
        highs = highlights.filter(highlight_parent=answer)
        for high in highs:
            rquestions.extend(questions.filter(highlight=high))

    context_dict['scrollto'] = scrollto

    context_dict['rquestions'] = rquestions
    context_dict['answers'] = answers

    return render_to_response('SimplerApp/content.html', context_dict, context)

@login_required
def sutton1scroll(request ,scrollto):
    context = RequestContext(request)

    answers = []
    for i in range(1134, 1467):
        if Simpler.objects.filter(id=i).exists():
            answers.append(Simpler.objects.get(id=i))

    context_dict = {'anscount': len(answers)}

    highlights = highlight.objects.all()
    questions = highlightq.objects.all()
    rquestions = []

    for answer in answers:
        highs = highlights.filter(highlight_parent=answer)
        for high in highs:
            rquestions.extend(questions.filter(highlight=high))

    context_dict['rquestions'] = rquestions
    context_dict['answers'] = answers

    context_dict['scrollto'] = scrollto

    return render_to_response('SimplerApp/content.html', context_dict, context)

def sysbio(request):
    context = RequestContext(request)
    test = 'test'
    context_dict = {'test':test}
    return render_to_response('SimplerApp/sysbio2.html', context_dict, context)

def feedback(request, fdback):
    context = RequestContext(request)
    fback.objects.create(fback=request.user.username + fdback.replace('xqmx', '?'))
    return HttpResponse('success')

def enotification(request, enotif):
    context = RequestContext(request)
    up = UserProfile.objects.get(user=request.user)
    up.emailnotif = enotif
    up.save()
    return HttpResponse('success')
