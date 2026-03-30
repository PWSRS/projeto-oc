import re
from django import forms
from .models import Individuo, Orcrim, CasaPrisional, Cidade, Pavilhao, Alojamento
from django.db.models.signals import post_save
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.core.exceptions import ValidationError


# Obtém o modelo de usuário ativo (geralmente User ou CustomUser)
User = get_user_model()


class CadastroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(
        label="PRIMEIRO NOME",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Seu primeiro nome"}),
    )
    last_name = forms.CharField(
        label="ÚLTIMO NOME",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Seu último nome"}),
    )
    email = forms.EmailField(
        label="E-MAIL INSTITUCIONAL",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "usuario@bm.rs.gov.br"}),
    )

    # 🟢 ADIÇÃO: Campos de senha manuais para controle total no HTML
    password1 = forms.CharField(
        label="SENHA", widget=forms.PasswordInput(attrs={"placeholder": "••••••••"})
    )
    password2 = forms.CharField(
        label="CONFIRMAR", widget=forms.PasswordInput(attrs={"placeholder": "••••••••"})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # 🟢 ADIÇÃO: Inclua password1 e password2 aqui
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields["username"].required = False

        self.fields["email"].help_text = (
            "Obrigatório: utilize seu e-mail institucional @bm.rs.gov.br"
        )

        # Aplica a classe CSS em todos, incluindo as novas senhas
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control shadow-sm"

    # --- VALIDAÇÕES ---

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        # Verifica se as senhas conferem
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("As senhas digitadas não são iguais.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        # Define a senha corretamente usando o método do Django
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        dominio_oficial = "@bm.rs.gov.br"
        if not email.endswith(dominio_oficial):
            raise forms.ValidationError(
                f"Acesso negado. Domínio aceito: {dominio_oficial}."
            )
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_first_name(self):
        nome = self.cleaned_data.get("first_name")
        return nome.upper() if nome else nome

    def clean_last_name(self):
        sobrenome = self.cleaned_data.get("last_name")
        return sobrenome.upper() if sobrenome else sobrenome


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="IDENTIFICADOR",  # Garante que o Django use o termo que queremos
        widget=forms.EmailInput(
            attrs={
                "class": "form-control py-2",  # 'py-2' dá um preenchimento interno melhor
                "placeholder": "usuario@bm.rs.gov.br",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="CHAVE DE ACESSO",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control py-2",
                "placeholder": "••••••••",
                "autocomplete": "current-password",
            }
        ),
    )


class IndividuoForm(forms.ModelForm):

    # MÉTODO DE LIMPEZA E VALIDAÇÃO DO CAMPO RG/CPF
    def clean_rg_cpf(self):
        rg_cpf = self.cleaned_data.get("rg_cpf")

        if rg_cpf:
            # 1. Limpeza garantida no back-end: remove todos os caracteres não-dígitos.
            # Isso transforma "000.000.000-00" em "00000000000" (11 dígitos).
            rg_cpf_limpo = re.sub(r"\D", "", rg_cpf)

            # 2. Verifica a validade do comprimento após a limpeza.
            if len(rg_cpf_limpo) not in [10, 11]:
                raise ValidationError(
                    "O campo RG/CPF deve ter 10 dígitos (para RG) ou 11 dígitos (para CPF)."
                )

            # 3. Retorna o valor limpo (10 ou 11 dígitos) que será salvo no banco.
            return rg_cpf_limpo

        return rg_cpf  # Retorna None/NoneType se o campo for opcional e vazio

    def clean_nome(self):
        # 1. Pega o valor do campo 'nome'
        nome = self.cleaned_data.get("nome")

        if nome:
            # 2. Converte para minúsculas e aplica a capitalização (Title Case)
            nome_formatado = nome.title()
            return nome_formatado

        return nome

    def clean(self):
        cleaned_data = super().clean()
        casa_prisional = cleaned_data.get("casa_prisional")
        pavilhao = cleaned_data.get("pavilhao")
        galeria = cleaned_data.get("galeria")
        cela = cleaned_data.get("cela")
        alojamento = cleaned_data.get("alojamento")

        # Lógica de validação de estrutura (Mantida como estava)
        if casa_prisional:
            tipo = casa_prisional.tipo_estrutura

            if tipo == "completa":
                if not pavilhao or not galeria or not cela:
                    self.add_error(
                        None, "Estrutura completa requer pavilhão, galeria e cela."
                    )
                if alojamento:
                    self.add_error(
                        "alojamento", "Estrutura completa não permite alojamento."
                    )
            elif tipo == "intermediaria":
                if pavilhao:
                    self.add_error(
                        "pavilhao", "Estrutura intermediária não permite pavilhão."
                    )
                if not galeria or not cela:
                    self.add_error(
                        None, "Estrutura intermediária requer galeria e cela."
                    )
            elif tipo == "apenas_alojamento":
                if pavilhao or galeria or cela:
                    self.add_error(
                        None,
                        "Estrutura de apenas alojamento não permite pavilhão, galeria ou cela.",
                    )
                if not alojamento:
                    self.add_error(
                        "alojamento",
                        "Estrutura de apenas alojamento requer alojamento.",
                    )
            # Adicione para 'modular' conforme necessário

        return cleaned_data

    class Meta:
        model = Individuo
        fields = [
            "nome",
            "rg_cpf",
            "data_nasc",
            "codigo_detento",
            "alcunha",
            "foto",
            "situacao_penal",
            "orcrim",
            "regime",
            "casa_prisional",
            "pavilhao",
            "galeria",
            "cela",
            "alojamento",
            "observacao",
            "nivel_orcrim",
            "data_entrada_unidade",
        ]

        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "rg_cpf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    # O pattern do HTML foi relaxado para aceitar a máscara,
                    # mas o Python fará a limpeza final.
                    "pattern": r"[\d\.\-]{10,14}",
                    "title": "Digite 10 dígitos para RG ou 11 para CPF (apenas números, pontos e traços são removidos).",
                }
            ),
            "data_nasc": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"
            ),
            "codigo_detento": forms.TextInput(attrs={"class": "form-control"}),
            "alcunha": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Separe por vírgulas as alcunhas.",
                }
            ),
            "foto": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "situacao_penal": forms.Select(attrs={"class": "form-control"}),
            "orcrim": forms.Select(attrs={"class": "form-control"}),
            "nivel_orcrim": forms.Select(attrs={"class": "form-control"}),
            "regime": forms.Select(attrs={"class": "form-control"}),
            "casa_prisional": forms.Select(attrs={"class": "form-control"}),
            "pavilhao": forms.Select(attrs={"class": "form-control"}),
            "galeria": forms.Select(attrs={"class": "form-control"}),
            "cela": forms.Select(attrs={"class": "form-control"}),
            "alojamento": forms.Select(attrs={"class": "form-control"}),
            "observacao": forms.TextInput(attrs={"class": "form-control"}),
        }


class OrcrimForm(forms.ModelForm):
    class Meta:
        model = Orcrim
        fields = "__all__"
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "sigla": forms.TextInput(attrs={"class": "form-control"}),
            "area_abrangencia": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "logo_orcrim": forms.FileInput(attrs={"class": "form-control"}),
        }


class CasaPrisionalForm(forms.ModelForm):
    class Meta:
        model = CasaPrisional
        fields = "__all__"
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "sigla": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.Select(attrs={"class": "form-control"}),
            "delegacia_penitenciaria": forms.Select(attrs={"class": "form-control"}),
            "tipo_estrutura": forms.Select(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_estrutura = cleaned_data.get("tipo_estrutura")
        # Só valida após salvar, então não verificamos alojamentos aqui
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cidade"].queryset = Cidade.objects.all().order_by("nome")
