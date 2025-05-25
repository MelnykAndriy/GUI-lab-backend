from django.urls import path

from chats.views import ChatMessagesView, RecentChatsView, SendMessageView, MarkMessagesAsReadView

urlpatterns = [
    path("", RecentChatsView.as_view(), name="recent_chats"),
    path("messages/", SendMessageView.as_view(), name="send_message"),
    path("messages/<int:userId>/", ChatMessagesView.as_view(), name="chat_messages"),
    path("messages/<int:userId>/read", MarkMessagesAsReadView.as_view(), name="mark_messages_as_read"),
]
