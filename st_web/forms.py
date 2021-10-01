from django import forms


class ShareLinkForm(forms.Form):
    expiration_date = forms.DateField(required=False)
    visit_limit = forms.IntegerField(required=False)
