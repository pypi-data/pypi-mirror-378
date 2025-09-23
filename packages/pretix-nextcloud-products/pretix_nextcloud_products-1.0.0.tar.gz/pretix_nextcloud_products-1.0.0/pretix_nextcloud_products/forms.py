from django import forms

from .models import NextcloudProductItem


class NextcloudProductItemForm(forms.ModelForm):

    class Meta:
        model = NextcloudProductItem
        fields = ("nextcloud_path",)
