from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random
from controle.models import (
    Cidade,
    Orcrim,
    CasaPrisional,
    Pavilhao,
    Galeria,
    Cela,
    Individuo,
    SITUACAO_CHOICES,
    REGIME_CHOICES,
    NIVEL_CHOICES,
)


class Command(BaseCommand):
    help = "Popula o banco de dados com dados táticos de teste"

    def gerar_cpf(self):
        return f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO("--- INICIANDO POPULAÇÃO TÁTICA ---"))

        # 1. CRIAR ESTRUTURA BÁSICA (Cidades e Unidades)
        cidade, _ = Cidade.objects.get_or_create(nome="Porto Alegre")

        # Criar Orcrims
        orcrims_dados = [
            ("Bala na Cara", "BNC", "ocr"),
            ("Os Manos", "14.18.12", "ocr"),
            ("Vila Jardim", "VJ", "ocr"),
            ("Anti-Bala", "V7", "ocr"),
            ("Os Taura", "TD5", "ocr"),
        ]
        orcrim_list = []
        for nome, sigla, abr in orcrims_dados:
            o, _ = Orcrim.objects.get_or_create(
                nome=nome, sigla=sigla, area_abrangencia=abr
            )
            orcrim_list.append(o)

        # Criar Casa Prisional de Exemplo
        casa, _ = CasaPrisional.objects.get_or_create(
            nome="Penitenciária Estadual de Charqueadas",
            sigla="PEC II",
            cidade=cidade,
            delegacia_penitenciaria="2dpr",
            tipo_estrutura="completa",
        )

        # Criar Pavilhão, Galeria e Celas
        pav, _ = Pavilhao.objects.get_or_create(casa_prisional=casa, nome="PAVILHÃO 01")
        gal, _ = Galeria.objects.get_or_create(
            casa_prisional=casa, pavilhao=pav, nome="GALERIA A"
        )

        celas = []
        for i in range(1, 11):
            c, _ = Cela.objects.get_or_create(
                casa_prisional=casa, pavilhao=pav, galeria=gal, numero=f"{i:02d}"
            )
            celas.append(c)

        # 2. GERAR INDIVÍDUOS
        nomes = [
            "FABIO",
            "RICARDO",
            "ADRIANO",
            "MARCELO",
            "CRISTIANO",
            "JONATAN",
            "RODRIGO",
            "ALEXANDRE",
        ]
        sobrenomes = [
            "SILVA",
            "SANTOS",
            "OLIVEIRA",
            "SOUZA",
            "PEREIRA",
            "LIMA",
            "COSTA",
            "MACHADO",
        ]
        alcunhas = [
            "DO GÁS",
            "ALEMÃO",
            "MAGRÃO",
            "NEGO",
            "CHINA",
            "PLAYBOY",
            "PROFESSOR",
            "BRUXO",
        ]

        total_criado = 0
        alvos_para_criar = 30  # Altere aqui a quantidade desejada

        for i in range(alvos_para_criar):
            nome_completo = f"{random.choice(nomes)} {random.choice(sobrenomes)} {random.choice(sobrenomes)}"
            cpf_fake = self.gerar_cpf()

            # Evita erro de duplicidade no CPF (campo Unique)
            if Individuo.objects.filter(rg_cpf=cpf_fake).exists():
                continue

            try:
                novo_individuo = Individuo.objects.create(
                    nome=nome_completo,
                    rg_cpf=cpf_fake,
                    data_nasc=date(
                        random.randint(1975, 2005),
                        random.randint(1, 12),
                        random.randint(1, 28),
                    ),
                    alcunha=random.choice(alcunhas) if random.random() > 0.2 else None,
                    situacao_penal=random.choice(SITUACAO_CHOICES)[0],
                    regime=random.choice(REGIME_CHOICES)[0],
                    orcrim=random.choice(orcrim_list),
                    nivel_orcrim=random.choice(NIVEL_CHOICES)[0],
                    casa_prisional=casa,
                    pavilhao=pav,
                    galeria=gal,
                    cela=random.choice(celas),
                    data_entrada_unidade=timezone.now().date()
                    - timedelta(days=random.randint(0, 500)),
                )
                total_criado += 1
                self.stdout.write(
                    f"Inserido: {nome_completo} (Alcunha: {novo_individuo.alcunha})"
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erro ao inserir {nome_completo}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"--- SUCESSO: {total_criado} REGISTROS CRIADOS NO ARI SUL ---"
            )
        )
