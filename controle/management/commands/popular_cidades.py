from django.core.management.base import BaseCommand
from controle.models import Cidade


class Command(BaseCommand):
    help = "Limpa e popula a tabela Cidade com valores padrão"

    def handle(self, *args, **kwargs):
        # Defina os valores como uma lista de tuplas, onde cada tupla representa um registro

        valores = [
            ("Charqueadas"),
            ("Jacuí"),
            ("Arroio dos Ratos"),
            ("Canoas"),
            ("Montenegro"),
            ("Sapucaia do Sul"),
            ("Osório"),
            ("Gravataí"),
            ("Taquara"),
            ("Novo Hamburgo"),
            ("São Leopoldo"),
            ("Porto Alegre"),
            ("Guaíba"),
            ("Caxias do Sul"),
            ("Bento Gonçalves"),
            ("Canela"),
            ("Guaporé"),
            ("Nova Prata"),
            ("Vacaria"),
            ("São Francisco de Paula"),
            ("Pelotas"),
            ("Rio Grande"),
            ("Santa Maria"),
            ("São Sepé"),
            ("Santiago"),
            ("Caçapava do Sul"),
            ("Júlio de Castilhos"),
            ("Três Passos"),
            ("Cruz Alta"),
            ("Ijuí"),
            ("Santa Rosa"),
            ("São Luiz Gonzaga"),
            ("Cerro Largo"),
            ("Santo Ângelo"),
            ("Passo Fundo"),
            ("Carazinho"),
            ("Erechim"),
            ("Iraí"),
            ("Getúlio Vargas"),
            ("Lagoa Vermelha"),
            ("Palmeira das Missões"),
            ("Sarandi"),
            ("Frederico Westphalen"),
            ("Soledade"),
            ("Espumoso"),
            ("Santana do Livramento"),
            ("Uruguaiana"),
            ("Itaqui"),
            ("Bagé"),
            ("São Borja"),
            ("Dom Pedrito"),
            ("Rosário do Sul"),
            ("Alegrete"),
            ("Santa Cruz do Sul"),
            ("Venâncio Aires"),
            ("Lageado"),
            ("Cachoeira do Sul"),
            ("Encruzilhada do Sul"),
            ("Arroio do Meio"),
            ("Sobradinho"),
            ("Candelária"),
            ("Encantado"),
            ("Rio Pardo"),
            ("Torres"),
        ]

        # Apaga todos os registros existentes na tabela Indisponibilidade
        self.stdout.write("Apagando todos os registros existentes na tabela Cidade...")
        Cidade.objects.all().delete()
        self.stdout.write("Registros apagados com sucesso.")

        # Insere os valores padrão
        self.stdout.write("Inserindo novos registros...")
        for nome in valores:
            try:
                Cidade.objects.create(
                    nome=nome,
                )
                self.stdout.write(f"Registro '{nome}' criado com sucesso.")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erro ao criar registro '{nome}': {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Tabela Cidade limpa e {len(valores)} registros criados com sucesso."
            )
        )
