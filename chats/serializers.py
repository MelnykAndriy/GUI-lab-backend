from django.contrib.auth.models import User
from rest_framework import serializers

from chats.models import Message


class MessageSerializer(serializers.ModelSerializer):
    senderId = serializers.IntegerField(source="sender.id", read_only=True)
    receiverId = serializers.IntegerField(source="receiver.id")
    read = serializers.BooleanField(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "senderId", "receiverId", "content", "timestamp", "read"]
        read_only_fields = ["id", "senderId", "timestamp", "read"]


class NewMessageRequestSerializer(serializers.Serializer):
    receiverId = serializers.IntegerField()
    content = serializers.CharField()


class RecentChatSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    lastMessage = MessageSerializer()
    unreadCount = serializers.IntegerField()

    def get_user(self, obj):
        from users.serializers import UserSerializer
        request = self.context.get('request')
        return UserSerializer(obj['user'], context={'request': request}).data
