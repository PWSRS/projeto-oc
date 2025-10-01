from django.contrib import admin, messages
from .models import (
    Cidade,
    CasaPrisional,
    Pavilhao,
    Galeria,
    Cela,
    Alojamento,
    Individuo,
    Orcrim,
)


# Admin para Cidade
class CidadeAdmin(admin.ModelAdmin):
    list_display = ["nome"]
    search_fields = ["nome"]


class AlojamentoInline(admin.TabularInline):
    model = Alojamento
    extra = 1  # Um alojamento por padrão
    fields = ["nome", "casa_prisional"]
    can_delete = True


# Admin para Casa Prisional
@admin.register(CasaPrisional)
class CasaPrisionalAdmin(admin.ModelAdmin):
    inlines = [AlojamentoInline]
    list_display = ["nome", "sigla", "tipo_estrutura"]
    list_filter = ["tipo_estrutura", "delegacia_penitenciaria"]
    search_fields = ["nome", "sigla"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Validação pós-salvo para tipo_estrutura = "apenas_alojamento"
        if (
            obj.tipo_estrutura == "apenas_alojamento"
            and not Alojamento.objects.filter(casa_prisional=obj).exists()
        ):
            messages.warning(
                request,
                f"Casa Prisional {obj.nome} com tipo 'Apenas Alojamento' deve ter pelo menos um alojamento associado.",
            )


# Admin para Pavilhão
class PavilhaoAdmin(admin.ModelAdmin):
    list_display = ["nome", "casa_prisional"]
    list_filter = ["casa_prisional"]
    search_fields = ["nome"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["casa_prisional"].required = False
        return form


# Admin para Galeria
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "casa_prisional", "pavilhao"]
    list_filter = ["casa_prisional", "pavilhao"]
    search_fields = ["nome"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["pavilhao"].required = False
        return form


# Admin para Cela
class CelaAdmin(admin.ModelAdmin):
    list_display = ["numero", "casa_prisional", "pavilhao", "galeria"]
    list_filter = ["casa_prisional", "pavilhao", "galeria"]
    search_fields = ["numero"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "pavilhao":
            kwargs["queryset"] = Pavilhao.objects.exclude(
                casa_prisional__tipo_estrutura="sem_pavilhao"
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["pavilhao"].required = False
        form.base_fields["galeria"].required = False
        return form


# Admin para Alojamento
class AlojamentoAdmin(admin.ModelAdmin):
    list_display = ["nome", "casa_prisional", "pavilhao", "galeria", "cela"]
    list_filter = ["casa_prisional", "pavilhao", "galeria", "cela"]
    search_fields = ["nome"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["pavilhao"].required = False
        form.base_fields["galeria"].required = False
        form.base_fields["cela"].required = False
        return form


# Admin para Indivíduo
class IndividuoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "rg_cpf",
        "situacao_penal",
        "orcrim",
        "casa_prisional",
        "regime",
        "data_nasc",
        "nivel_orcrim",
    )
    list_filter = ("situacao_penal", "orcrim", "casa_prisional")
    search_fields = ("nome", "rg_cpf", "codigo_detento")


# Admin para Orcrim
class OrcrimAdmin(admin.ModelAdmin):
    list_display = ("sigla", "nome", "area_abrangencia")
    search_fields = ("nome", "sigla")


# Registro dos modelos com suas respectivas classes Admin
admin.site.register(Cidade, CidadeAdmin)
# Removido: admin.site.register(CasaPrisional, CasaPrisionalAdmin) # Já registrado com @admin.register
admin.site.register(Pavilhao, PavilhaoAdmin)
admin.site.register(Galeria, GaleriaAdmin)
admin.site.register(Cela, CelaAdmin)
admin.site.register(Alojamento, AlojamentoAdmin)  # Corrigido, removido AlojamentoInline
admin.site.register(Individuo, IndividuoAdmin)
admin.site.register(Orcrim, OrcrimAdmin)
