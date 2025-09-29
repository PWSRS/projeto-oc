from django.urls import path, include
from . import views
from controle.views import (
    IndividuoListView,
    IndividuoCreateView,
    IndividuoUpdateView,
    IndividuoDeleteView,
    IndividuoDetailView,
    OrcrimListView,
    OrcrimCreateView,
    OrcrimUpdateView,
    OrcrimDeleteView,
    CasaPrisionalListView,
    CasaPrisionalCreateView,
    CasaPrisionalUpdateView,
    CasaPrisionalDeleteView,
    individuos_por_orcrim,
    organograma_view,
    orcrim_list,
)

urlpatterns = [
    # URLs para Individuo
    path("visualizar_individuos/", IndividuoListView.as_view(), name="individuo_list"),
    path(
        "individuo/<int:pk>/",
        IndividuoDetailView.as_view(),
        name="individuo_detail",
    ),
    path("adicionar_individuo/", IndividuoCreateView.as_view(), name="individuo_add"),
    path(
        "editar_individuo/<int:pk>/",
        IndividuoUpdateView.as_view(),
        name="individuo_edit",
    ),
    path(
        "deletar_individuo/<int:pk>/",
        IndividuoDeleteView.as_view(),
        name="individuo_delete",
    ),
    # URLs para Orcrim
    path("visualizar_orcrims/", OrcrimListView.as_view(), name="orcrim_list"),
    path("adicionar_orcrim/", OrcrimCreateView.as_view(), name="orcrim_add"),
    path(
        "editar_orcrim/<int:pk>/",
        OrcrimUpdateView.as_view(),
        name="orcrim_edit",
    ),
    path(
        "deletar_orcrim/<int:pk>/",
        OrcrimDeleteView.as_view(),
        name="orcrim_delete",
    ),
    # URLs para Casa Prisional
    path(
        "visualizar_casas_prisionais/",
        CasaPrisionalListView.as_view(),
        name="casaprisional_list",
    ),
    path(
        "adicionar_casa_prisional/",
        CasaPrisionalCreateView.as_view(),
        name="casaprisional_add",
    ),
    path(
        "editar_casa_prisional/<int:pk>/",
        CasaPrisionalUpdateView.as_view(),
        name="casaprisional_edit",
    ),
    path(
        "deletar_casa_prisional/<int:pk>/",
        CasaPrisionalDeleteView.as_view(),
        name="casaprisional_delete",
    ),
    path("ajax/pavilhoes/", views.carregar_pavilhoes, name="carregar_pavilhoes"),
    path("ajax/galerias/", views.carregar_galerias, name="carregar_galerias"),
    path("ajax/celas/", views.carregar_celas, name="carregar_celas"),
    path("ajax/alojamentos/", views.carregar_alojamentos, name="carregar_alojamentos"),
    # AJAX para tipo de estrutura da casa prisional
    path("ajax/tipo_estrutura/", views.tipo_estrutura_view, name="tipo_estrutura"),
    # AJAX para carregar dados diretamente por casa prisional
    path("ajax/galerias_por_casa/", views.carregar_galerias, name="galerias_por_casa"),
    path("ajax/celas_por_casa/", views.carregar_celas, name="celas_por_casa"),
    path(
        "ajax/alojamentos_por_casa/",
        views.carregar_alojamentos,
        name="alojamentos_por_casa",
    ),
    # Organograma
    # URL para a página que exibe o organograma
    path("organograma/", views.organograma_view, name="organograma"),
    # URL da API para listar todas as Orcrims (Organizações Criminosas)
    path("api/orcrim/", views.orcrim_list, name="api_orcrim_list"),
    # URL da API para buscar os indivíduos de uma Orcrim específica
    path(
        "api/orcrim/<int:orcrim_id>/individuos/",
        views.individuos_por_orcrim,
        name="individuos_por_orcrim",
    ),
]
