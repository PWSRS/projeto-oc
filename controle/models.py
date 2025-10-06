from django.db import models
from django.core.exceptions import ValidationError

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

    def __str__(self):
        return f"{self.nome} - {self.casa_prisional.nome}"


class Galeria(models.Model):
    casa_prisional = models.ForeignKey(CasaPrisional, on_delete=models.CASCADE)
    pavilhao = models.ForeignKey(
        Pavilhao, on_delete=models.CASCADE, null=True, blank=True
    )
    nome = models.CharField(
        max_length=100, verbose_name="Galeria", null=True, blank=True
    )
    orcrim = models.ForeignKey(
        "Orcrim",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Orcrim Relacionada",
    )

    class Meta:
        verbose_name = "Galeria"
        verbose_name_plural = "Galerias"

    def __str__(self):
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
    rg_cpf = models.CharField(max_length=11, verbose_name="RG/CPF", unique=True)
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
        max_length=50, choices=REGIME_CHOICES, verbose_name="Regime"
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

    @property
    def foto_url(self):
        if self.foto and hasattr(self.foto, "url"):
            return self.foto.url
        return "/static/images/default_photo.png"

    class Meta:
        verbose_name = "Indivíduo"
        verbose_name_plural = "Indivíduos"

    def __str__(self):
        return self.nome
