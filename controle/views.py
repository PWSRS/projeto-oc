from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.db.models.functions import Coalesce
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
from .forms import UserProfileForm
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
    Movimentacao,
)
from .forms import (
    IndividuoForm,
    OrcrimForm,
    CasaPrisionalForm,
    CadastroUsuarioForm,
    MovimentacaoForm,
)


# View para página inicial
@login_required
def home(request):
    return render(request, "home.html")


@login_required
def perfil_usuario(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect("perfil_usuario")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "registration/perfil.html", {"form": form})


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
    # 1. Prefetch das Galerias (como você já tinha, mas otimizado)
    prefetch_galerias = Prefetch(
        "galeria_set",
        queryset=Galeria.objects.select_related("pavilhao")
        .prefetch_related("orcrims")
        .annotate(total_pessoas=Count("individuo"))
        .order_by("pavilhao__nome", "nome"),
    )

    # 2. Busca dos Presídios
    presidios = (
        CasaPrisional.objects.prefetch_related(
            prefetch_galerias,
            "alojamento_set",  # IMPORTANTE: Carrega os alojamentos diretos da unidade
        )
        # CORREÇÃO DO CONTADOR: Conta todos os indivíduos da unidade,
        # seja de cela ou de alojamento.
        .annotate(total_geral=Count("individuo")).order_by("sigla")
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
            "request": request,
            "user": request.user,  # <--- ADICIONE ESTA LINHA
        },
    )

    # O restante do seu código (WeasyPrint) continua igual
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
    return render(request, "casaprisional/busca_por_cela.html", context)


def dashboard_estatistico(request):
    total_geral = Individuo.objects.count()

    # --- 1. DADOS PARA O GRÁFICO DE BARRAS ---
    stats_orcrim = (
        Orcrim.objects.annotate(total=Count("individuo"))
        .filter(total__gt=0)
        .order_by("-total")
    )

    # --- 2. DADOS PARA O GRÁFICO DE PIZZA ---
    stats_regime = (
        Individuo.objects.values("regime")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # --- 3. DADOS PARA A TABELA (LÓGICA APERFEIÇOADA) ---
    galerias = Galeria.objects.annotate(total_presos=Count("individuo")).filter(
        total_presos__gt=0
    )

    dados_galerias = []
    for gal in galerias:
        # Pegamos a contagem de todas as ORCRIMs nesta galeria
        contagem_orcrim = (
            Individuo.objects.filter(galeria=gal)
            .values("orcrim__nome")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        # Inicializamos variáveis padrão
        sigla_dominante = "N/A"
        porcentagem_dominio = 0
        is_misto = False

        if contagem_orcrim.exists():
            # Pegamos o primeiro lugar
            primeiro = contagem_orcrim[0]

            # Verificamos se existe um segundo lugar para comparar
            if len(contagem_orcrim) > 1:
                segundo = contagem_orcrim[1]

                # SE houver empate exato entre o 1º e o 2º, é MISTO
                if primeiro["total"] == segundo["total"]:
                    sigla_dominante = "MISTO"
                    is_misto = True
                else:
                    sigla_dominante = primeiro["orcrim__nome"] or "S/F"
            else:
                # Se só existe um grupo na galeria, o domínio é absoluto
                sigla_dominante = primeiro["orcrim__nome"] or "S/F"

            # Cálculo da porcentagem baseada no líder (mesmo que seja empate)
            if gal.total_presos > 0:
                porcentagem_dominio = (primeiro["total"] / gal.total_presos) * 100

        # --- LÓGICA DE UNIDADE (MANTIDA) ---
        sigla_unidade = "S/U"
        if gal.pavilhao and gal.pavilhao.casa_prisional:
            sigla_unidade = gal.pavilhao.casa_prisional.sigla
        elif hasattr(gal, "casa_prisional") and gal.casa_prisional:
            sigla_unidade = gal.casa_prisional.sigla

        dados_galerias.append(
            {
                "nome": f"{sigla_unidade} - {gal.nome}",
                "total": gal.total_presos,
                "dominio_sigla": sigla_dominante,
                "porcentagem": porcentagem_dominio,
                "is_misto": is_misto,  # Enviamos essa flag para o template
            }
        )

    context = {
        "stats_orcrim": stats_orcrim,
        "stats_regime": stats_regime,
        "dados_galerias": dados_galerias,
        "total_geral": total_geral,
    }
    return render(request, "orcrim/dashboard.html", context)


def buscar_detento(request):
    query = request.GET.get("q", "").strip()  # .strip() evita erros com espaços vazios
    resultados = Individuo.objects.none()

    if query:
        # 1. Primeiro, buscamos os indivíduos que batem com o nome/vulgo
        alvos = Individuo.objects.filter(
            Q(nome__icontains=query) | Q(alcunha__icontains=query)
        )

        # 2. Pegamos os IDs de onde esses alvos estão
        # Usamos values_list com flat=True para simplificar
        celas_ids = list(alvos.values_list("cela_id", flat=True).exclude(cela_id=None))
        alojamentos_ids = list(
            alvos.values_list("alojamento_id", flat=True).exclude(alojamento_id=None)
        )

        # 3. CONSTRUÇÃO DO RESULTADO:
        # Queremos: Os próprios alvos + quem compartilha a cela + quem compartilha o alojamento
        filtros = Q(
            id__in=alvos.values_list("id", flat=True)
        )  # Inclui os alvos originais sempre

        if celas_ids:
            filtros |= Q(cela_id__in=celas_ids)
        if alojamentos_ids:
            filtros |= Q(alojamento_id__in=alojamentos_ids)

        resultados = (
            Individuo.objects.filter(filtros)
            .select_related(
                "casa_prisional", "pavilhao", "galeria", "cela", "alojamento", "orcrim"
            )
            .order_by("casa_prisional", "cela", "alojamento", "nome")
            .distinct()  # Importante para não repetir nomes se o filtro bater duas vezes
        )

    return render(
        request,
        "casaprisional/busca_individuos.html",
        {"resultados": resultados, "query": query},
    )


def quantidade_individuos_por_orcrim(request):
    # Buscamos a partir do modelo Orcrim (é mais lógico se queremos cards de Orcrim)
    # Isso garante que mesmo Orcrims com ZERO presos apareçam (se você quiser)
    dados = (
        Orcrim.objects.annotate(
            total=Count(
                "individuo"
            )  # 'individuo' é o nome do modelo relacionado em minúsculo
        )
        .filter(total__gt=0)
        .order_by("-total")
    )

    return render(request, "orcrim/quantidade_por_orcrim.html", {"dados": dados})


# TODO View que lista o histórico de movimentações dos detentos,
# mostrando as casas prisionais por onde passaram, as datas e os motivos das
# transferências. Isso pode ser útil para análises de perfil e histórico de cada indivíduo.
def perfil_individuo(request, pk):
    individuo = get_object_or_404(Individuo, pk=pk)
    # Buscamos o histórico ordenado pela data mais recente
    historico = individuo.historico_movimentacoes.all().order_by("-data_entrada")

    return render(
        request,
        "individuo/movimentacoes.html",
        {
            "individuo": individuo,
            "historico": historico,
        },
    )


def editar_movimentacao(request, pk):
    mov = get_object_or_404(Movimentacao, pk=pk)
    if request.method == "POST":
        form = MovimentacaoForm(request.POST, instance=mov)
        if form.is_valid():
            form.save()
            messages.success(request, "Movimentação atualizada!")
            return redirect("perfil_individuo", pk=mov.individuo.pk)
    else:
        form = MovimentacaoForm(instance=mov)

    return render(
        request, "individuo/editar_movimentacao.html", {"form": form, "mov": mov}
    )


def excluir_movimentacao(request, mov_pk):
    mov = get_object_or_404(Movimentacao, pk=mov_pk)
    individuo_id = mov.individuo.pk
    if request.method == "POST":
        mov.delete()
        messages.success(request, "Movimentação removida com sucesso.")
    return redirect("perfil_individuo", pk=individuo_id)


def listar_detentos_por_alojamento(request, alojamento_id):
    # Busca o alojamento ou retorna 404
    alojamento = get_object_or_404(Alojamento, id=alojamento_id)

    # Filtra os detentos vinculados a este alojamento
    detentos = (
        Individuo.objects.filter(alojamento=alojamento)
        .select_related("orcrim", "casa_prisional")
        .order_by("nome")
    )

    context = {
        "alojamento": alojamento,
        "detentos": detentos,
        "titulo": f"ALOJAMENTO: {alojamento.nome}",
    }
    # Reutilizamos o seu template de listagem para manter o padrão
    return render(request, "casaprisional/listar_detentos_alojamento.html", context)


def listar_foragidos_procurados(request):
    # 1. Pega o termo digitado (se não houver, fica None)
    query = request.GET.get("q", "").strip()

    # 2. Filtro base (Sempre traz apenas foragidos e procurados)
    queryset = Individuo.objects.filter(situacao_penal__in=["foragido", "procurado"])

    # 3. Se o usuário digitou algo, filtramos dentro do resultado anterior
    if query:
        queryset = queryset.filter(
            Q(nome__icontains=query)
            | Q(alcunha__icontains=query)
            | Q(codigo_detento__icontains=query)  # Adicionei o código também
        )

    # 4. Otimização de banco de dados
    foragidos = queryset.select_related("orcrim", "casa_prisional", "galeria").order_by(
        "nome"
    )

    return render(
        request,
        "individuo/foragidos_procurados.html",
        {
            "foragidos": foragidos,
            "query": query,  # Enviamos de volta para o input não esvaziar
        },
    )
