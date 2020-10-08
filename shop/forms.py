from django import forms
from .models import Order



class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_date'].label = 'Дата получения заказа'

    # first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Михаил'}))
    # last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Иванов'}))
    # phone = forms.CharField()
    # address = forms.CharField()
    # buying_type = forms.CharField()
    # comment = forms.CharField()
    order_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'address', 'buying_type', 'order_date', 'comment'
        )