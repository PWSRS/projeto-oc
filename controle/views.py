from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from .models import Individuo
from .serializers import IndividuoSerializer, OrcrimSerializer
from django.http import JsonResponse
from django.conf import settings
import os
from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.urls import reverse_lazy
from .models import (
    Individuo,
    Orcrim,
    CasaPrisional,
    Pavilhao,
    Galeria,
    Cela,
    Alojamento,
)
from .forms import IndividuoForm, OrcrimForm, CasaPrisionalForm, CadastroUsuarioForm


# View para página inicial
@login_required
def home(request):
    return render(request, "home.html")


def registro(request):
    if request.method == "POST":
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            # Chamamos o save(commit=False) para aplicar a trava de segurança
            user = form.save(commit=False)

            # O username já é definido no form.save(), então focamos na trava:
            user.is_active = False  # 🔒 Bloqueado até aprovação manual

            user.save()

            # Mensagem de orientação para o agente
            messages.warning(
                request,
                "Solicitação enviada! Seu acesso passará por análise técnica. "
                "Aguarde a homologação da ARI para realizar o login.",
            )
            return redirect("login")
    else:
        form = CadastroUsuarioForm()

    return render(request, "registration/registro.html", {"form": form})


# Trava de segurança para apenas administradores acessarem
def e_supervisor(user):
    return user.is_staff


# --- PAINÉIS DE LISTAGEM ---


@user_passes_test(e_supervisor)
def painel_aprovacao(request):
    """Lista apenas quem se cadastrou e ainda não foi aprovado (is_active=False)"""
    usuarios_pendentes = User.objects.filter(is_active=False).order_by("-date_joined")
    return render(
        request, "registration/painel_aprovacao.html", {"usuarios": usuarios_pendentes}
    )


@user_passes_test(e_supervisor)
def listar_usuarios_ativos(request):
    """Lista apenas quem já está liberado no sistema (is_active=True)"""
    usuarios_ativos = User.objects.filter(is_active=True).order_by("-date_joined")
    return render(
        request, "registration/painel_ativos.html", {"usuarios": usuarios_ativos}
    )


# --- AÇÕES PARA NOVOS CADASTROS (PENDENTES) ---


@user_passes_test(e_supervisor)
def aprovar_usuario(request, user_id):
    """Ativa o usuário que estava pendente"""
    usuario = get_object_or_404(User, id=user_id)
    usuario.is_active = True
    usuario.save()
    messages.success(
        request, f"Acesso de {usuario.get_full_name() or usuario.username} aprovado!"
    )
    return redirect("painel_aprovacao")


@user_passes_test(e_supervisor)
def rejeitar_usuario(request, user_id):
    """Exclui o cadastro se não for alguém da organização (Limpeza de banco)"""
    usuario = get_object_or_404(User, id=user_id)
    nome = usuario.username
    usuario.delete()  # Como é um cadastro novo e indevido, removemos logo.
    messages.error(request, f"Solicitação de {nome} rejeitada e removida do banco.")
    return redirect("painel_aprovacao")


# --- AÇÕES PARA USUÁRIOS ATIVOS ---


@user_passes_test(e_supervisor)
def revogar_acesso(request, user_id):
    """Bloqueia o acesso, mas mantém o usuário no banco (is_active=False)"""
    if request.user.id == user_id:
        messages.error(
            request, "Operação negada: Você não pode bloquear seu próprio acesso."
        )
        return redirect("usuarios_ativos")

    usuario = get_object_or_404(User, id=user_id)
    usuario.is_active = False  # Bloqueia, mas não apaga
    usuario.save()
    messages.warning(
        request,
        f"Acesso de {usuario.username} suspenso. Ele agora consta em 'Pendentes'.",
    )
    return redirect("usuarios_ativos")


@user_passes_test(e_supervisor)
def excluir_usuario_ativo(request, user_id):
    """Remove o usuário ativo permanentemente do banco"""
    if request.user.id == user_id:
        messages.error(request, "Você não pode excluir sua própria conta.")
        return redirect("usuarios_ativos")

    usuario = get_object_or_404(User, id=user_id)
    nome = usuario.username
    usuario.delete()
    messages.success(request, f"O registro de {nome} foi excluído permanentemente.")
    return redirect("usuarios_ativos")


# Função para requisitar a página 404.html personalizada
def not_found(request, exception):
    return render(request, "404.html")


# View para a página principal do organograma
def organograma_view(request):
    return render(request, "orcrim/organograma.html", {})


# API View para listar as Orcrims
def orcrim_list(request):
    orcrimes = list(Orcrim.objects.values("id", "nome"))
    return JsonResponse(orcrimes, safe=False)


# API View para listar os indivíduos de uma Orcrim
def individuos_por_orcrim(request, orcrim_id):
    # Busque os indivíduos da Orcrim específica, ordenando-os pelo novo campo.
    # A ordem pode ser importante para a exibição no front-end.
    individuos_qs = Individuo.objects.filter(orcrim_id=orcrim_id).order_by(
        "nivel_orcrim"
    )

    # Prepare os dados para o JSON, incluindo o novo campo 'nivel_orcrim'.
    individuos_data = [
        {
            "id": ind.id,
            "nome": ind.nome,
            "situacao_penal": ind.situacao_penal,
            "alcunha": ind.alcunha,
            "foto": ind.foto.url if ind.foto else None,
            "nivel_orcrim": ind.nivel_orcrim,  # Novo campo adicionado aqui
        }
        for ind in individuos_qs
    ]
    return JsonResponse(individuos_data, safe=False)


# Views para Individuo
class IndividuoListView(ListView):
    model = Individuo
    template_name = "individuo/individuo_list.html"
    context_object_name = "object_list"
    paginate_by = 15  # Paginação: 10 indivíduos por página

    def get_queryset(self):
        # 1. Obtém o queryset base (todos os indivíduos)
        queryset = super().get_queryset()

        # 2. Obtém o termo de busca e remove espaços extras (trim)
        query = self.request.GET.get("q")

        # 3. Limpa a query e só continua se houver algo para buscar
        if query:
            # Remove espaços no início e fim e converte para string
            cleaned_query = str(query).strip()
        else:
            cleaned_query = None

        # 4. Se a query limpa tiver conteúdo, aplica o filtro
        if cleaned_query:
            # Filtra onde o 'nome' OU a 'alcunha' contêm o termo (case-insensitive)
            queryset = queryset.filter(
                Q(nome__icontains=cleaned_query) | Q(alcunha__icontains=cleaned_query)
            ).distinct()

        # Se cleaned_query for None ou "", ele retorna o queryset completo.
        return queryset


class IndividuoCreateView(CreateView):
    model = Individuo
    form_class = IndividuoForm
    template_name = "individuo/individuo_form.html"
    success_url = reverse_lazy("individuo_list")


class IndividuoUpdateView(UpdateView):
    model = Individuo
    form_class = IndividuoForm
    template_name = "individuo/individuo_form.html"
    success_url = reverse_lazy("individuo_list")


class IndividuoDeleteView(DeleteView):
    model = Individuo
    template_name = "individuo/individuo_confirm_delete.html"
    success_url = reverse_lazy("individuo_list")


class IndividuoDetailView(DetailView):
    model = Individuo
    template_name = "individuo/individuo_detail.html"
    context_object_name = "individuo"


# Views para Orcrim
class OrcrimListView(ListView):
    model = Orcrim
    template_name = "orcrim/orcrim_list.html"
    paginate_by = 10
    ordering = ["nome"]

    def get_queryset(self):
        # 1. Começamos com o queryset base (todos os registros)
        queryset = super().get_queryset()

        # 2. Mantemos sua lógica de contagem de indivíduos
        queryset = queryset.annotate(total_individuos=Count("individuo"))

        # 3. Capturamos o que o usuário digitou no campo 'q' do template
        query = self.request.GET.get("q")

        # 4. Se houver algo digitado, filtramos por Nome ou Sigla
        if query:
            queryset = queryset.filter(
                Q(nome__icontains=query) | Q(sigla__icontains=query)
            )

        return queryset


class OrcrimCreateView(CreateView):
    model = Orcrim
    form_class = OrcrimForm
    template_name = "orcrim/orcrim_form.html"
    success_url = reverse_lazy("orcrim_list")


class OrcrimUpdateView(UpdateView):
    model = Orcrim
    form_class = OrcrimForm
    template_name = "orcrim/orcrim_form.html"
    success_url = reverse_lazy("orcrim_list")


class OrcrimDeleteView(DeleteView):
    model = Orcrim
    template_name = "orcrim/orcrim_confirm_delete.html"
    success_url = reverse_lazy("orcrim_list")


# Views para Casa Prisional
class CasaPrisionalListView(ListView):
    model = CasaPrisional
    template_name = "casaprisional/casaprisional_list.html"


class CasaPrisionalCreateView(CreateView):
    model = CasaPrisional
    form_class = CasaPrisionalForm
    template_name = "casaprisional/casaprisional_form.html"
    success_url = reverse_lazy("casaprisional_list")


class CasaPrisionalUpdateView(UpdateView):
    model = CasaPrisional
    form_class = CasaPrisionalForm
    template_name = "casaprisional/casaprisional_form.html"
    success_url = reverse_lazy("casaprisional_list")


class CasaPrisionalDeleteView(DeleteView):
    model = CasaPrisional
    template_name = "casaprisional/casaprisional_confirm_delete.html"
    success_url = reverse_lazy("casaprisional_list")


def carregar_pavilhoes(request):
    casa_id = request.GET.get("casa_id")
    pavilhoes = Pavilhao.objects.filter(casa_prisional_id=casa_id).values("id", "nome")
    return JsonResponse(list(pavilhoes), safe=False)


def carregar_galerias(request):
    pavilhao_id = request.GET.get("pavilhao_id")
    casa_id = request.GET.get("casa_id")

    if pavilhao_id:
        galerias = Galeria.objects.filter(pavilhao_id=pavilhao_id)
    elif casa_id:
        galerias = Galeria.objects.filter(casa_prisional_id=casa_id)
    else:
        galerias = Galeria.objects.none()
    return JsonResponse(list(galerias.values("id", "nome")), safe=False)


def carregar_celas(request):
    galeria_id = request.GET.get("galeria_id")
    casa_id = request.GET.get("casa_id")

    if galeria_id:
        celas = Cela.objects.filter(galeria_id=galeria_id)
    elif casa_id:
        celas = Cela.objects.filter(casa_prisional_id=casa_id)
    else:
        celas = Cela.objects.none()

    return JsonResponse(list(celas.values("id", "numero")), safe=False)


def carregar_alojamentos(request):
    cela_id = request.GET.get("cela_id")
    casa_id = request.GET.get("casa_id")
    print(f"Chamando carregar_alojamentos: cela_id={cela_id}, casa_id={casa_id}")
    try:
        if cela_id:
            alojamentos = Alojamento.objects.filter(cela_id=cela_id)
        elif casa_id:
            alojamentos = Alojamento.objects.filter(casa_prisional_id=casa_id)
        else:
            alojamentos = Alojamento.objects.none()
        print(f"Alojamentos encontrados: {alojamentos.count()}")
        data = [
            {"id": a.id, "nome": a.nome if a.nome else "Alojamento sem nome"}
            for a in alojamentos
        ]
        print(f"Dados serializados: {data}")
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Erro em carregar_alojamentos: {str(e)}")
        return JsonResponse(
            {"error": f"Erro ao carregar alojamentos: {str(e)}"}, status=500
        )


def tipo_estrutura_view(request):
    casa_id = request.GET.get("casa_id")
    casa = CasaPrisional.objects.filter(id=casa_id).first()
    return JsonResponse({"tipo_estrutura": casa.tipo_estrutura if casa else "completa"})


def listar_por_galeria(request, galeria_id):
    galeria = Galeria.objects.get(id=galeria_id)
    alojamentos = Alojamento.objects.filter(cela__galeria=galeria)
    individuos = Individuo.objects.filter(alojamento__in=alojamentos)

    context = {
        "galeria": galeria,
        "individuos": individuos,
    }
    return render(request, "individuo/individuo_por_galeria.html", context)


from django.db.models import Prefetch  # Importe o Prefetch


def selecionar_presidio(request):
    # Definimos como as galerias devem ser carregadas
    prefetch_galerias = Prefetch(
        "galeria_set",
        queryset=Galeria.objects.select_related("pavilhao")  # Removido "orcrim" daqui
        .prefetch_related("orcrims")  # Adicionado para carregar as múltiplas Orcrims
        .annotate(total_pessoas=Count("individuo"))
        .order_by("pavilhao__nome", "nome"),
    )

    presidios = (
        CasaPrisional.objects.prefetch_related(
            prefetch_galerias, "galeria_set__alojamento_set"
        )
        .annotate(total_geral=Count("galeria__individuo"))
        .all()
    )

    context = {
        "presidios": presidios,
    }
    return render(request, "individuo/selecionar_presidio.html", context)


def listar_detentos_por_galeria(request, galeria_id):
    galeria = get_object_or_404(Galeria, id=galeria_id)
    # Adicionado .order_by('nome') para a lista de detentos não vir bagunçada
    detentos = Individuo.objects.filter(galeria=galeria).order_by("nome")

    context = {
        "galeria": galeria,
        "detentos": detentos,
    }
    return render(request, "individuo/listar_detentos.html", context)


def gerar_pdf_individuo(request, pk):
    individuo = get_object_or_404(Individuo, pk=pk)

    # Renderiza o HTML
    html_string = render_to_string(
        "pdf_individuo.html",
        {
            "individuo": individuo,
            "request": request,  # Passar o request ajuda a resolver URLs
        },
    )

    # O segredo para fotos no Windows/Pycharm é o base_url
    html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="Ficha_{individuo.nome}.pdf"'
    return response


def orcrim_individuos_list(request, pk):
    orcrim = get_object_or_404(Orcrim, pk=pk)
    # Supondo que o campo no model Individuo se chame 'orcrim'
    individuos = Individuo.objects.filter(orcrim=orcrim).select_related(
        "casa_prisional", "galeria"
    )

    return render(
        request,
        "orcrim/orcrim_individuos.html",
        {  # Mude de 'controle/' para 'orcrim/'
            "orcrim": orcrim,
            "individuos": individuos,
        },
    )

def lista_liderancas(request):
    # Filtramos quem não é "sem_expressao"
    # Assumindo que NIVEL_CHOICES tem 'lideranca', 'frente', etc.
    liderancas = (
        Individuo.objects.exclude(nivel_orcrim="sem_expressao")
        .select_related("orcrim", "casa_prisional", "pavilhao", "galeria")
        .order_by("nome")
    )

    context = {
        "liderancas": liderancas,
        "total": liderancas.count(),
    }
    return render(request, "orcrim/liderancas.html", context)


def busca_por_cela(request):
    # Pega todos os presídios para o primeiro select
    casas = CasaPrisional.objects.all()

    # Captura os filtros da URL (via GET)
    casa_id = request.GET.get("casa_prisional")
    pavilhao_id = request.GET.get("pavilhao")
    galeria_id = request.GET.get("galeria")
    cela_id = request.GET.get("cela")

    # Query inicial (vazia ou todos, dependendo da sua preferência)
    # Aqui vamos começar vazia para só mostrar ao filtrar
    detentos = Individuo.objects.none()

    if casa_id:
        detentos = Individuo.objects.all()
        detentos = detentos.filter(casa_prisional_id=casa_id)

        if pavilhao_id:
            detentos = detentos.filter(pavilhao_id=pavilhao_id)
        if galeria_id:
            detentos = detentos.filter(galeria_id=galeria_id)
        if cela_id:
            detentos = detentos.filter(cela_id=cela_id)

    context = {
        "casas": casas,
        "detentos": detentos.select_related(
            "orcrim", "casa_prisional", "galeria", "cela"
        ),
    }
    return render(request, "orcrim/busca_por_cela.html", context)


def dashboard_estatistico(request):
    total_geral = Individuo.objects.count()

    # --- 1. DADOS PARA O GRÁFICO DE BARRAS (ORCRIMS GERAL) ---
    stats_orcrim = (
        Orcrim.objects.annotate(total=Count("individuo"))
        .filter(total__gt=0)
        .order_by("-total")
    )

    # --- 2. DADOS PARA O GRÁFICO DE PIZZA (REGIMES GERAL) ---
    stats_regime = (
        Individuo.objects.values("regime")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # --- 3. DADOS PARA A TABELA (DOMÍNIO POR GALERIA) ---
    galerias = Galeria.objects.annotate(total_presos=Count("individuo")).filter(
        total_presos__gt=0
    )

    dados_galerias = []
    for gal in galerias:
        contagem_orcrim = (
            Individuo.objects.filter(galeria=gal)
            .values("orcrim__nome")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        predominante = contagem_orcrim[0] if contagem_orcrim else None

        if predominante and gal.total_presos > 0:
            porcentagem_dominio = (predominante["total"] / gal.total_presos) * 100
            sigla_dominante = (
                predominante["orcrim__nome"] if predominante["orcrim__nome"] else "S/F"
            )
        else:
            porcentagem_dominio = 0
            sigla_dominante = "N/A"

        # --- LÓGICA DE UNIDADE ADAPTATIVA ---
        sigla_unidade = "S/U"

        if gal.pavilhao and gal.pavilhao.casa_prisional:
            # Caso padrão: Galeria vinculada a Pavilhão que tem Casa Prisional
            sigla_unidade = gal.pavilhao.casa_prisional.sigla
        elif hasattr(gal, "casa_prisional") and gal.casa_prisional:
            # Caso direto: Se você adicionou FK de CasaPrisional direto na Galeria
            sigla_unidade = gal.casa_prisional.sigla

        # Se for o caso específico de Pelotas e estiver vindo vazio,
        # você pode até forçar uma busca por nome ou deixar o S/U para identificar erros de cadastro.

        dados_galerias.append(
            {
                "nome": f"{sigla_unidade} - {gal.nome}",
                "total": gal.total_presos,
                "dominio_sigla": sigla_dominante,
                "porcentagem": porcentagem_dominio,
            }
        )

    context = {
        "stats_orcrim": stats_orcrim,
        "stats_regime": stats_regime,
        "dados_galerias": dados_galerias,
        "total_geral": total_geral,
    }

    return render(request, "orcrim/dashboard.html", context)
