from django import forms
from .models import Matching

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

class MatchingForm(forms.ModelForm):
    name = forms.TextInput()
    sell_topics = forms.TextInput()
    buy_topics = forms.TextInput()
    city = forms.TextInput()
    study_topics = forms.TextInput()
    email = forms.TextInput()
    sell_price = forms.DecimalField()

    class Meta:
        model = Matching
        fields = [
            'name',
            'sell_topics',
            'buy_topics',
            'city',
            'study_topics',
            'email',
            'sell_price'
        ]
        labels = {
            'name': 'Name',
            'sell_topics':'Selling Book Areas',
            'buy_topics':'Buying Book Areas',
            'city':'City of Residence',
            'study_topics':'Group Study Possibilities',
            'email':'Enter Email',
            'sell_price': 'Selling Price'
        }