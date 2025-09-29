from rest_framework import serializers
from .models import Individuo, Orcrim


class IndividuoSerializer(serializers.ModelSerializer):
    lider_nome = serializers.CharField(source="lider.nome", read_only=True)
    # Retorna o ID do líder para criar a hierarquia no front-end
    lider_id = serializers.PrimaryKeyRelatedField(source="lider", read_only=True)

    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Individuo
        fields = [
            "id",
            "nome",
            "alcunha",
            "situacao_penal",
            "foto",
            "lider",
            "lider_nome",
            "foto",
        ]

    def get_foto_url(self, obj):
        request = self.context.get("request")
        if obj.foto and hasattr(obj.foto, "url"):
            return request.build_absolute_uri(obj.foto.url)
        return None


class OrcrimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orcrim
        # Defina os campos que você quer incluir na resposta da API
        fields = ["id", "nome", "sigla"]
