from django import forms
from .models import RewardHistory


class RewardHistoryForm(forms.ModelForm):
    class Meta:
        model = RewardHistory
        exclude = ['user', 'reward', 'bought_at']
        fields = ['reward_sent']

        widgets = {
            'reward_sent': forms.CheckboxInput(
                attrs={'class': 'form-check-input'})
        }

        labels = {
            'reward_sent': 'Reward Sent'
        }
