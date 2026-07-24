from django import forms
from django.contrib.auth import get_user_model
from .models import Profile, Address
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()

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


def _bootstrap_form_fields(form):
    for name, field in form.fields.items():
        widget = field.widget
        if getattr(widget, 'input_type', None) == 'checkbox':
            continue
        existing = widget.attrs.get('class', '')
        widget.attrs.update({
            'class': ' '.join(filter(None, [existing, 'form-control form-control-lg'])),
        })


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_form_fields(self)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_form_fields(self)


class AddressForm(forms.ModelForm):
    city = forms.ChoiceField(choices=INDIA_CITIES, required=True)
    state = forms.ChoiceField(choices=INDIA_STATES, required=True)

    class Meta:
        model = Address
        fields = ['label', 'line1', 'line2', 'city', 'state', 'postal_code', 'country', 'default']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_form_fields(self)
        self.fields['country'].initial = 'India'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_form_fields(self)
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({'placeholder': 'Enter username or email'})
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({'placeholder': 'Enter password'})


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=150)
    last_name = forms.CharField(required=False, max_length=150)
    email = forms.EmailField(required=True)
    mobile = forms.CharField(required=False, max_length=30, label='Mobile Number')
    terms = forms.BooleanField(required=True, label='I agree to the Terms & Conditions')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'mobile', 'password1', 'password2', 'terms')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            # Create or update profile with mobile/phone
            Profile.objects.update_or_create(user=user, defaults={'phone': self.cleaned_data.get('mobile', '')})
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_form_fields(self)
        if 'terms' in self.fields:
            self.fields['terms'].widget.attrs.update({'class': 'form-check-input'})
