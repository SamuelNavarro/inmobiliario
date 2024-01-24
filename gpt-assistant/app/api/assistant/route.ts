import { experimental_AssistantResponse } from 'ai';
import OpenAI from 'openai';
import { MessageContentText } from 'openai/resources/beta/threads/messages/messages';
import { env } from '@/env.mjs';
import { NextRequest } from 'next/server';
import { z } from 'zod';
import { zfd } from 'zod-form-data';

const schema = zfd.formData({
  threadId: z.string().or(z.undefined()),
  message: zfd.text(),
});

// Create an OpenAI API client (that's edge friendly!)
const openai = new OpenAI({
  apiKey: env.OPENAI_API_KEY || '',
});
export const runtime = 'edge';

export async function POST(req: NextRequest) {
  try {
    // Parse the request body
    const input = await req.formData();

    const data = schema.parse(input);

    const threadId =
      env.OPENAI_THREAD_ID ?? (await openai.beta.threads.create()).id;
    const messageData = {
      role: 'user' as 'user',
      content: data.message,
    };

    const createdMessage = await openai.beta.threads.messages.create(
      threadId,
      messageData,
    );

    return experimental_AssistantResponse(
      { threadId, messageId: createdMessage.id },
      async ({ threadId, sendMessage }) => {
        // Run the assistant on the thread
        const run = await openai.beta.threads.runs.create(threadId, {
          assistant_id:
            env.OPENAI_ASSISTANT_ID ??
            (() => {
              throw new Error('ASSISTANT_ID is not set');
            })(),
        });

        async function waitForRun(run: OpenAI.Beta.Threads.Runs.Run) {
          while (run.status === 'queued' || run.status === 'in_progress') {
            await new Promise((resolve) => setTimeout(resolve, 300));
            run = await openai.beta.threads.runs.retrieve(threadId, run.id);

            if (
              ['cancelled', 'cancelling', 'failed', 'expired'].includes(
                run.status,
              )
            ) {
              throw new Error(`Run status: ${run.status}`);
            }
          }
        }

        await waitForRun(run);

        // Get new thread messages (after our message)
        const responseMessages = (
          await openai.beta.threads.messages.list(threadId, {
            after: createdMessage.id,
            order: 'asc',
          })
        ).data;

        // Send the messages
        for (const message of responseMessages) {
          sendMessage({
            id: message.id,
            role: 'assistant',
            content: message.content.filter(
              (content) => content.type === 'text',
            ) as Array<MessageContentText>,
          });
        }
      },
    );
  } catch (error) {
    console.error('Error in POST function:', error);
    return new Response(
      JSON.stringify({ error: 'An error occurred with the AI response.' }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      },
    );
  }
}
