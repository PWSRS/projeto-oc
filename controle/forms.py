from django import forms
from .models import Individuo, Orcrim, CasaPrisional, Cidade, Pavilhao, Alojamento
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class IndividuoForm(forms.ModelForm):
    def clean_rg_cpf(self):
        rg_cpf = self.cleaned_data.get("rg_cpf")

        if rg_cpf:
            # 1. Remove qualquer caractere que não seja número
            rg_cpf_numerico = "".join(filter(str.isdigit, rg_cpf))

            # 2. Verifica se o campo tem 10 ou 11 dígitos
            if len(rg_cpf_numerico) not in [10, 11]:
                raise ValidationError(
                    "O campo RG/CPF deve ter 10 dígitos (para RG) ou 11 dígitos (para CPF)."
                )

        return rg_cpf_numerico

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
            "grau_importancia",
            "nivel_orcrim",
        ]

        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "rg_cpf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "pattern": r"[\d]{10,11}",
                    "title": "Digite 10 dígitos para RG ou 11 para CPF (apenas números).",
                }
            ),
            "data_nasc": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"
            ),
            "codigo_detento": forms.TextInput(attrs={"class": "form-control"}),
            "alcunha": forms.TextInput(attrs={"class": "form-control"}),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "situacao_penal": forms.Select(attrs={"class": "form-control"}),
            "orcrim": forms.Select(attrs={"class": "form-control"}),
            "grau_importancia": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "nivel_orcrim": forms.Select(attrs={"class": "form-control"}),
            "regime": forms.Select(attrs={"class": "form-control"}),
            "casa_prisional": forms.Select(attrs={"class": "form-control"}),
            "pavilhao": forms.Select(attrs={"class": "form-control"}),
            "galeria": forms.Select(attrs={"class": "form-control"}),
            "cela": forms.Select(attrs={"class": "form-control"}),
            "alojamento": forms.Select(attrs={"class": "form-control"}),
            "observacao": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        casa_prisional = cleaned_data.get("casa_prisional")
        pavilhao = cleaned_data.get("pavilhao")
        galeria = cleaned_data.get("galeria")
        cela = cleaned_data.get("cela")
        alojamento = cleaned_data.get("alojamento")

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
            "area_atuacao": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
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
