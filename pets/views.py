from rest_framework.views import APIView, status, Request, Response
from .models import Pet
from .serializers import PetSerializer
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
        trait = req.query_params.get("trait", None)
        pets_objects = Pet.objects
        if trait:
            pets_set = pets_objects.filter(traits__name__iexact=trait)
        else:
            pets_set = Pet.objects.all()
        result_page = self.paginate_queryset(pets_set, req, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):
    def get(self, req: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        serializer = PetSerializer(found_pet)
        return Response(serializer.data)

    def delete(self, req: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        found_pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, req: Request, pet_id: int) -> Response:
        try:
            found_pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        serializer = PetSerializer(data=req.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        group = validated_data.pop("group", "")
        if group:
            try:
                group_data = Group.objects.get(scientific_name=group["scientific_name"])
            except Group.DoesNotExist:
                group_data = Group.objects.create(**group)
            found_pet.group = group_data

        traits = validated_data.pop("traits", "")
        if traits:
            found_pet.traits.clear()
            for trait_data in traits:
                try:
                    trait = Trait.objects.get(name__iexact=trait_data["name"])
                except Trait.DoesNotExist:
                    trait = Trait.objects.create(**trait_data)
                found_pet.traits.add(trait)

        for key, value in validated_data.items():
            setattr(found_pet, key, value)
        found_pet.save()

        return Response(PetSerializer(found_pet).data, status.HTTP_200_OK)
