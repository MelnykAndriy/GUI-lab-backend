from django.urls import path

from chats.views import ChatMessagesView, RecentChatsView, SendMessageView

urlpatterns = [
    path("", RecentChatsView.as_view(), name="recent_chats"),
    path("messages/", SendMessageView.as_view(), name="send_message"),
    path("messages/<int:userId>/", ChatMessagesView.as_view(), name="chat_messages"),
]
