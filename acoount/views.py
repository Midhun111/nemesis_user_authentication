from django.forms.forms import Form
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.conf import settings

from acoount.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from acoount.models import Account



def acoount_search_view(request, *args, **kwargs):
	context = {}
	if request.method == "GET":
		search_query = request.GET.get("q")
		if len(search_query) > 0:
			search_results = Account.objects.filter(email__icontains=search_query).filter(username__icontains=search_query).distinct()
			user = request.user
			accounts = [] # [(account1, True), (account2, False), ...]
			for account in search_results:
				accounts.append((account, False)) # you have no friends yet
			context['accounts'] = accounts
				
	return render(request, "acoount/search_results.html", context)


def register_view(request, *args, **kwargs):
	user = request.user
	if user.is_authenticated: 
		return HttpResponse("You are already authenticated as " + str(user.email))

	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email').lower()
			raw_password = form.cleaned_data.get('password1')
			acoount = authenticate(email=email, password=raw_password)
			login(request, acoount)
			destination = kwargs.get("next")
			if destination:
				return redirect(destination)
			return redirect('home')
		else:
			context['registration_form'] = form

	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'acoount/register.html', context)





def logout_view(request):
	logout(request)
	return redirect("home")


def login_view(request, *args, **kwargs):
	context = {}

	user = request.user
	if user.is_authenticated: 
		return redirect("home")

	destination = get_redirect_if_exists(request)
	print("destination: " + str(destination))

	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)

			if user:
				login(request, user)
				if destination:
					return redirect(destination)
				return redirect("home")

	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form

	return render(request, "acoount/login.html", context)


def get_redirect_if_exists(request):
	redirect = None
	if request.GET:
		if request.GET.get("next"):
			redirect = str(request.GET.get("next"))
	return redirect





def acoount_view(request, *args, **kwargs):
	"""
	- Logic here is kind of tricky
		is_self (boolean)
			is_friend (boolean)
				-1: NO_REQUEST_SENT
				0: THEM_SENT_TO_YOU
				1: YOU_SENT_TO_THEM
	"""
	context = {}
	user_id = kwargs.get("user_id")
	try:
		acoount = Account.objects.get(pk=user_id)
	except:
		return HttpResponse("Something went wrong.")
	if acoount:
		context['id'] = acoount.id
		context['username'] = acoount.username
		context['email'] = acoount.email
		context['profile_image'] = acoount.profile_image.url

		# Define template variables
		is_self = True
		is_friend = False
		user = request.user
		if user.is_authenticated and user != acoount:
			is_self = False
		elif not user.is_authenticated:
			is_self = False
			
		# Set the template variables to the values
		context['is_self'] = is_self
		context['is_friend'] = is_friend
		context['BASE_URL'] = settings.BASE_DIR

		return render(request, "acoount/acoount.html", context)



def edit_acoount_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		return redirect("login")
	user_id = kwargs.get("user_id")
	acoount = Account.objects.get(pk=user_id)
	if acoount.pk != request.user.pk:
		return HttpResponse("You cannot edit someone elses profile.")
	context = {}
	if request.POST:
		form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
		if form.is_valid():
			form.save()
			new_username = form.cleaned_data['username']
			return redirect("acoount:view", user_id=acoount.pk)
		else:
			form = AccountUpdateForm(request.POST, instance=request.user,
				initial={
					"id": acoount.pk,
					"email": acoount.email, 
					"username": acoount.username,
					"profile_image": acoount.profile_image,
				}
			)
			context['form'] = form
	else:
		form = AccountUpdateForm(
			initial={
					"id": acoount.pk,
					"email": acoount.email, 
					"username": acoount.username,
					"profile_image": acoount.profile_image,
				}
			)
		context['form'] = form
	context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
	return render(request, "acoount/edit_account.html", context)




