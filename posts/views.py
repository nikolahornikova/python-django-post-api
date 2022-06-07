import json
from django.http import JsonResponse, HttpResponse
import requests
from rest_framework.views import APIView
from posts.models import Post
from posts.serializers import PostSerializer

EXTERNAL_API_URL = "https://jsonplaceholder.typicode.com"


class Index(APIView):

    def get(self, request, **kwargs):
        return JsonResponse({"message": "Hello, world. You're at the main index."})


class PostView(APIView):
    def get(self, request, **kwargs):
        post_id = kwargs.get("post_id")
        if post_id is None:
            posts = Post.objects.all()
            serializer = PostSerializer(posts, many=True)
            return JsonResponse(serializer.data, safe=False)

        try:
            post = Post.objects.get(id=post_id)
            serializer = PostSerializer(post)
            return JsonResponse(serializer.data)
        except Post.DoesNotExist:
            pass

        try:
            post = Post.objects.get(external_id=post_id)
            serializer = PostSerializer(post)
            return JsonResponse(serializer.data)
        except Post.DoesNotExist:
            if post_exists_in_external_db(post_id):
                new_post_data = retrieve_post_data_from_external_db(post_id)
                serializer = PostSerializer(data=new_post_data)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data)
                return JsonResponse(serializer.errors, status=400)
        return HttpResponse(status=404)

    def delete(self, request, **kwargs):
        post_id = kwargs.get("post_id")
        try:
            posts = Post.objects.get(id=post_id)
            posts.delete()
            return HttpResponse(status=204)
        except Post.DoesNotExist:
            return HttpResponse(status=404)

    def post(self, request, **kwargs):
        if not request.body:
            return HttpResponse(status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        data = {
            "title": body.get("post_title"),
            "text": body.get("post_text"),
            "user_id": body.get("user_id"),
        }

        if data["user_id"] is None:
            return HttpResponse(status=400)

        if user_exists_in_external_db(data["user_id"]):
            serializer = PostSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        return HttpResponse(status=404)

    def put(self, request, **kwargs):
        if not request.body:
            return HttpResponse(status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        post_id = kwargs.get("post_id")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return HttpResponse(status=404)

        data = {
            "title": body.get("post_title") or post.title,
            "text": body.get("post_text") or post.text,
            "user_id": post.user_id,
        }

        serializer = PostSerializer(post, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

        return JsonResponse(serializer.errors, status=400)


class UserPostView(APIView):
    def get(self, request, **kwargs):
        user_id = kwargs.get("user_id")
        posts = Post.objects.filter(user_id=user_id)
        serializer = PostSerializer(posts, many=True)
        return JsonResponse(serializer.data, safe=False)


def retrieve_post_data_from_external_db(post_id):
    try:
        r = requests.get('{}/posts/{}'.format(EXTERNAL_API_URL, post_id))
        external_post = r.json()
        return {
            "title": external_post.get("title"),
            "text": external_post.get("body"),
            "user_id": external_post.get("userId"),
            "external_id": external_post.get("id"),
        }
    except:
        return {}


def user_exists_in_external_db(user_id):
    try:
        r = requests.get('{}/users/{}'.format(EXTERNAL_API_URL, user_id))
        return r.status_code == 200
    except:
        return False


def post_exists_in_external_db(post_id):
    try:
        r = requests.get('{}/posts/{}'.format(EXTERNAL_API_URL, post_id))
        return r.status_code == 200
    except:
        return False
