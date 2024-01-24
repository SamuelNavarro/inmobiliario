'use client';

import { Button } from '@/components/button';
import { Icons } from '@/components/icons';
import { Input } from '@/components/input';
import { readDataStream } from '@/lib/read-data-stream';
import { AssistantStatus, Message } from 'ai/react';
import { API_URL } from '@/config';
import { ChangeEvent, FormEvent, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';
import Image from 'next/image';

const roleToColorMap: Record<Message['role'], string> = {
  system: 'lightred',
  user: 'white',
  function: 'lightblue',
  assistant: 'gray',
  tool: 'lightyellow',
  data: 'lightpurple',
};

const DotAnimation = () => {
  const dotVariants = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: 0.5 } },
    exit: { opacity: 0, transition: { duration: 0.5 } },
  };

  // Stagger children animations
  const containerVariants = {
    initial: { transition: { staggerChildren: 0 } },
    animate: { transition: { staggerChildren: 0.5, staggerDirection: 1 } },
    exit: { transition: { staggerChildren: 0.5, staggerDirection: 1 } },
  };

  const [key, setKey] = useState(0);

  // ...
  return (
    <motion.div
      key={key}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex gap-x-0.5 -ml-1"
      variants={containerVariants}
      onAnimationComplete={() => setKey((prevKey) => prevKey + 1)}
    >
      {[...Array(3)].map((_, i) => (
        <motion.span key={i} variants={dotVariants}>
          .
        </motion.span>
      ))}
    </motion.div>
  );
};

const Chat = () => {
  const placeholder =
    'Give me the average price of the appartments for sale...';
  const [messages, setMessages] = useState<Message[]>([]);
  const [message, setMessage] = useState<string>(placeholder);
  const [file, setFile] = useState<File | undefined>(undefined);
  const [threadId, setThreadId] = useState<string>('');
  const [error, setError] = useState<unknown | undefined>(undefined);
  const [status, setStatus] = useState<AssistantStatus>('awaiting_message');
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | undefined>('');

  const handleSelectAnswer = (answer: string) => {
    setSelectedAnswer(answer);
  };

  const handleSaveAnswer = async () => {
    try {
      const response = await fetch(`${API_URL}/api/answer/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: selectedAnswer }),
      });

      if (!response.ok) {
        throw new Error('Failed to save the answer');
      }

      // Handle success response
      console.log('Answer saved successfully');
    } catch (error) {
      console.error('Error saving answer:', error);
    }
  };

  const handleFormSubmit = async (e: FormEvent) => {
    e.preventDefault();

    setStatus('in_progress');

    setMessages((messages: Message[]) => [
      ...messages,
      { id: '', role: 'user' as 'user', content: message! },
    ]);

    const formData = new FormData();
    formData.append('message', message as string);
    formData.append('threadId', threadId);
    formData.append('file', file as File);

    const result = await fetch('/api/assistant', {
      method: 'POST',
      body: formData,
    });

    setFile(undefined);

    if (result.body == null) {
      throw new Error('The response body is empty.');
    }

    try {
      for await (const { type, value } of readDataStream(
        result.body.getReader(),
      )) {
        switch (type) {
          case 'assistant_message': {
            setMessages((messages: Message[]) => [
              ...messages,
              {
                id: value.id,
                role: value.role,
                content: value.content[0].text.value,
              },
            ]);
            break;
          }
          case 'assistant_control_data': {
            setThreadId(value.threadId);
            setMessages((messages: Message[]) => {
              const lastMessage = messages[messages.length - 1];
              lastMessage.id = value.messageId;
              return [...messages.slice(0, messages.length - 1), lastMessage];
            });
            break;
          }
          case 'error': {
            setError(value);
            break;
          }
        }
      }
    } catch (error) {
      setError(error);
    }

    setStatus('awaiting_message');
  };

  const handleMessageChange = (e: ChangeEvent<HTMLInputElement>) => {
    setMessage(e.target.value);
  };

  const handleOpenFileExplorer = () => {
    fileInputRef.current?.click();
  };

  return (
    <main className="flex min-h-screen flex-col p-12">
      <div className="flex flex-col w-full max-w-xl mx-auto stretch">
        <h1 className="flex items-center text-3xl text-zinc-100 font-extrabold pb-4">
          <span className="mr-2 pr-3 font-sans font-light">
            Tu agente inmobiliario by{' '}
          </span>
          <Image src="/logo.svg" width={150} height={150} alt="logo" />
        </h1>
        {error != null && (
          <div className="relative bg-red-500 text-white px-6 py-4 rounded-md">
            <span className="block sm:inline">
              Error: {(error as any).toString()}
            </span>
          </div>
        )}

        {messages.map((m: Message) => (
          <div
            key={m.id}
            className="flex justify-between items-start mb-2"
            style={{ color: roleToColorMap[m.role] }}
          >
            <div className="flex flex-col">
              <strong className="pt-2 mt-2">
                {`${m.role.charAt(0).toUpperCase() + m.role.slice(1)}: `}
              </strong>
              <ReactMarkdown className="whitespace-pre-wrap">
                {m.content}
              </ReactMarkdown>
            </div>
            {m.role === 'assistant' && (
              <Button
                onClick={() => handleSelectAnswer(m.content)}
                className="save-button self-center"
              >
                Selecciona para guardar
              </Button>
            )}
          </div>
        ))}

        {status === 'in_progress' && (
          <span className="text-white flex gap-x-2">
            <Icons.spinner className="animate-spin w-5 h-5" />
            Analyzing
            <DotAnimation />
          </span>
        )}

        <form
          onSubmit={handleFormSubmit}
          className="flex items-start flex-col p-4 pb-2 text-white max-w-xl bg-black mx-auto fixed bottom-0 w-full mb-8 border border-gray-300 rounded-xl shadow-xl"
        >
          <div className="flex items-start w-full">
            <Input
              disabled={status !== 'awaiting_message'}
              className="flex-1 placeholder:text-gray-500 bg-neutral-900"
              placeholder={placeholder}
              onChange={handleMessageChange}
            />
            <Button
              className="flex-0 ml-2 cursor-pointer"
              variant="ghost"
              type="submit"
              disabled={status !== 'awaiting_message'}
            >
              <Icons.arrowRight className="text-gray-200 hover:text-white transition-colors duration-200 ease-in-out" />
            </Button>
            <Button
              type="button"
              className="save-answer-button"
              onClick={handleSaveAnswer}
              disabled={!selectedAnswer}
            >
              Guardar respuesta
            </Button>
          </div>
        </form>
      </div>
    </main>
  );
};

export default Chat;
