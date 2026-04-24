from django import forms
from .models import PressingService
from users.models import Address   # adapte le chemin si nécessaire

class PressingOrderForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=PressingService.objects.filter(is_active=True),
        label="Service souhaité"
    )
    address = forms.ModelChoiceField(
        queryset=Address.objects.none(),  # sera filtré dynamiquement
        label="Adresse de prise en charge",
        required=True
    )
    garment_description = forms.CharField(
        max_length=200,
        label="Description du vêtement"
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Quantité"
    )
    weight = forms.DecimalField(
        required=False,
        label="Poids estimé (kg)",
        help_text="Pour les services facturés au poids"
    )
    scheduled_date = forms.DateTimeField(
        required=False,
        label="Date souhaitée",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    delivery_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        label="Adresse de livraison",
        required=False
    )
    note = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Note / Précisions"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtre les adresses de l'utilisateur
            self.fields['address'].queryset = user.addresses.all()
            self.fields['delivery_address'].queryset = user.addresses.all()