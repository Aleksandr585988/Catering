from django.core.handlers.wsgi import WSGIRequest
from django.template.response import TemplateResponse
from django import forms


class UploadDishesForm(forms.Form):
    csv_file = forms.FileField()


def import_dishes(request: WSGIRequest, **kwargs):
    if request.method == 'GET':
        form = UploadDishesForm()
        context = {"form": form}

        return TemplateResponse(request, "admin/import_dishes.html", context)
    elif request.method == 'POST':
        breakpoint()
        return
    else:
        raise ValueError(f'Method {request.method} not supported')

