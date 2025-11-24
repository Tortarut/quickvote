from django import forms

from .models import NotificationRule, Complaint


class NotificationRuleForm(forms.ModelForm):
    """Форма создания правила уведомления. Фильтрует опросы по автору."""
    class Meta:
        model = NotificationRule
        fields = ("survey", "threshold", "email")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["survey"].queryset = NotificationRule._meta.get_field("survey").remote_field.model.objects.filter(author=user)


class ComplaintForm(forms.ModelForm):
    """Форма отправки жалобы на опрос."""
    class Meta:
        model = Complaint
        fields = ("survey", "text")

