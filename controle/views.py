from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import generics
from .models import Individuo
from .serializers import IndividuoSerializer, OrcrimSerializer
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
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
from .forms import IndividuoForm, OrcrimForm, CasaPrisionalForm


# View para página inicial
def home(request):
    return render(request, "home.html")


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
    paginate_by = 10  # Paginação: 10 orcrims por página


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


# TODO Busca por presídio (listar todos os detentos, com campo de busca por alcunha/nome)


def listar_por_galeria(request, galeria_id):
    galeria = Galeria.objects.get(id=galeria_id)
    alojamentos = Alojamento.objects.filter(cela__galeria=galeria)
    individuos = Individuo.objects.filter(alojamento__in=alojamentos)

    context = {
        "galeria": galeria,
        "individuos": individuos,
    }
    return render(request, "individuo/individuo_por_galeria.html", context)


def selecionar_presidio(request):
    # Lista todos os presídios
    presidios = CasaPrisional.objects.all()
    context = {
        "presidios": presidios,
    }
    return render(request, "individuo/selecionar_presidio.html", context)


def listar_detentos_por_galeria(request, galeria_id):
    # Obtém a galeria ou retorna 404 se não existir
    galeria = get_object_or_404(Galeria, id=galeria_id)
    # Filtra detentos diretamente pela galeria (usando o campo ForeignKey em Individuo)
    detentos = Individuo.objects.filter(galeria=galeria)
    context = {
        "galeria": galeria,
        "detentos": detentos,
    }
    return render(request, "individuo/listar_detentos.html", context)
