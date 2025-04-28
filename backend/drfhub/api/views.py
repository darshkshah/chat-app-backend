from django.http import JsonResponse
from django.forms.models import  model_to_dict

from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.models import User

# Create your views here.

# ['id', 'password', 'last_login', 'is_superuser', 'first_name', 'last_name', 'username', 'pn_country_code', 'phone_number', 'email', 'bio', 'avatar', 'online_status', 'created_at', 'is_active', 'is_staff']

@api_view(["GET", "POST"])
def api_home(request, *args, **kwargs):
    if request.method == "GET":
        return Response({"detail": '"GET" not allowed no no no'}, status=404)
    model_data = User.objects.all().order_by('?').first()
    data = {}
    if model_data:
        data = model_to_dict(model_data, fields=['id', 'last_login', 'is_superuser', 'first_name', 'last_name', 'username', 'pn_country_code', 'phone_number', 'email', 'bio', 'online_status', 'created_at', 'is_active', 'is_staff'])

    return Response(data)

# def api_home(request, *args, **kwargs):
#     model_data = User.objects.all().order_by('?').first()
#     data = {}
#     if model_data:
#         data = model_to_dict(model_data, fields=['id', 'last_login', 'is_superuser', 'first_name', 'last_name', 'username', 'pn_country_code', 'phone_number', 'email', 'bio', 'online_status', 'created_at', 'is_active', 'is_staff'])

#     return JsonResponse(data)

# def api_home(request, *args, **kwargs):
#     model_data = User.objects.all().order_by('?').first()
#     data = {}
#     if model_data:
        # data["id"] = model_data.id
        # data["first_name"] = model_data.first_name
        # data["last_name"] = model_data.last_name
        # data["phone_number"] = f"{model_data.pn_country_code} {model_data.phone_number}"
        # data["email"] = model_data.email
        # data["bio"] = model_data.bio
        # data["online_status"] = model_data.online_status
        # data["last_login"] = model_data.last_login
        # data["created_at"] = model_data.created_at

    # return JsonResponse(data)


# def api_home(request, *args, **kwargs):
#     print("REQUEST: ")
#     # print(request.scheme)
#     print(request.body)
#     print(request.path)
#     print(request.method)
#     print(request.GET['abc'])
#     print(request.POST)
#     dictionary = dict(request.GET)
#     print(len(list(dictionary.keys())))
#     # print(request.headers)
#     return JsonResponse({"message": "Hi there, this is a Django API Response!!"})
