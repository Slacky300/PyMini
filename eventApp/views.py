import json
from django.shortcuts import render, redirect
from . forms import EventPlaceFrm, CreateEventFrm
from . models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . filters import VenueFilter
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from . decorators import unauthenticated_user, allowed_users
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from . utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
import threading
from django.views import View
from django.contrib.auth.models import Group

class EmailThread(threading.Thread):

    def __init__(self,email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()



def send_action_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('authentication/activate.html',{
        'user': user,
        'domain' : current_site,
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : generate_token.make_token(user)
    })

    email = EmailMessage(subject= email_subject, body=email_body,from_email = settings.EMAIL_HOST_USER,to = [user.email])
    EmailThread(email).start()


# Create your views here.
def home(request):
    

    return render(request,'main/land.html')


@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Staff'])
def addEventL(request):

    ints = {
        'owner' : request.user,
    }

    frm = EventPlaceFrm(initial=ints)
    context = {
        'form' : frm
    }
    if request.method == 'POST':
        try:

            frm = EventPlaceFrm(request.POST,request.FILES,initial=ints)
            if frm.is_valid():
                frm.save()
                messages.success(request,'Submitted Successfully')
                return redirect('venues')
        except Exception as e:
            messages.error(request,'Failed to submit')
            context['e'] = e
            return render(request,'main/forms/addEventLocation.html',context)

    return render(request,'main/forms/addEventLocation.html',context)


def places(request):


    lct = Venues.objects.all()
    venueFltr = VenueFilter(request.GET, queryset = lct)
    context = {
        'venue' : venueFltr,
    }
    return render(request,'main/places.html',context)


@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Users'])
def createEvent(request,slug):

    venue = Venues.objects.get(slug = slug)
    
    ints = {
        'eveManager' : request.user,
        'venue' : venue,
    }
    frm = CreateEventFrm(initial=ints)
    context = {
        'venue' : venue,
        'form' : frm,
    }
    if request.method == 'POST':
        try:
            frm = CreateEventFrm(request.POST,request.FILES)
            vnu = request.POST.get('venue')
            price = request.POST.get('price')
            eve = CreatEvent.objects.filter(venue = venue)
            stDate = request.POST.get('startDate')
            avilb = True
            for x in eve:
                if x.startDate.strftime("%Y-%m-%d") == stDate:
                    avilb = False
            if not avilb:
                messages.error(request,f'{venue.name} is not available on {stDate}')
                return redirect('/createEvent/'+slug)
            else:
                print('-----------------See the format----------')
            if frm.is_valid():
                    venueX = Venues.objects.get(id = vnu)
                    venueX.availabililty = False
                    venueX.save()
                    frm.save()
                    messages.success(request,'Submitted Successfully')
                    frm.clean()
                    event = CreatEvent.objects.get(venue = venueX)
                    event.tBkngPrice = price
                    event.save()
                    return redirect('eventCrude')
        except:
            messages.error(request,'Failed to submit')
            return render(request,'main/forms/createEvent.html',context)
    else:
        
        return render(request,'main/forms/createEvent.html',context)
    

@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Users'])
def venueDetail(request, slug):

    venue = Venues.objects.get(slug = slug)
    context = {
        'venue' : venue,
    }
    return render(request,'main/details/venueDetail.html',context)





@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Users'])
def eventCrude(request):

    events = CreatEvent.objects.filter(eveManager = request.user)

    msg = Msgs.objects.filter(recvr = request.user)
    context = {
        'eve' : events,
        'msg' : msg,
    }
    return render(request,'main/crud/eventCrud.html',context)






@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Users'])
def eventDelete(request,slug):

    events = CreatEvent.objects.get(slug = slug)
    venue = Venues.objects.get(slug = events.venue.slug)
    venue.availabililty = True
    venue.save()
    events.delete()
    messages.success(request,'Event deleted successfully')
    return redirect('eventCrude')






@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Users'])
def eventEdit(request, slug):
    event = CreatEvent.objects.get(slug = slug)
    venue = Venues.objects.get(slug = event.venue.slug)

    ints = {
        'eveManager' : request.user,
        'venue' : event.venue,
        'name' : event.name,
        'eveTyp' : event.eveTyp,
        'startDate' : event.startDate,
        'endDate' : event.endDate,
        'startTime' : event.startTime,
        'endTime' : event.endTime,
        'nGuest' : event.nGuest,
        'desc' : event.desc,
        'TicketPrice' : event.TicketPrice,

    }
    frm = CreateEventFrm(initial=ints)
    context = {
        'form' : frm,
        'venue' : venue,
    }
    if request.method == 'POST':
        try:
            frm = CreateEventFrm(request.POST,request.FILES)
            vnu = request.POST.get('venue')
            if frm.is_valid():
                    venueX = Venues.objects.get(id = vnu)
                    venueX.availabililty = False
                    venueX.save()
                    frm.save()
                    messages.success(request,'Edited Successfully')
                    frm.clean()
                    return render(request,'main/forms/createEvent.html',context)
        except:
            messages.error(request,'Failed to submit')
            return render(request,'main/forms/createEvent.html',context)
    else:
        
        return render(request,'main/forms/createEvent.html',context)



@unauthenticated_user
def loginR(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email = email, password = password)

        if user is None:
            messages.error(request,'Provided email or password is incorrect')
            return render(request,'authentication/login.html')

        if not user.is_emailVerified:
                messages.error(request,f'Email is not verified please check your {email} inbox')
                return render(request,'authentication/login.html')


        if user is not None:
            login(request,user)
            messages.success(request,'Logged In Successfully')
            return redirect('home')

        else:
            messages.error(request,'Invalid Credentials')
            return render(request,'authentication/login.html')

    else:
        return render(request,'authentication/login.html')

@unauthenticated_user
def registerR(request):


    if request.method == 'POST':

        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')

        if email == "" or name == "" or password == "":
            messages.error(request,"Please provide all the details for registration")
            return render(request,'authentication/register.html')
        
        if len(password)<6:
            messages.error(request,"Password length should be more than 6 characters")
            return render(request,'authentication/register.html')

        if UserAccount.objects.filter(email=email).exists():
            messages.warning(request,'User with this email already exists')
            return render(request,'authentication/register.html')
        else:
           
            myuser = UserAccount.objects.create_user(email, name, password)
            myuser.save()
            newUser = UserAccount.objects.get(email = email)
            group = Group.objects.get(name='Users')
            newUser.groups.add(group)
            send_action_email(myuser,request)
            messages.success(request,f'We have sent you an email on {email} check your inbox')
            return redirect('loginR')

    else:
        return render(request,'authentication/register.html')



def logoutR(request):
    logout(request)
    messages.success(request,'Logged Out Successfully')
    return redirect('loginR')


@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Users'])
def confrm(request,slug):
    eve = CreatEvent.objects.get(slug = slug)
    eve.status = True
    eve.save()
    messages.success(request,'Ready for payment')
    return redirect('eventCrude')

@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Users'])
def payFor(request,slug):


    try:


        eventX = CreatEvent.objects.get(slug = slug)
        eventX.payDone = True
        rcpt = Receipt(
            rcptFor = request.user,
            event = eventX,
            status = True
        )
        rcpt.save()
        eventX.save()
        messages.success(request,'Payment Successfull')
        return redirect('eventCrude')
    except:
        messages.error(request,'Failed to generate receipt')
        return redirect('eventCrude')


@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Users'])
def getStatus(request,slug):

    eventX = CreatEvent.objects.get(slug = slug)
    rcpt = Receipt.objects.get(event = eventX)
    context = {
        'event' : eventX,
        'rcpt' : rcpt,
    }

    return render(request,'main/crud/receipt.html',context)
    

# @login_required(login_url='/login/')
# @allowed_users(allowed_roles=['Users'])
# def availaibility(request,slug):

#     if request.method == 'POST':


#         venueF = Venues.objects.get(slug = slug)
#         event = CreatEvent.objects.filter(venue = venueF)
#         dt = request.POST.get('avail')
#         print(f'----------------------{dt}---------------')
#         venueF.srchDate = dt
#         venueF.save()
#         avilb = True
#         for x in event:
#             if x.startDate.strftime("%Y-%m-%d") == dt:
#                 avilb = False
#         if  not avilb:
#             venueF.availabililty = False
#             venueF.save()
#             return redirect('/venue/'+slug)
        
#         else:

#             venueF.availabililty = True
#             venueF.save()
       
#             return redirect('/venue/'+slug)
#     else :
#         return redirect('/venue/'+slug)
    

@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Staff'])
def regClients(request,slug):

    ven = Venues.objects.get(slug = slug)
    eve = CreatEvent.objects.filter(venue = ven)
    context = {
        'ven' : ven,
        'eve' : eve,
    }
    return render(request,'main/crud/registeredClients.html',context)


@login_required(login_url='/login/')
@allowed_users(allowed_roles=['Staff'])
def viewVenues(request):
    ven = Venues.objects.filter(owner = request.user)
    context = {
        'ven' : ven,
    }
    return render(request,'main/crud/addedVenues.html',context)
    

# @login_required(login_url='/login/')
# @allowed_users(allowed_roles=['Staff'])
# def deleteIt(request,slug):

#     eve = CreatEvent.objects.get(slug = slug)
#     ven = eve.venue.slug
#     print(ven)
#     try:
#         eve.delete()
#         messages.success(request,'Event successfully cancelled')
#         return redirect('/regClients/'+ven)
#     except:
#         messages.error(request,'Failed to delete')
#         return redirect('/regClients/'+ven)
    
@unauthenticated_user
def stfReg(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')

        if email == "" or name == "" or password == "":
            messages.error(request,"Please provide all the details for registration")
            return render(request,'authentication/register.html')
        
        if len(password)<6:
            messages.error(request,"Password length should be more than 6 characters")
            return render(request,'authentication/register.html')

        if UserAccount.objects.filter(email=email).exists():
            messages.warning(request,'User with this email already exists')
            return render(request,'authentication/register.html')
        else:

            myuser = UserAccount.objects.xUser(email, name, password)
            myuser.save()
            send_action_email(myuser,request)
            group = Group.objects.get(name = 'Staff')
            newUser = UserAccount.objects.get(email = email)
            newUser.groups.add(group)
            messages.success(request,f'We have sent you an email on {email} check your inbox')
            return redirect('loginR')

    else:
        return render(request,'authentication/staffRegister.html')




def sendMsgs(request,slug):

    
    if request.method == 'POST':

        try:

            eve = CreatEvent.objects.get(slug = slug)
            recvr = eve.eveManager
            ven = eve.venue.slug
            msgtext = request.POST.get('msgtext')
            msg2 = f'From : {request.user} \n Dear {recvr}, {msgtext} \n'
            msg = Msgs(
                msgText = msg2,
                recvr = recvr
            )
            msg.save()

            eve.delete()

            messages.success(request,'Event successfully cancelled')
            return redirect('/regClients/'+ven)
        
        except:
            messages.error(request,'Failed to delete')
            return redirect('/regClients/'+ven)


# def checkAlt(request,slug):

#     if request.method == 'GET':

#         dat = request.GET.get('avbl')
#         print(f'---------------------{dat}')
#         avl = Venues.objects.get(slug = slug)
#         print(avl)
#         eve = CreatEvent.objects.filter(venue = avl)
#         print(f'----------------------{eve}-----------------')

#         for x in eve:
#             if x.startDate.strftime("%Y-%m-%d") == dat:
#                 data = {
#                     'availaible' : False
#                 }
#                 print(f'----------------------Trueeeeeee----------------')
#                 return JsonResponse(data)
        
#         data = {
#             'availaible' : True
#         }
#         print(f'----------------------Falseeeeeeeee----------------')
#         return JsonResponse(data)
        
    

def activate_user(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserAccount.objects.get(pk=uid)
    except Exception as e:
        user = None

    if user and generate_token.check_token(user,token):
        user.is_emailVerified = True
        user.save()
        messages.success(request,'Email successfully verified')
        return redirect('home')
    return render(request,'authentication/activateFailed.html',{'user' : user })



class Checkat(View):

    def get(self, request, slug, *args, **kwargs):

        venueF = Venues.objects.get(slug = slug)
        event = CreatEvent.objects.filter(venue = venueF)
        avil = []
        for x in event:
            a = x.startDate.strftime("%Y-%m-%d")
            avil.append(a)
        
        

        return JsonResponse(json.dumps(avil),safe=False)



    
        
