from django import forms
from . models import Account, UserProfile, Address

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Enter Password',
        'class': 'form-control',
                }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirm Password',  
         }))
    class Meta:
        model=Account
        fields = {'first_name', 'last_name', 'phone_number','email','password'}

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self). __init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Enter first name'  
        self.fields['last_name'].widget.attrs['placeholder']='Enter last name'
        self.fields['phone_number'].widget.attrs['placeholder']='Enter phone Number'
        self.fields['email'].widget.attrs['placeholder']='Enter Email Address'

        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'  

    def clean(self): 
        cleaned_data = super(RegistrationForm, self). clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "password does not match!"
            ) 
    

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self). __init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'  

class UserProfileForm(forms.ModelForm):
    addresses = forms.ModelMultipleChoiceField(
        queryset=Address.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ('addresses', 'profile_picture')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['addresses'].queryset = Address.objects.filter(user=user)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street_address', 'city', 'state', 'country', 'phone_number']