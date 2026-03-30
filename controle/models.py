from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Choices para campos específicos
SITUACAO_CHOICES = [
    ("recolhido", "Recolhido"),
    ("recolhido_tornozeleira", "Recolhido - Tornozeleira"),
    ("liberdade", "Liberdade"),
    ("foragido", "Foragido"),
    ("removido", "Removido"),
    ("procurado", "Procurado"),
]

REGIME_CHOICES = [
    ("fechado", "Fechado"),
    ("semiaberto", "Semiaberto"),
    ("aberto", "Aberto"),
    ("provisorio", "Provisório"),
    ("monitorado", "Monitorado"),
    ("sem regime", "Sem Regime"),
]

ORCRIM_ABRANGENCIA_CHOICES = [
    ("ocl", "OCL"),
    ("ocr", "OCR"),
    ("ocn", "OCN"),
    ("oci", "OCI"),
    ("nao_possui", "Não possui"),
]

DELEGACIAS_PENITENCIARIAS_CHOICES = [
    ("1dpr", "1ª DPR"),
    ("2dpr", "2ª DPR"),
    ("3dpr", "3ª DPR"),
    ("4dpr", "4ª DPR"),
    ("5dpr", "5ª DPR"),
    ("6dpr", "6ª DPR"),
    ("7dpr", "7ª DPR"),
    ("8dpr", "8ª DPR"),
    ("9dpr", "9ª DPR"),
    ("10dpr", "10ª DPR"),
    ("unid_esp", "Unidades Especiais"),
]


TIPO_ESTRUTURA_CHOICES = [
    ("completa", "Completa (Pavilhão, Galeria, Cela)"),  # Sem alojamento/módulo
    (
        "intermediaria",
        "Intermediária (Galeria, Cela)",
    ),  # Sem pavilhão, alojamento/módulo
    ("pavilhao", "Pavilhão"),  # Detalhar se necessário
    ("modular", "Módulo"),  # Detalhar se necessário
    ("apenas_alojamento", "Apenas Alojamento"),  # Sem pavilhão/galeria/cela
]

NIVEL_CHOICES = (
    ("lider", "Líder"),
    ("influente", "Influente"),
    ("sem_expressao", "Sem Expressão"),
)


class Cidade(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Cidade")

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"

    def __str__(self):
        return self.nome


class Orcrim(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Orcrim")
    sigla = models.CharField(max_length=30, verbose_name="Sigla", blank=True, null=True)
    area_abrangencia = models.CharField(
        max_length=30,
        choices=ORCRIM_ABRANGENCIA_CHOICES,
        verbose_name="Área de Abrangência",
    )
    logo_orcrim = models.ImageField(
        upload_to="fotos/", blank=True, null=True, verbose_name="Logo da Orcrim"
    )

    class Meta:
        verbose_name = "Orcrim"
        verbose_name_plural = "Orcrims"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class CasaPrisional(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Casa Prisional")
    sigla = models.CharField(max_length=20, verbose_name="Sigla")
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True)
    delegacia_penitenciaria = models.CharField(
        max_length=20,
        choices=DELEGACIAS_PENITENCIARIAS_CHOICES,
        verbose_name="Delegacia Penitenciária",
    )
    tipo_estrutura = models.CharField(
        max_length=100,
        choices=TIPO_ESTRUTURA_CHOICES,
        default="completa",
        verbose_name="Tipo de Estrutura",
    )

    class Meta:
        verbose_name = "Casa Prisional"
        verbose_name_plural = "Casas Prisionais"

    def __str__(self):
        return f"{self.sigla} - {self.nome}"


class Pavilhao(models.Model):
    casa_prisional = models.ForeignKey(CasaPrisional, on_delete=models.CASCADE)
    nome = models.CharField(
        max_length=100, verbose_name="Pavilhão", null=True, blank=True
    )

    class Meta:
        verbose_name = "Pavilhão"
        verbose_name_plural = "Pavilhões"

    # Esta propriedade retorna APENAS o nome do pavilhão (ex: "PAV 1")
    @property
    def nome_curto(self):
        return self.nome if self.nome else "-"

    def __str__(self):
        # Mantém assim para o Admin e selects mostrarem o nome completo
        return f"{self.nome} - {self.casa_prisional.nome}"


class Galeria(models.Model):
    casa_prisional = models.ForeignKey(CasaPrisional, on_delete=models.CASCADE)
    pavilhao = models.ForeignKey(
        Pavilhao, on_delete=models.CASCADE, null=True, blank=True
    )
    nome = models.CharField(
        max_length=100, verbose_name="Galeria", null=True, blank=True
    )
    # Alterado de ForeignKey para ManyToManyField
    orcrims = models.ManyToManyField(
        "Orcrim",
        blank=True,
        verbose_name="Orcrims Relacionadas",
        related_name="galerias",
    )

    class Meta:
        verbose_name = "Galeria"
        verbose_name_plural = "Galerias"

    # Propriedade para retornar apenas o nome limpo no template
    @property
    def nome_curto(self):
        return self.nome if self.nome else "-"

    def __str__(self):
        # Mantém o padrão completo para buscas e Admin
        return f"{self.nome} - {self.casa_prisional.nome}"


class Cela(models.Model):
    casa_prisional = models.ForeignKey(
        CasaPrisional,
        on_delete=models.CASCADE,
    )
    pavilhao = models.ForeignKey(
        Pavilhao, on_delete=models.CASCADE, null=True, blank=True
    )
    galeria = models.ForeignKey(
        Galeria, on_delete=models.CASCADE, null=True, blank=True
    )
    numero = models.CharField(max_length=10, verbose_name="Cela", null=True, blank=True)

    class Meta:
        verbose_name = "Cela"
        verbose_name_plural = "Celas"

    def __str__(self):
        return self.numero


class Alojamento(models.Model):
    casa_prisional = models.ForeignKey(CasaPrisional, on_delete=models.CASCADE)
    pavilhao = models.ForeignKey(
        Pavilhao, on_delete=models.CASCADE, null=True, blank=True
    )
    galeria = models.ForeignKey(
        Galeria, on_delete=models.CASCADE, null=True, blank=True
    )
    cela = models.ForeignKey(Cela, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100, verbose_name="Alojamento", blank=True)
    orcrim = models.ForeignKey(
        "Orcrim",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Orcrim Relacionada",
    )

    class Meta:
        verbose_name = "Alojamento"
        verbose_name_plural = "Alojamentos"

    def __str__(self):
        return self.nome


class Individuo(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome Completo")
    rg_cpf = models.CharField(max_length=14, verbose_name="RG/CPF", unique=True)
    data_nasc = models.DateField()
    alcunha = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Alcunha"
    )
    codigo_detento = models.CharField(
        max_length=8, blank=True, null=True, verbose_name="Cód."
    )
    foto = models.ImageField(
        upload_to="fotos/", blank=True, null=True, verbose_name="Foto"
    )
    situacao_penal = models.CharField(
        max_length=50, choices=SITUACAO_CHOICES, verbose_name="Situação Penal"
    )
    orcrim = models.ForeignKey(
        Orcrim, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Orcrim"
    )
    regime = models.CharField(
        max_length=50, choices=REGIME_CHOICES, null=True, blank=True, verbose_name="Regime"
    )
    casa_prisional = models.ForeignKey(
        CasaPrisional, on_delete=models.SET_NULL, null=True, blank=True
    )
    pavilhao = models.ForeignKey(
        Pavilhao, on_delete=models.SET_NULL, null=True, blank=True
    )
    galeria = models.ForeignKey(
        Galeria, on_delete=models.SET_NULL, null=True, blank=True
    )
    cela = models.ForeignKey(Cela, on_delete=models.SET_NULL, null=True, blank=True)
    alojamento = models.ForeignKey(
        Alojamento, on_delete=models.SET_NULL, null=True, blank=True
    )
    observacao = models.CharField(max_length=150, null=True, blank=True)
    nivel_orcrim = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default="sem_expressao",  # Adicione um valor padrão
        verbose_name="Nível de Hierarquia na Orcrim",
    )
    data_entrada_unidade = models.DateTimeField(
        default=timezone.now,
        blank=True,
        null=True,
        verbose_name="Data de Entrada na Unidade (Real)"
    )

    @property
    def foto_url(self):
        if self.foto and hasattr(self.foto, "url"):
            return self.foto.url
        return "/static/images/default_photo.png"

    class Meta:
        verbose_name = "Indivíduo"
        verbose_name_plural = "Indivíduos"

    def get_situacao_badge_class(self):
        mapping = {
            "recolhido": "bg-danger-subtle text-danger border-danger",
            "foragido": "bg-warning-subtle text-warning border-warning",
            "procurado": "bg-warning-subtle text-warning border-warning",
            "liberdade": "bg-success-subtle text-success border-success",
            "recolhido_tornozeleira": "bg-primary-subtle text-primary border-primary",
            "removido": "bg-secondary-subtle text-secondary border-secondary",
        }
        # Retorna as classes baseadas no valor, ou um padrão caso não encontre
        return mapping.get(self.situacao_penal, "bg-secondary-subtle text-secondary")

    def get_regime_badge_class(self):
        mapping = {
            "fechado": "bg-danger-subtle text-danger border-danger",
            "semiaberto": "bg-warning-subtle text-warning border-warning",
            "provisorio": "bg-info-subtle text-info border-info",
            "aberto": "bg-success-subtle text-success border-success",
            "monitorado": "bg-primary-subtle text-primary border-primary",
            "sem regime": "bg-secondary-subtle text-secondary border-secondary",
        }
        # Retorna as classes baseadas no valor, ou um padrão caso não encontre
        return mapping.get(self.regime, "bg-secondary-subtle text-secondary")

    def get_hierarquia_color_class(self):
        mapping = {
            "lider": "text-danger-tech",  # Vermelho para o topo
            "influente": "text-warning-tech",  # Amarelo para os braços direitos
            "sem_expressao": "text-info-tech",  # Azul para o operacional
        }
        return mapping.get(self.nivel_orcrim, "text-info-tech")
    
    def save(self, *args, **kwargs):
        # Lógica para verificar se é edição
        if self.pk:
            old_instance = Individuo.objects.get(pk=self.pk)
            # Verifica se mudou a localização
            mudou = (
                old_instance.casa_prisional != self.casa_prisional or
                old_instance.pavilhao != self.pavilhao or
                old_instance.galeria != self.galeria or
                old_instance.cela != self.cela
            )
            
            if mudou:
                # Fecha a movimentação anterior
                Movimentacao.objects.filter(
                    individuo=self, 
                    data_saida__isnull=True
                ).update(data_saida=timezone.now())

        # Executa o salvamento real do Indivíduo no banco
        super().save(*args, **kwargs)

        # Cria o histórico inicial ou o novo (após a mudança)
        if not Movimentacao.objects.filter(individuo=self, data_saida__isnull=True).exists():
            Movimentacao.objects.create(
                individuo=self,
                casa_prisional=self.casa_prisional,
                pavilhao=self.pavilhao,
                galeria=self.galeria,
                cela=self.cela,
                alojamento=self.alojamento,
                data_entrada=self.data_entrada_unidade # Usa a data que você digitou!
            )
    def __str__(self):
        return self.nome

class Movimentacao(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name='historico_movimentacoes')
    
    # Copiamos a estrutura que você já tem
    casa_prisional = models.ForeignKey(CasaPrisional, on_delete=models.SET_NULL, null=True)
    pavilhao = models.ForeignKey(Pavilhao, on_delete=models.SET_NULL, null=True, blank=True)
    galeria = models.ForeignKey(Galeria, on_delete=models.SET_NULL, null=True, blank=True)
    cela = models.ForeignKey(Cela, on_delete=models.SET_NULL, null=True, blank=True)
    alojamento = models.ForeignKey(Alojamento, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Os campos de controle de tempo
    # Agora o usuário pode editar, mas o padrão é o momento atual
    data_entrada = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Data de Entrada"
    )
    
    # Campo de auditoria (invisível no formulário, mas salvo no banco)
    data_registro = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data do Registro no Sistema"
    )
    data_saida = models.DateTimeField(verbose_name="Data de Saída", null=True, blank=True)
    
    # Para saber quem fez a movimentação (opcional, mas bom para auditoria)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"
        ordering = ['-data_entrada']

    def __str__(self):
        return f"{self.individuo.nome} - {self.casa_prisional.sigla} ({self.data_entrada})"
