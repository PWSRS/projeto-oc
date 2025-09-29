import json
from django.core.management.base import BaseCommand
from controle.models import Cidade, CasaPrisional, Pavilhao, Galeria, Cela, Alojamento


class Command(BaseCommand):
    help = "Popula o banco de dados com estrutura prisional a partir de um arquivo JSON"

    def handle(self, *args, **kwargs):
        try:
            with open(
                "controle/management/commands/estrutura_prisional.json",
                "r",
                encoding="utf-8",
            ) as f:
                dados = json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR("Arquivo 'estrutura_prisional.json' não encontrado.")
            )
            return

        cidade_nome = dados["cidade"]
        casa_info = dados["casa_prisional"]
        estrutura = dados["estrutura"]

        cidade, _ = Cidade.objects.get_or_create(nome=cidade_nome)

        casa, _ = CasaPrisional.objects.get_or_create(
            nome=casa_info["nome"],
            sigla=casa_info["sigla"],
            cidade=cidade,
            delegacia_penitenciaria=casa_info["delegacia_penitenciaria"],
        )

        for nome_pavilhao, galerias in estrutura.items():
            pavilhao = Pavilhao.objects.create(casa_prisional=casa, nome=nome_pavilhao)
            for nome_galeria, celas in galerias.items():
                galeria = Galeria.objects.create(
                    casa_prisional=casa, pavilhao=pavilhao, nome=nome_galeria
                )
                for numero_cela, alojamentos in celas.items():
                    cela = Cela.objects.create(
                        casa_prisional=casa,
                        pavilhao=pavilhao,
                        galeria=galeria,
                        numero=numero_cela,
                    )
                    for nome_alojamento in alojamentos:
                        Alojamento.objects.create(
                            casa_prisional=casa,
                            pavilhao=pavilhao,
                            galeria=galeria,
                            cela=cela,
                            nome=nome_alojamento,
                        )

        self.stdout.write(
            self.style.SUCCESS(
                "Estrutura prisional inserida com sucesso no banco de dados."
            )
        )
