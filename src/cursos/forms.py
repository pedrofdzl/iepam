from django import forms


class CourseCreateForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(max_length=500, widget=forms.Textarea())


