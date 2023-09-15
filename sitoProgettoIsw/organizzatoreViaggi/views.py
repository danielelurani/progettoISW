from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, TravelForm, InvitationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Travel, Invitation

# Create your views here.

def logout_user(request):
    logout(request)
    return redirect('login')

def login_view(request):

    if request.user.is_authenticated:
        return redirect('userHomePage')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username = username, password = password)

            if user is not None:
                login(request, user)
                return redirect('/organizzatoreViaggi/userHomePage')
            else:
                messages.info(request, 'Username o password errati!')

        context = {}
        return render(request, 'organizzatoreViaggi/login.html', context)

def signup_view(request):

    if request.user.is_authenticated:
        return redirect('userHomePage')
    else:
        form = CreateUserForm()
 
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')
            else:
                context = {'form': form}
                return render(request, 'organizzatoreViaggi/signup.html', context)

        context = {'form': form}
        return render(request, 'organizzatoreViaggi/signup.html', context)

@login_required(login_url = 'login')
def userHomePage_view(request):

    if request.method == 'POST':
        form = TravelForm(request.POST)
        if form.is_valid():
            travel = form.save(commit=False)
            travel.save()
            travel.participants.add(request.user)
            travel.save()
            return redirect('myTravels')
    else:
        form = TravelForm()

    invites = Invitation.objects.filter(receiver = request.user.email)

    context = {'form': form, 'invites': invites}
    return render(request, 'organizzatoreViaggi/userHomePage.html', context)

"""def processInvitation_view(request, inv_id):

    invitation = Invitation.objects.get(id=inv_id)

    if "accept" in request.POST:

        travel = invitation.travel
        user = request.user

        travel.participants.add(user)

        invitation.state = True
        invitation.save()

        return redirect('myTravels')

    if "decline" in request.POST:
        invitation.delete()
        return redirect('userHomePage')"""

    

@login_required(login_url = 'login')
def detailsTravel_view(request):
    return render(request, 'organizzatoreViaggi/detailsTravel.html')

@login_required(login_url = 'login')
def myTravels_view(request):

    travels = Travel.objects.filter(participants = request.user)
    context = { 'travelsList': travels }
    return render(request, 'organizzatoreViaggi/myTravels.html',context)


@login_required(login_url= 'login')
def changeItinerary_view(request):
    return render(request, 'organizzatoreViaggi/changeItinerary.html')

@login_required(login_url= 'login')
def invite_view(request):

    current_user = request.user

    if request.method == 'POST':
        form = InvitationForm(current_user, request.POST)

        if form.is_valid():
            receiver_email = form.cleaned_data['receiver']
            this_travel = form.cleaned_data['travel']

            invitation = Invitation.objects.create(sender=current_user, receiver=receiver_email, travel=this_travel)
            invitation.save()
            return redirect('invite')
    else:
        form = InvitationForm(current_user)

    context = { 'form': form }
    return render(request, 'organizzatoreViaggi/invite.html', context)
