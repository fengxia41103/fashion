#!/usr/bin/python  
# -*- coding: utf-8 -*-  

from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, logout, login
from django.template import RequestContext
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count,Max,Min,Avg

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers
# protect the view with require_POST decorator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.template import loader, Context

# django-crispy-forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# django-filters
from django_filters import FilterSet, BooleanFilter
from django_filters.views import FilterView
import django_filters

# django emails
from django.core.mail import send_mail

# so what
import re,os,os.path,shutil,subprocess, testtools
import random,codecs,unittest,time, tempfile, csv, hashlib
from datetime import datetime as dt
from multiprocessing import Process, Queue
import simplejson as json
import googlemaps
from itertools import groupby
import urllib, lxml.html
from utility import MyUtility

from intern.models import *

###################################################
#
#	Common utilities
#
###################################################
def class_view_decorator(function_decorator):
	"""Convert a function based decorator into a class based decorator usable
	on class based Views.
	
	Can't subclass the `View` as it breaks inheritance (super in particular),
	so we monkey-patch instead.
	"""
	
	def simple_decorator(View):
		View.dispatch = method_decorator(function_decorator)(View.dispatch)
		return View
	
	return simple_decorator

###################################################
#
#	Static views
#
###################################################
class HomeView (TemplateView):
	template_name = 'intern/common/home_with_login_modal.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)

		user_auth_form = AuthenticationForm()
		user_registration_form = UserCreationForm()

		context['registration_form']=user_registration_form
		context['auth_form']=user_auth_form
		return context

###################################################
#
#	User views
#
###################################################
class LoginView(FormView):
	template_name = 'registration/login.html'
	success_url = reverse_lazy('application_list')
	form_class = AuthenticationForm
	def form_valid(self,form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(username=username, password=password)

		if user is not None and user.is_active:
		    login(self.request, user)
		    return super(LoginView, self).form_valid(form)
		else:
		    return self.form_invalid(form)

class LogoutView(TemplateView):
	template_name = 'registration/logged_out.html'
	def get(self,request):
		logout(request)
    	# Redirect to a success page.
		# messages.add_message(request, messages.INFO, 'Thank you for using our service. Hope to see you soon!')
		return HttpResponseRedirect (reverse_lazy('home'))

class UserRegisterView(FormView):
	template_name = 'registration/register_form.html'
	form_class = UserCreationForm
	success_url = reverse_lazy('login')
	def form_valid(self,form):
		user_name = form.cleaned_data['username']
		password = form.cleaned_data['password2']
		if len(User.objects.filter(username = user_name))>0:
			return self.form_invalid(form)
		else:
			user = User.objects.create_user(user_name, '', password)			
			user.save()

			return super(UserRegisterView,self).form_valid(form)

###################################################
#
#	MyApplication views
#
###################################################
class MyApplicationAdd(CreateView):
	model = MyApplication
	template_name = 'intern/common/add_form.html'
	success_url = reverse_lazy('application_list')
	# fields = ['application_id', 'applicant_name','start_date','end_date','status']	

	def form_valid(self, form):
		form.instance.created_by = self.request.user
		return super(CreateView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CreateView, self).get_context_data(**kwargs)
		context['title'] = u'New Application'
		context['list_url'] = self.success_url
		return context

class MyApplicationListFilter (FilterSet):
	class Meta:
		model = MyApplication
		fields = {
				'status':['exact'],
				'applicant_name':['contains'],
				'start_date':['exact'],
				'end_date':['exact'],		
				}

class MyApplicationList (FilterView):
	template_name = 'intern/application/list.html'
	paginate_by = 10
	
	def get_filterset_class(self):
		return MyApplicationListFilter

@class_view_decorator(login_required)
class MyApplicationEdit (UpdateView):
	model = MyApplication
	template_name = 'intern/common/edit_form.html'
	
	def get_success_url(self):
		return reverse_lazy('application_detail', kwargs={'pk':self.get_object().id})
			
	def get_context_data(self, **kwargs):
		context = super(UpdateView, self).get_context_data(**kwargs)
		context['title'] = u'Edit application'
		context['list_url'] = reverse_lazy('application_list')
		return context

@class_view_decorator(login_required)
class MyApplicationDelete (DeleteView):
	model = MyApplication
	template_name = 'intern/common/delete_form.html'
	success_url = reverse_lazy('application_list')

	def get_context_data(self, **kwargs):
		context = super(DeleteView, self).get_context_data(**kwargs)
		context['title'] = u'Delete application'
		context['list_url'] = reverse_lazy('application_list')
		return context		

class MyApplicationDetail(DetailView):
	model = MyApplication
	template_name = 'intern/application/detail.html'
	def get_context_data(self, **kwargs):
		context = super(DetailView, self).get_context_data(**kwargs)
		application = self.get_object()
		context['audits'] = application.mystatusaudit_set.order_by('-created')

		return context

@class_view_decorator(login_required)
class MyApplicationStatusUpdate(TemplateView):
	template_name = ''

	def post(self,request):
		obj_id = request.POST['obj_id']
		application = MyApplication.objects.get(id=int(obj_id))
		application.status = MyStatus.objects.get(status=int(request.POST['status_id']))
		application.save()

		return HttpResponse(json.dumps({'status':'ok'}), 
			content_type='application/javascript')

@class_view_decorator(login_required)
class MyApplicationReminder(DetailView):
	model = MyApplication
	template_name = 'intern/application/reminder_email.html'

	def post(self,request,pk):
		application = self.get_object()
		content = loader.get_template(self.template_name)
		html= content.render(Context({'object':application}))

		send_mail(
			subject = 'Reminder: application %s'%application.application_id, 
			message = '',
			html_message = html, 
			from_email = 'fengxia41103@gmail.com',
			recipient_list = [application.status.contact.email,'nianyizh@hotmail.com'], 
			fail_silently=False)

		return HttpResponse(json.dumps({'status':'ok'}), 
			content_type='application/javascript')

###################################################
#
#	MyStatusAudit views
#
###################################################		
@class_view_decorator(login_required)
class MyStatusAuditDelete (DeleteView):
	model = MyStatusAudit
	template_name = 'intern/common/delete_form.html'
	success_url = reverse_lazy('application_list')

	def get_context_data(self, **kwargs):
		context = super(DeleteView, self).get_context_data(**kwargs)
		context['title'] = u'Delete status audit'
		context['list_url'] = reverse_lazy('application_list')
		return context	
