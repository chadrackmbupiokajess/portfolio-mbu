# portfolioapp/forms.py
from django import forms
from .models import *

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['email', 'message']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message', 'rows': 5}),
        }

class CommentForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'd-none',
            'id': 'comment-image-upload',
            'accept': 'image/*'
        })
    )
    
    class Meta:
        model = Comment
        fields = ['text', 'image']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control comment-textarea',
                'placeholder': 'Écrivez un commentaire...',
                'rows': 1,
                'maxlength': '5000',
                'data-max-chars': '5000'
            }),
        }
    
    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        image = self.cleaned_data.get('image')
        
        if not text and not image:
            raise forms.ValidationError("Le commentaire ne peut pas être vide.")
        
        if len(text) > 5000:
            raise forms.ValidationError("Le commentaire ne peut pas dépasser 5000 caractères.")
            
        return text
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Vérifier la taille du fichier (max 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if image.size > max_size:
                raise forms.ValidationError("L'image ne doit pas dépasser 5 Mo.")
                
            # Vérifier le type de fichier
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in valid_types:
                raise forms.ValidationError("Type de fichier non pris en charge. Utilisez JPEG, PNG, GIF ou WebP.")
                
        return image

class ReplyForm(CommentForm):
    class Meta(CommentForm.Meta):
        model = Comment  # On utilise le même modèle que Comment
        fields = ['text', 'image']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control reply-textarea',
                'placeholder': 'Répondre au commentaire...',
                'rows': 1,
                'maxlength': '5000',
                'data-max-chars': '5000'
            }),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'full_name', 'bio', 'profile_picture', 'location',
            'date_of_birth', 'education_level', 'sex', 'activities', 'city', 'country', 'civil_status'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'activities': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'position', 'company', 'message', 'photo', 'rating']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre poste'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre entreprise'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre témoignage...', 'rows': 4}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }

class ProjectSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un projet...',
            'id': 'search-input'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="Tous les tags",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + [
            ('en_cours', 'En cours'),
            ('termine', 'Terminé'),
            ('pause', 'En pause'),
            ('archive', 'Archivé')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )