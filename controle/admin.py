from django.contrib import admin, messages
from .forms import (
    CelasEmMassaForm,
)  # Importa o formulário que você acabou de me mostrar
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import (
    Cidade,
    CasaPrisional,
    Pavilhao,
    Galeria,
    Cela,
    Alojamento,
    Individuo,
    Orcrim,
    Movimentacao,
)


# --- INLINES ---
class AlojamentoInline(admin.TabularInline):
    model = Alojamento
    extra = 1
    fields = ["nome"]  # Removido casa_prisional pois já está implícito no pai
    can_delete = True


# --- ADMIN CLASSES ---


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = (
        "individuo",
        "casa_prisional",
        "pavilhao",
        "galeria",
        "data_entrada",
        "data_saida",
    )
    list_filter = ("casa_prisional", "data_entrada")
    # Use autocomplete se o volume de dados for alto
    autocomplete_fields = ["individuo"]


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ["nome"]
    search_fields = ["nome"]


@admin.register(CasaPrisional)
class CasaPrisionalAdmin(admin.ModelAdmin):
    inlines = [AlojamentoInline]
    list_display = ["nome", "sigla", "tipo_estrutura"]
    list_filter = ["tipo_estrutura", "delegacia_penitenciaria"]
    search_fields = ["nome", "sigla"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if (
            obj.tipo_estrutura == "apenas_alojamento"
            and not obj.alojamento_set.exists()
        ):
            messages.warning(
                request,
                f"Atenção: {obj.nome} está como 'Apenas Alojamento' mas não possui alojamentos cadastrados.",
            )


@admin.register(Pavilhao)
class PavilhaoAdmin(admin.ModelAdmin):
    list_display = ["nome", "casa_prisional"]
    list_filter = ["casa_prisional"]
    search_fields = ["nome"]


@admin.register(Galeria)
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ["nome", "casa_prisional", "pavilhao", "get_orcrims"]
    list_filter = ["casa_prisional", "pavilhao", "orcrims"]
    search_fields = ["nome"]
    filter_horizontal = ("orcrims",)
    actions = ["gerar_celas_em_massa"]

    # --- ATRIBUTOS DE EXIBIÇÃO ---
    def get_orcrims(self, obj):
        return ", ".join([o.sigla or o.nome for o in obj.orcrims.all()])

    get_orcrims.short_description = "Orcrims Relacionadas"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("orcrims")

    # --- ACTION: GERAR CELAS EM MASSA ---
    @admin.action(description="🔨 Gerar Celas em massa (Seleção Múltipla)")
    def gerar_celas_em_massa(self, request, queryset):
        from django.shortcuts import render, redirect

        # Agora permitimos mais de uma galeria!
        # Apenas validamos se o usuário não esqueceu de selecionar nada.
        if not queryset.exists():
            self.message_user(request, "Nenhuma galeria selecionada.", messages.WARNING)
            return None

        # Se o usuário confirmou o formulário (Clicou no botão "CADASTRAR AGORA")
        if "apply" in request.POST:
            form = CelasEmMassaForm(request.POST)
            if form.is_valid():
                txt_numeros = form.cleaned_data["numeros"]
                total_criado = 0

                # LOOP: Para cada galeria que você marcou o checkbox
                for galeria in queryset:
                    quantidade = self._processar_criacao_celas(galeria, txt_numeros)
                    total_criado += quantidade

                self.message_user(
                    request,
                    f"Sucesso! Foram geradas {total_criado} celas distribuídas em {queryset.count()} galerias.",
                    messages.SUCCESS,
                )
                return redirect("admin:controle_galeria_changelist")

        # Se for o carregamento inicial da página de confirmação
        form = CelasEmMassaForm(
            initial={"_selected_action": request.POST.getlist("_selected_action")}
        )

        return render(
            request,
            "admin/action_confirmation.html",
            {
                "title": "Gerar Celas em Massa (Múltiplas Galerias)",
                "queryset": queryset,  # Aqui o template vai listar todas as galerias que você marcou
                "form": form,
                "action": "gerar_celas_em_massa",
                "opts": self.model._meta,
            },
        )

    # --- MÉTODO AUXILIAR (LÓGICA DE NEGÓCIO) ---
    def _processar_criacao_celas(self, galeria, texto_entrada):
        """Processa a string de entrada e cria as celas no banco."""
        celas_criadas = 0
        partes = [p.strip() for p in texto_entrada.split(",") if p.strip()]

        for parte in partes:
            try:
                # Caso seja intervalo: 1-10
                if "-" in parte:
                    inicio, fim = map(int, parte.split("-"))
                    # Garante que o range funcione mesmo se digitarem invertido (ex: 10-1)
                    passo = 1 if inicio <= fim else -1
                    lista_nums = range(inicio, fim + passo, passo)
                else:
                    # Caso seja número único
                    lista_nums = [int(parte)]

                for num in lista_nums:
                    _, created = Cela.objects.get_or_create(
                        numero=str(num),
                        galeria=galeria,
                        defaults={
                            "casa_prisional": galeria.casa_prisional,
                            "pavilhao": galeria.pavilhao,
                        },
                    )
                    if created:
                        celas_criadas += 1
            except (ValueError, TypeError):
                continue  # Pula entradas inválidas como "abc"

        return celas_criadas


@admin.register(Cela)
class CelaAdmin(admin.ModelAdmin):
    list_display = ["numero", "casa_prisional", "pavilhao", "galeria"]
    list_filter = ["casa_prisional", "pavilhao", "galeria"]
    search_fields = ["numero"]


@admin.register(Alojamento)
class AlojamentoAdmin(admin.ModelAdmin):
    list_display = ["nome", "casa_prisional", "pavilhao", "galeria", "cela"]
    list_filter = ["casa_prisional", "pavilhao"]
    search_fields = ["nome"]


@admin.register(Individuo)
class IndividuoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "rg_cpf",
        "situacao_penal",
        "orcrim",
        "casa_prisional",
        "regime",
    )
    list_filter = ("situacao_penal", "orcrim", "casa_prisional", "regime")
    search_fields = ("nome", "rg_cpf", "codigo_detento")
    # Importante para que MovimentacaoAdmin funcione com autocomplete
    search_fields = ("nome", "rg_cpf", "codigo_detento")


@admin.register(Orcrim)
class OrcrimAdmin(admin.ModelAdmin):
    list_display = ("sigla", "nome", "area_abrangencia")
    search_fields = ("nome", "sigla")
