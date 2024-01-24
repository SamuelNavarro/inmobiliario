import logging
import time

import ollama
import openai
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from inmobiliario.chat.api.serializers import AdviceSerializer, AnswerSerializer, ProfileSerializer, QuestionSerializer
from inmobiliario.chat.models import Profile

openai.api_key = settings.OPENAI_API_KEY

logger = logging.getLogger(__name__)

client = openai.OpenAI()


class ProfileViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = ProfileSerializer
    lookup_field = "user__id"  # TODO: cambiar a uuid

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    @action(detail=False)
    def me(self, request):
        serializer = self.serializer_class(request.user.profile, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class AdviceView(CreateAPIView):
    serializer_class = AdviceSerializer

    def post(self, request, *args, **kwargs):
        logger.info(f"AdviceView post: {request.data}")

        advice_text = request.data["text"]
        client = ollama.Client(host="http://host.docker.internal:11435/api/chat")
        response = client.chat(
            model="llama2",
            messages=[
                {
                    "role": "user",
                    "content": f"{advice_text}",
                },
            ],
        )

        llama2_response = response.get("message").get("content")

        logger.info("Respuesta recibida de llama2")

        serializer_data = request.data.copy()
        serializer_data["advice"] = llama2_response

        serializer = self.serializer_class(data=serializer_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionView(CreateAPIView):
    serializer_class = QuestionSerializer

    def post(self, request, *args, **kwargs):
        logger.info(f"QuestionView.post: {request.data}")
        thread_id = "thread_R0zpM9V8pQFydaGkZ74MLbAA"
        assistant_id = "asst_MEtcZIjatdi4zrhpLNcoxk7J"

        message = request.data["text"]
        message = client.beta.threads.messages.create(thread_id=thread_id, role="user", content=message)

        instructions = """Use this data to answer questions in the most truthfull manner. The columns are as follows:
            - The id represents the id of the property.
            - The listing_type which has two categories: for-sale and for-rent.
            - The property_type is either an appartment or a house.
            - last_price is the price of the property.
            - num_bedrooms, num_bathrooms, has_pool, has_terrace and surface_total as the name implies.
        """

        # === Run our Assistant ===
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions=instructions,
        )

        def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
            """

            Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
            :param thread_id: The ID of the thread.
            :param run_id: The ID of the run.
            :param sleep_interval: Time in seconds to wait between checks.
            """
            while True:
                try:
                    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                    if run.completed_at:
                        elapsed_time = run.completed_at - run.created_at
                        formatted_elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                        logging.info(f"Run completed in {formatted_elapsed_time}")

                        messages = client.beta.threads.messages.list(thread_id=thread_id)
                        last_message = messages.data[0]
                        ai_response = last_message.content[0].text.value
                        logger.info(f"ASISTANT RESPONSE : {ai_response}")
                        break

                except Exception as e:
                    logging.error(f"An error occurred while retrieving the run: {e}")
                    ai_response = "Error ocurred"
                    break
                logging.info("Waiting for run to complete...")
                time.sleep(sleep_interval)
            return ai_response

        ai_response = wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)
        data = request.data.copy()
        # data["answer"] = {"text": ai_response}

        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            question = serializer.save()
            answer_data = {"text": ai_response}
            answer_serializer = AnswerSerializer(data=answer_data)
            if answer_serializer.is_valid():
                answer = answer_serializer.save(question=question)
                question.answer = answer.text
                question.save()
            return Response(status=status.HTTP_201_CREATED, data=QuestionSerializer(question).data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class AnswerView(CreateAPIView):
    serializer_class = AnswerSerializer

    def post(self, request, *args, **kwargs):
        logger.info(f"Received AnswerView: {request.data}")
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
