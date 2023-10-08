from rest_framework.views import APIView, status, Request, Response
from .models import Pet
from .serializers import PetSerializer

# from groups.serializers import GroupSerializer
from traits.models import Trait
from groups.models import Group
from rest_framework.pagination import PageNumberPagination


class PetView(APIView, PageNumberPagination):
    def post(self, req: Request) -> Response:
        serializer = PetSerializer(data=req.data)
        serializer.is_valid(raise_exception=True)
        traits = serializer.validated_data.pop("traits")
        group = serializer.validated_data.pop("group")

        pet = Pet.objects.create(**serializer.validated_data)

        try:
            group_data = Group.objects.get(scientific_name=group["scientific_name"])
        except Group.DoesNotExist:
            group_data = Group.objects.create(**group)
        pet.group = group_data

        for trait_data in traits:
            try:
                trait = Trait.objects.get(name__iexact=trait_data["name"])
            except Trait.DoesNotExist:
                trait = Trait.objects.create(**trait_data)
            pet.traits.add(trait)

        serializer = PetSerializer(pet)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, req: Request):
        pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets, req, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)
