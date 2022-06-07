from rest_framework import serializers

from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'text', 'external_id', 'user_id']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance

    def create(self, validated_data):
        return Post.objects.create(**validated_data)
