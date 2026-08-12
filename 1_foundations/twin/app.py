from typing import Dict, List
from sys import exception
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import Update
from models import OpenRouter, Gemini
from context import ContextGen
from tools import tools, handle_tool_calls
from dotenv import load_dotenv
import os


load_dotenv(override=True)
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
context_gen = ContextGen()
system_prompt = context_gen.system_prompt()
chat_history: Dict[int, List[Dict[str, str]]] = {}
max_chat_history = 20

def chat(model, messages):

    model_name = model.model_name

    response = model.client.chat.completions.create(model=model_name, messages=messages, tools=tools)
    finish_reason = response.choices[0].finish_reason
    while finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        message = response.choices[0].message.content
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = model.client.chat.completions.create(model=model_name, messages=messages, tools=tools)
        finish_reason = response.choices[0].finish_reason
    assistant_reply = response.choices[0].message.content
    return assistant_reply

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    history = chat_history[chat_id][-max_chat_history:]

    try:
        # Try openrouter first, fallback to Gemini if needed
        try:
            messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_message}]
            assistant_reply = chat(OpenRouter, messages)
        except Exception as e:
            pass
            print(f"Openrouter is failed: {e}, falling back to Gemini")
            messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_message}]
            assistant_reply = chat(Gemini, messages)

        reply = [{"roll": "user", "content": user_message}] + [{"role": "assistant", "content": assistant_reply}]
        chat_history[chat_id].append(reply)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=assistant_reply)
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        await context.bot.send_message(chat_id=chat_id, text=error_msg)
        print("Error in chat handler")


if __name__ == "__main__":
    app = ApplicationBuilder().token(telegram_token).build()
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler)
    app.add_handler(message_handler)
    app.run_polling()
