from rest_framework import serializers

from inmobiliario.chat.models import Advice, Answer, Conversation, ConversationFile, Profile, Question
from inmobiliario.users.api.serializers import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = "__all__"

    def get_user(self, obj):
        return UserSerializer(obj.user, context=self.context).data


class ConversationSerializer(serializers.ModelSerializer):
    # maybe add the line below
    profile = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "profile", "title", "created_at"]


class ConversationFileSerializer(serializers.ModelSerializer):
    # TODO: serializer pk related field
    class Meta:
        model = ConversationFile
        fields = ["id", "conversation", "file", "created_at"]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["text", "created_at", "updated_at", "confidence"]
        read_only_fields = ["created_at", "updated_at"]


class AdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advice
        fields = ["text", "advice", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class QuestionSerializer(serializers.ModelSerializer):
    # answer = AnswerSerializer()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["text", "created_at", "updated_at", "answer"]
        read_only_fields = ["created_at", "updated_at"]

    def get_answer(self, obj):
        answer = Answer.objects.filter(question=obj).first()
        if answer:
            return AnswerSerializer(answer).data
        return None

    # def create(self, validated_data):
    #     answers_data = validated_data.pop('answer', None)
    #     question = Question.objects.create(**validated_data)
    #     if answers_data:
    #         Answer.objects.create(question=question, **answers_data)
    #     return question
