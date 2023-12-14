# forms.py

from django import forms
from .models import AuctionListing, Bid,Category


class CreateListingForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category'] 
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 8}),  
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateListingForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()

    def save(self, commit=True):
        instance = super(CreateListingForm, self).save(commit=False)
        instance.creator = self.user
        if commit:
            instance.save()
        return instance

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']