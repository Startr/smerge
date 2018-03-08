from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.utils.translation import ugettext as _
from .models import ProjectForm, SnapFileForm, SnapFile, Project
from .forms import OpenProjectForm
from xml.etree import ElementTree as ET
import json
from .xmltools import merge
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib import messages
from django.urls import reverse

# Create your views here.

class HomeView(View):
    def get(self, request):
        context = {
        }
        return render(request, 'home.html', context)


class ProjectView(View):
    def get(self, request, proj_id):
        proj = Project.objects.filter(id=proj_id).first()
        if proj is None:
            raise Http404
        files = [obj.as_dict() for obj in SnapFile.objects.filter(project = proj_id)]
        context = {
            'proj_name': proj.name,
            'proj_description': proj.description,
            'proj_id' : proj.id,
            'files': files
        }
        return render(request, 'proj.html', context)


class MergeView(View):
    def get(self, request, proj_id):
        file_ids = request.GET.getlist('file')
        proj = Project.objects.get(id=proj_id)
        files = list(SnapFile.objects.filter(id__in=file_ids, project=proj_id))
        if len(files)>1:

            new_file = SnapFile.create_and_save(project=proj, ancestors=file_ids, file='')
            new_file.file = str(new_file.id) + '.xml'
            new_file.save()

            try:
                file1 = files.pop()
                file2  = files.pop()
                merge(file1= file1.get_media_path(),
                      file2= file2.get_media_path(),
                      output= new_file.get_media_path(),
                      file1_description= file1.description,
                      file2_description= file2.description)
                for file in files:
                    merge(file1= new_file.get_media_path(),
                          file2= file.get_media_path(),
                          output= new_file.get_media_path(),
                          file1_description= file1.description,
                          file2_description= file2.description
                        )
                return JsonResponse(new_file.as_dict())

            except Exception as e:
                print (e)
                new_file.delete()
                return HttpResponse('invalid data ', status=400)

        else:
            return HttpResponse('invalid data ', status=400)



class SyncView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SyncView, self).dispatch(request, *args, **kwargs)

    def post(self, request, proj_id):
        ancestor_id = request.GET.get('ancestor')
        commit_message = str(request.GET.get('message'))
        proj = Project.objects.get(id=proj_id)
        ancestor = list(SnapFile.objects.filter(id=ancestor_id, project=proj_id))

        data = request.body

        new_file = SnapFile.create_and_save(project=proj, ancestors=ancestor, file='', description=commit_message)
        with open(settings.MEDIA_ROOT + '/'  + str(new_file.id) + '.xml', 'wb') as f:
            f.write(data)
        new_file.file = str(new_file.id) + '.xml'
        new_file.save()

        new_file.xml_job()

        new_url = settings.URL + '/sync/'+str(proj.id) + '?ancestor='+str(new_file.id)
        return JsonResponse({'message': _('OK'), 'url': new_url})


class CreateProjectView(View):

    def get(self, request):
        file_form = SnapFileForm()
        proj_form = ProjectForm()
        context = {
            'file_form' : file_form,
            'proj_form' : proj_form

        }
        return render(request, 'create_proj.html', context)

    def post(self, request):
        snap_form = SnapFileForm(request.POST, request.FILES)
        proj_form = ProjectForm(request.POST, request.FILES)
        print(request.FILES)
        if snap_form.is_valid() and proj_form.is_valid():
            # verify xml
            file = request.FILES['file']
            try:
                ET.fromstring(file.read())

            except ET.ParseError:
                messages.warning(request, 'No valid xml.')
                return HttpResponseRedirect(reverse('create_proj'))

            proj_instance = proj_form.save()
            file = SnapFile.create_and_save(file=file, project=proj_instance, description=request.POST['description'])

            file.xml_job()

            return redirect('proj', proj_id=proj_instance.id)

        else:
            messages.warning(request, 'Invalid Data.')
            return HttpResponseRedirect(reverse('create_proj'))


class OpenProjectView(View):
    def get(self, request):
        form = OpenProjectForm()
        context = {
            'form' : form
        }
        return render(request, 'open_proj.html', context)

    def post(self, request):
        form = OpenProjectForm(request.POST)
        if form.is_valid():
            proj_id = request.POST['project']
            if(Project.objects.filter(id = proj_id)):
                return redirect('proj', proj_id=proj_id)
            else:
                messages.warning(request, 'No such project.')
        else:
            messages.warning(request, 'Invalid Data.')

        return HttpResponseRedirect(reverse('open_proj'))