from django import forms

from shopapp.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    images = forms.ImageField(
        widget=forms.ClearableFileInput(), #attrs={"multiple": True}
    )
# from django.contrib.auth.models import Group
# from django.forms import ModelForm
#
# class GroupForm(ModelForm):
#     class Meta:
#         model = Group
#         fields = ["name"]