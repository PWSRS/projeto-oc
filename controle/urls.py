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
)

urlpatterns = [
    # Aprovação pelo admin
    path("painel-aprovacao/", views.painel_aprovacao, name="painel_aprovacao"),
    path("usuarios-ativos/", views.listar_usuarios_ativos, name="usuarios_ativos"),
    # Ações
    path("aprovar/<int:user_id>/", views.aprovar_usuario, name="aprovar_usuario"),
    path(
        "rejeitar/<int:user_id>/", views.rejeitar_usuario, name="rejeitar_usuario"
    ),  # Para novos
    path(
        "revogar/<int:user_id>/", views.revogar_acesso, name="revogar_acesso"
    ),  # Para ativos
    path(
        "excluir-ativo/<int:user_id>/",
        views.excluir_usuario_ativo,
        name="excluir_usuario_ativo",
    ),
    # Cadastro de usuário
    path("contas/registro/", views.registro, name="registro"),
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
    # Rota para gerar o PDF da ficha do alvo
    path(
        "individuo/<int:pk>/pdf/", views.gerar_pdf_individuo, name="gerar_pdf_individuo"
    ),
    # URL Busca de detento
    path("busca_individuos/", views.buscar_detento, name="buscar_detento"),
    # URLs para Orcrim
    path("visualizar_orcrims/", OrcrimListView.as_view(), name="orcrim_list"),
    path("quantidade-individuos-por-orcrim/", views.quantidade_individuos_por_orcrim, name="quantidade_individuos_por_orcrim"),
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
    # URL para lideranças de ocrim
    path(
        "visualizar_liderancas_orcrims/",
        views.lista_liderancas,
        name="visualizar_liderancas",
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
    # URL para listar individuos por cela
    path("busca-por-cela/", views.busca_por_cela, name="busca_por_cela"),
    # URL da API para buscar os indivíduos de uma Orcrim específica
    path(
        "api/orcrim/<int:orcrim_id>/individuos/",
        views.individuos_por_orcrim,
        name="individuos_por_orcrim",
    ),
    # Lista os presos por orcrim
    path(
        "orcrim/<int:pk>/individuos/",
        views.orcrim_individuos_list,
        name="orcrim_individuos",
    ),
    # URL para listar indivíduos por galeria
    path("selecionar-presidio/", views.selecionar_presidio, name="selecionar_presidio"),
    # URL para dashboard
    path("dashboard/", views.dashboard_estatistico, name="dashboard"),
    path(
        "galeria/<int:galeria_id>/detentos/",
        views.listar_detentos_por_galeria,
        name="listar_detentos_por_galeria",
    ),
]
