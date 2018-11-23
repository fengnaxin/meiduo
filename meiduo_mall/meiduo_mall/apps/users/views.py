from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializer import CreateUserSerializer


class UsernameCountView(CreateAPIView):
    """CreateAPIView视图"""

    serializer_class = CreateUserSerializer






