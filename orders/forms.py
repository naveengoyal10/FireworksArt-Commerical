from django import forms
from .models import Order

INDIA_STATES = [
    ('', 'Select State'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
    ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
    ('Chandigarh', 'Chandigarh'),
    ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('Delhi', 'Delhi'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Ladakh', 'Ladakh'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Puducherry', 'Puducherry'),
]

INDIA_CITIES = [
    ('', 'Select City'),
    ('Agra', 'Agra'),
    ('Ahmedabad', 'Ahmedabad'),
    ('Bengaluru', 'Bengaluru'),
    ('Bhopal', 'Bhopal'),
    ('Chandigarh', 'Chandigarh'),
    ('Chennai', 'Chennai'),
    ('Coimbatore', 'Coimbatore'),
    ('Delhi', 'Delhi'),
    ('Hyderabad', 'Hyderabad'),
    ('Jaipur', 'Jaipur'),
    ('Jodhpur', 'Jodhpur'),
    ('Kanpur', 'Kanpur'),
    ('Kochi', 'Kochi'),
    ('Kolkata', 'Kolkata'),
    ('Lucknow', 'Lucknow'),
    ('Mumbai', 'Mumbai'),
    ('Nagpur', 'Nagpur'),
    ('Noida', 'Noida'),
    ('Pune', 'Pune'),
    ('Rajkot', 'Rajkot'),
    ('Surat', 'Surat'),
    ('Thiruvananthapuram', 'Thiruvananthapuram'),
    ('Vadodara', 'Vadodara'),
    ('Visakhapatnam', 'Visakhapatnam'),
]


class CheckoutForm(forms.Form):
    # Customer Info
    full_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )

    # Billing Address
    billing_address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street Address'
        })
    )
    billing_city = forms.ChoiceField(
        choices=INDIA_CITIES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    billing_state = forms.ChoiceField(
        choices=INDIA_STATES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    billing_postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postal Code'
        })
    )
    billing_country = forms.CharField(
        max_length=100,
        required=True,
        initial='India',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country'
        })
    )

    # Shipping Address
    same_as_billing = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'sameAsBilling'
        })
    )
    shipping_address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street Address'
        })
    )
    shipping_city = forms.ChoiceField(
        choices=INDIA_CITIES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    shipping_state = forms.ChoiceField(
        choices=INDIA_STATES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    shipping_postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postal Code'
        })
    )
    shipping_country = forms.CharField(
        max_length=100,
        required=False,
        initial='India',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country'
        })
    )

    # Payment Method
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        same_as_billing = cleaned_data.get('same_as_billing')

        if not same_as_billing:
            if not cleaned_data.get('shipping_address'):
                self.add_error('shipping_address', 'Shipping address is required')
            if not cleaned_data.get('shipping_city'):
                self.add_error('shipping_city', 'Shipping city is required')
            if not cleaned_data.get('shipping_state'):
                self.add_error('shipping_state', 'Shipping state is required')
            if not cleaned_data.get('shipping_postal_code'):
                self.add_error('shipping_postal_code', 'Shipping postal code is required')

        return cleaned_data
