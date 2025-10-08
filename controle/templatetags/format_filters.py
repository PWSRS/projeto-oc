from django import template
import re

register = template.Library()


@register.filter
def formatar_cpf_rg(value):
    """
    Formata uma string de 11 dígitos (CPF) ou 10 (RG) para exibição.
    """
    if not value:
        return ""

    # Garante que seja string e remove caracteres não-dígitos, por segurança
    clean_value = str(value).replace(".", "").replace("-", "").strip()

    if len(clean_value) == 11:
        # Formata CPF: 000.000.000-00
        return (
            f"{clean_value[:3]}.{clean_value[3:6]}.{clean_value[6:9]}-{clean_value[9:]}"
        )

    elif len(clean_value) == 10:
        # Formata RG (Exemplo comum: 0.000.000-0)
        # Se o seu padrão de RG for diferente, ajuste esta linha
        return value

    # Retorna o valor original se não for 10 ou 11 dígitos
    return value
