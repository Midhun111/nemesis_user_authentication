from django.urls import path

from acoount.views import(

    acoount_view,
    edit_acoount_view,
)

app_name = 'acoount'

urlpatterns = [
	path('<user_id>/', acoount_view, name="view"),
    path('<user_id>/edit/', edit_acoount_view, name="edit"),
]