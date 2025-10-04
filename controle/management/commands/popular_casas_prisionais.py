from django.core.management.base import BaseCommand
from controle.models import CasaPrisional, Cidade


class Command(BaseCommand):
    help = "Limpa e popula a tabela CasaPrisional com valores padrão"

    def handle(self, *args, **kwargs):
        valores = [
            (
                "Penitenciária de Alta Segurança de Charqueadas",
                "PASC",
                "Charqueadas",
                "unid_esp",  # deve ser o valor da escolha, não o texto
            ),
            (
                "Presídio Regional de Pelotas",
                "PRP",
                "Pelotas",
                "5dpr",  # deve ser o valor da escolha, não o texto
            ),
        ]

        self.stdout.write(
            "Apagando todos os registros existentes na tabela CasaPrisional..."
        )
        CasaPrisional.objects.all().delete()
        self.stdout.write("Registros apagados com sucesso.")

        self.stdout.write("Inserindo novos registros...")
        for nome, sigla, nome_cidade, delegacia_penitenciaria in valores:
            try:
                # cidade_obj armazena todas as cidades ca classe Cidade
                cidade_obj, _ = Cidade.objects.get_or_create(nome=nome_cidade)
                CasaPrisional.objects.create(
                    nome=nome,
                    sigla=sigla,
                    cidade=cidade_obj,
                    delegacia_penitenciaria=delegacia_penitenciaria,
                )
                self.stdout.write(f"Registro '{nome}' criado com sucesso.")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erro ao criar registro '{nome}': {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Tabela CasaPrisional limpa e {len(valores)} registros criados com sucesso."
            )
        )
