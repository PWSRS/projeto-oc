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
    lista_liderancas,
    orcrim_individuos_list,
    quantidade_individuos_por_orcrim,
    listar_detentos_por_alojamento,
    listar_foragidos_procurados,
    busca_por_cela,
    buscar_detento,
    organograma_view,
    orcrim_list,
    registro,
    listar_usuarios_ativos,
    excluir_usuario_ativo,
    painel_aprovacao,
    aprovar_usuario,
    rejeitar_usuario,
    revogar_acesso,
    perfil_individuo,
    excluir_movimentacao,
    editar_movimentacao,
)

urlpatterns = [
    # --- DASHBOARD E GERAL ---
    path("dashboard/", views.dashboard_estatistico, name="dashboard"),
    path("organograma/", views.organograma_view, name="organograma"),
    path("selecionar-presidio/", views.selecionar_presidio, name="selecionar_presidio"),
    # --- GESTÃO DE USUÁRIOS E ADMINISTRAÇÃO ---
    path("contas/registro/", views.registro, name="registro"),
    path("painel-aprovacao/", views.painel_aprovacao, name="painel_aprovacao"),
    path("usuarios-ativos/", views.listar_usuarios_ativos, name="usuarios_ativos"),
    path("aprovar/<int:user_id>/", views.aprovar_usuario, name="aprovar_usuario"),
    path("rejeitar/<int:user_id>/", views.rejeitar_usuario, name="rejeitar_usuario"),
    path("revogar/<int:user_id>/", views.revogar_acesso, name="revogar_acesso"),
    path(
        "excluir-ativo/<int:user_id>/",
        views.excluir_usuario_ativo,
        name="excluir_usuario_ativo",
    ),
    # --- INDIVÍDUOS (LISTAGENS E BUSCAS) ---
    path("visualizar_individuos/", IndividuoListView.as_view(), name="individuo_list"),
    path("busca_individuos/", views.buscar_detento, name="buscar_detento"),
    path("busca-por-cela/", views.busca_por_cela, name="busca_por_cela"),
    path(
        "individuos_foragidos_procurados/",
        views.listar_foragidos_procurados,
        name="listar_foragidos_procurados",
    ),
    path(
        "movimentacao/editar/<int:pk>/",
        views.editar_movimentacao,
        name="editar_movimentacao",
    ),
    path(
        "movimentacao/excluir/<int:mov_pk>/",
        views.excluir_movimentacao,
        name="excluir_movimentacao",
    ),
    # --- INDIVÍDUO (DETALHES E AÇÕES) ---
    path("individuo/<int:pk>/", IndividuoDetailView.as_view(), name="individuo_detail"),
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
    path(
        "individuo/<int:pk>/pdf/", views.gerar_pdf_individuo, name="gerar_pdf_individuo"
    ),
    path(
        "individuo/<int:pk>/movimentacoes/",
        views.perfil_individuo,
        name="perfil_individuo",
    ),
    # --- ORGANIZAÇÕES CRIMINOSAS (ORCRIM) ---
    path("visualizar_orcrims/", OrcrimListView.as_view(), name="orcrim_list"),
    path("adicionar_orcrim/", OrcrimCreateView.as_view(), name="orcrim_add"),
    path("editar_orcrim/<int:pk>/", OrcrimUpdateView.as_view(), name="orcrim_edit"),
    path("deletar_orcrim/<int:pk>/", OrcrimDeleteView.as_view(), name="orcrim_delete"),
    path(
        "visualizar_liderancas_orcrims/",
        views.lista_liderancas,
        name="visualizar_liderancas",
    ),
    path(
        "quantidade-individuos-por-orcrim/",
        views.quantidade_individuos_por_orcrim,
        name="quantidade_individuos_por_orcrim",
    ),
    path(
        "orcrim/<int:pk>/individuos/",
        views.orcrim_individuos_list,
        name="orcrim_individuos",
    ),
    # --- CASA PRISIONAL E ESTRUTURAS ---
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
    path(
        "alojamento/<int:alojamento_id>/detentos/",
        views.listar_detentos_por_alojamento,
        name="listar_detentos_por_alojamento",
    ),
    path(
        "galeria/<int:galeria_id>/detentos/",
        views.listar_detentos_por_galeria,
        name="listar_detentos_por_galeria",
    ),
    # --- AJAX E CARREGAMENTO DINÂMICO ---
    path("ajax/pavilhoes/", views.carregar_pavilhoes, name="carregar_pavilhoes"),
    path("ajax/galerias/", views.carregar_galerias, name="carregar_galerias"),
    path("ajax/celas/", views.carregar_celas, name="carregar_celas"),
    path("ajax/alojamentos/", views.carregar_alojamentos, name="carregar_alojamentos"),
    path("ajax/tipo_estrutura/", views.tipo_estrutura_view, name="tipo_estrutura"),
    path("ajax/galerias_por_casa/", views.carregar_galerias, name="galerias_por_casa"),
    path("ajax/celas_por_casa/", views.carregar_celas, name="celas_por_casa"),
    path(
        "ajax/alojamentos_por_casa/",
        views.carregar_alojamentos,
        name="alojamentos_por_casa",
    ),
    # --- API ENDPOINTS ---
    path("api/orcrim/", views.orcrim_list, name="api_orcrim_list"),
    path(
        "api/orcrim/<int:orcrim_id>/individuos/",
        views.individuos_por_orcrim,
        name="individuos_por_orcrim",
    ),
]
