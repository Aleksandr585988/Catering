from django import forms


class UploadDishesForm(forms.Form):
    csv_file = forms.FileField()