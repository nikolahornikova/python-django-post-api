from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Post API",
        default_version='v1'
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),

    path('', views.Index.as_view(), name='index'),
    path('post/<int:post_id>', views.PostView.as_view()),
    path('post', views.PostView.as_view()),
    path('user/<int:user_id>/posts', views.UserPostView.as_view()),

]
