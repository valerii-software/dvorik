from django import forms

from .models import Group, GroupMember


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'description', 'avatar')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }


class GroupSettingsForm(forms.ModelForm):
    """edit_group form: the basic Group fields PLUS a linked-groups
    multi-select sourced from groups the admin is themselves a member of
    (so they can only recommend groups they actually subscribed to)."""
    linked_groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Привязанные группы',
        help_text='Выводятся в правой колонке как «ссылки». Можно прикрепить группы, в которых вы сами состоите.',
    )

    class Meta:
        model = Group
        fields = ('name', 'description', 'avatar')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }

    def __init__(self, *args, owner=None, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        if owner is not None:
            member_group_ids = list(
                GroupMember.objects.filter(user=owner).values_list('group_id', flat=True)
            )
            qs = Group.objects.filter(id__in=member_group_ids)
            if instance and instance.pk:
                qs = qs.exclude(pk=instance.pk)
            self.fields['linked_groups'].queryset = qs
        if instance and instance.pk:
            self.initial['linked_groups'] = list(
                instance.outgoing_links.values_list('linked_id', flat=True)
            )

    def save_links(self, instance):
        from .models import GroupLink
        new_ids = {g.id for g in self.cleaned_data.get('linked_groups', [])}
        existing = {gl.linked_id: gl for gl in instance.outgoing_links.all()}
        for lid, gl in existing.items():
            if lid not in new_ids:
                gl.delete()
        for pos, lid in enumerate(new_ids - set(existing)):
            GroupLink.objects.create(group=instance, linked_id=lid, position=pos)
