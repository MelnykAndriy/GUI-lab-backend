import threading
import time

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chats.models import Message
from chats.serializers import (MessageSerializer, NewMessageRequestSerializer,
                               RecentChatSerializer)
from users.management.commands.create_bot_users import BOT_EMAILS


def _handle_bot_replies(request, receiver, content):
    # Auto-reply bot logic (testing only)
    if receiver.email in BOT_EMAILS:

        def bot_reply():
            time.sleep(0.5)  # Simulate thinking delay
            reply_content = f"Auto-reply from {receiver.first_name or receiver.username}: I received your message: '{content}'"
            Message.objects.create(
                sender=receiver, 
                receiver=request.user,
                content=reply_content
            )

        threading.Thread(target=bot_reply, daemon=True).start()

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NewMessageRequestSerializer(data=request.data)
        if serializer.is_valid():
            receiver_id = serializer.validated_data["receiverId"]
            content = serializer.validated_data["content"]
            try:
                receiver = User.objects.get(id=receiver_id)
            except User.DoesNotExist:
                return Response(
                    {"code": 404, "message": "Receiver not found"}, status=404
                )
            message = Message.objects.create(
                sender=request.user, receiver=receiver, content=content
            )

            _handle_bot_replies(request, receiver, content)

            return Response(MessageSerializer(message).data, status=201)
        return Response(
            {"code": 400, "message": "Invalid input", "details": serializer.errors},
            status=400,
        )


class ChatMessagesPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "limit"
    max_page_size = 100


class ChatMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userId):
        try:
            other_user = User.objects.get(id=userId)
        except User.DoesNotExist:
            return Response({"code": 404, "message": "User not found"}, status=404)
        messages = Message.objects.filter(
            (
                models.Q(sender=request.user, receiver=other_user)
                | models.Q(sender=other_user, receiver=request.user)
            )
        ).order_by("-timestamp")  # Newest messages first
        paginator = ChatMessagesPagination()
        page = paginator.paginate_queryset(messages, request)
        data = MessageSerializer(page, many=True).data

        pagination_provider = hasattr(paginator, "page") and paginator.page is not None
        pagination = {
            "total": (
                paginator.page.paginator.count if pagination_provider else len(data)
            ),
            "pages": paginator.page.paginator.num_pages if pagination_provider else 1,
            "page": paginator.page.number if pagination_provider else 1,
            "limit": (
                paginator.get_page_size(request) if pagination_provider else len(data)
            ),
        }

        return Response({"messages": data, "pagination": pagination})


class RecentChatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sent = Message.objects.filter(sender=user).values_list("receiver", flat=True)
        received = Message.objects.filter(receiver=user).values_list(
            "sender", flat=True
        )
        chat_user_ids = set(list(sent) + list(received))
        chat_user_ids.discard(user.id)
        chats = []
        for other_id in chat_user_ids:
            try:
                other_user = User.objects.get(id=other_id)
            except User.DoesNotExist:
                continue
            last_msg = (
                Message.objects.filter(
                    (
                        Q(sender=user, receiver=other_user)
                        | Q(sender=other_user, receiver=user)
                    )
                )
                .order_by("-timestamp")
                .first()
            )
            unread_count = Message.objects.filter(
                sender=other_user, receiver=user, read=False
            ).count()  # Only count unread messages
            chats.append(
                {
                    "user": other_user,
                    "lastMessage": last_msg,
                    "unreadCount": unread_count,
                }
            )
        # After building the chats list, sort by lastMessage.timestamp (descending)
        chats.sort(
            key=lambda c: c["lastMessage"].timestamp if c["lastMessage"] else "",
            reverse=True,
        )
        serializer = RecentChatSerializer(
            chats, many=True, context={"request": request}
        )
        # Add 'read' status to lastMessage if present
        for chat, data in zip(chats, serializer.data):
            if chat["lastMessage"]:
                data["lastMessage"]["read"] = chat["lastMessage"].read
        return Response({"chats": serializer.data})


class MarkMessagesAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, userId):
        try:
            other_user = User.objects.get(id=userId)
        except User.DoesNotExist:
            return Response({"code": 404, "message": "User not found"}, status=404)
        # Mark all messages from other_user to current user as read
        updated = Message.objects.filter(sender=other_user, receiver=request.user, read=False).update(read=True)
        return Response({
            "success": True,
            "message": f"Messages marked as read",
            "updated": updated
        })
