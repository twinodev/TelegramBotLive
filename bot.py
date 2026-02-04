from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests
import time

# ------------------ CONFIG ------------------
TOKEN = "8520408570:AAG0us_bGZBEkGRihRx5KUY9aarSbxoX5NI"
REQUIRED_CHANNELS = ["@AfroTechDigital"]
ADMIN_ID = 8412139604  # Your Telegram ID
NANOBANANA_KEY = "723b2caa5ad351d3c78f4a8d3e7dfd21"
OWM_KEY = "72548db56ce06658e96d9003bb11bce0"

# Simple user storage
users = set()

# ------------------ HELPERS ------------------
async def is_subscribed(user_id, app):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await app.bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

def main_menu(user_name):
    keyboard = [
        [InlineKeyboardButton("📥 Download Software", callback_data="download")],
        [InlineKeyboardButton("🖼 Free Images", callback_data="images")],
        [InlineKeyboardButton("🌤 Weather", callback_data="weather")],
        [InlineKeyboardButton("📚 Learn Tech", callback_data="learn")],
        [InlineKeyboardButton("📸 Generate AI Image", callback_data="ai_image")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="contact")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_menu():
    keyboard = [
        [InlineKeyboardButton("📊 Bot Stats", callback_data="stats"),
         InlineKeyboardButton("📢 Broadcast Message", callback_data="broadcast")],
        [InlineKeyboardButton("🔄 Restart Menu", callback_data="restart_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ------------------ /start COMMAND ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    app = context.application

    users.add(user_id)

    # ---------- Check Subscription ----------
    if not await is_subscribed(user_id, app):
        keyboard = [
            [InlineKeyboardButton("Join AfroTechDigital", url="https://t.me/AfroTechDigital")],
            [InlineKeyboardButton("I have joined", callback_data="check")]
        ]
        await update.message.reply_text(
            f"👋 Hi {user_name}!\n\n"
            "🚫 You must join @AfroTechDigital first to use this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ---------- Admin sees BOTH Menus ----------
    if user_id == ADMIN_ID:
        keyboard = [
            # Admin Panel buttons
            [InlineKeyboardButton("📊 Bot Stats", callback_data="stats"),
             InlineKeyboardButton("📢 Broadcast Message", callback_data="broadcast")],
            [InlineKeyboardButton("🔄 Restart Menu", callback_data="restart_menu")],
            # User buttons
            [InlineKeyboardButton("📥 Download Software", callback_data="download")],
            [InlineKeyboardButton("🖼 Free Images", callback_data="images")],
            [InlineKeyboardButton("🌤 Weather", callback_data="weather")],
            [InlineKeyboardButton("📚 Learn Tech", callback_data="learn")],
            [InlineKeyboardButton("📸 Generate AI Image", callback_data="ai_image")],
            [InlineKeyboardButton("📞 Contact Admin", callback_data="contact")]
        ]
        await update.message.reply_text(
            f"👑 Welcome Admin {user_name}! You can use all features below:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ---------- Normal user ----------
    await update.message.reply_text(
        f"✅ Welcome, {user_name}! Choose an option below 👇",
        reply_markup=main_menu(user_name)
    )

# ------------------ CHECK SUBSCRIPTION BUTTON ------------------
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    app = context.application

    if await is_subscribed(user_id, app):
        if user_id == ADMIN_ID:
            await query.edit_message_text(
                "👑 Admin Panel — choose an action:",
                reply_markup=admin_menu()
            )
        else:
            await query.edit_message_text(
                f"✅ Thanks for joining, {user_name}!\nChoose an option below 👇",
                reply_markup=main_menu(user_name)
            )
    else:
        await query.answer("❌ You are still not subscribed!", show_alert=True)

# ------------------ MENU BUTTON HANDLER ------------------
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    choice = query.data
    user_id = query.from_user.id

    # ---------- ADMIN BUTTONS ----------
    if choice == "stats":
        if user_id == ADMIN_ID:
            await query.edit_message_text(f"📊 Total users: {len(users)}")
        else:
            await query.answer("❌ You are not admin!", show_alert=True)

    elif choice == "broadcast":
        if user_id == ADMIN_ID:
            await query.edit_message_text("📢 Send your broadcast message now (type it in chat).")
            context.user_data["awaiting_broadcast"] = True
        else:
            await query.answer("❌ You are not admin!", show_alert=True)

    elif choice == "restart_menu":
        await query.edit_message_text(
            "Menu refreshed!",
            reply_markup=admin_menu() if user_id == ADMIN_ID else main_menu("User")
        )

    # ---------- USER MENU ----------
    elif choice == "download":
        await query.edit_message_text("📥 Download feature coming soon!")
    elif choice == "images":
        await query.edit_message_text("🖼 Image feature coming soon!")
    elif choice == "weather":
        await query.message.reply_text("🌤 Enter your city name to get current weather:")
        context.user_data["awaiting_weather"] = True
    elif choice == "learn":
        await query.edit_message_text("📚 Learning feature coming soon!")
    elif choice == "contact":
        await query.edit_message_text("📞 Contact: @AfroTechDigital")
    elif choice == "ai_image":
        await query.message.reply_text("🖼 Send me a prompt to generate an AI image:")
        context.user_data["awaiting_ai_prompt"] = True

# ------------------ MESSAGE HANDLER ------------------
async def admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # ---------- ADMIN BROADCAST ----------
    if user_id == ADMIN_ID and context.user_data.get("awaiting_broadcast"):
        for uid in users:
            try:
                await context.application.bot.send_message(uid, f"📢 ADMIN MESSAGE:\n{text}")
            except:
                pass
        await update.message.reply_text("✅ Broadcast sent to all users!")
        context.user_data["awaiting_broadcast"] = False
        return

    # ---------- AI IMAGE GENERATION ----------
    if context.user_data.get("awaiting_ai_prompt"):
        prompt = text
        await update.message.reply_text("✨ Generating your image… Please wait a moment.")
        gen_url = "https://api.nanobananaapi.ai/api/v1/nanobanana/generate"
        headers = {"Authorization": f"Bearer {NANOBANANA_KEY}", "Content-Type": "application/json"}
        body = {"prompt": prompt, "type": "TEXTTOIAMGE", "numImages": 1}
        try:
            response = requests.post(gen_url, json=body, headers=headers).json()
            task_id = response.get("data", {}).get("taskId")
        except:
            await update.message.reply_text("❌ Failed to send prompt to Nanobanana.")
            context.user_data["awaiting_ai_prompt"] = False
            return
        if not task_id:
            await update.message.reply_text("❌ Could not start image generation. Try again later.")
            context.user_data["awaiting_ai_prompt"] = False
            return
        status_url = f"https://api.nanobananaapi.ai/api/v1/nanobanana/record-info?taskId={task_id}"
        image_url = None
        for _ in range(30):
            time.sleep(3)
            try:
                status_response = requests.get(status_url, headers={"Authorization": f"Bearer {NANOBANANA_KEY}"}).json()
                if status_response.get("successFlag") == 1:
                    image_url = status_response.get("response", {}).get("resultImageUrl")
                    break
            except:
                continue
        if image_url:
            await update.message.reply_photo(photo=image_url)
        else:
            await update.message.reply_text("⏳ Image not ready yet. Try again later.")
        context.user_data["awaiting_ai_prompt"] = False

    # ---------- WEATHER ----------
    if context.user_data.get("awaiting_weather"):
        city = text
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_KEY}&units=metric"
        try:
            res = requests.get(url).json()
            if res.get("cod") != 200:
                await update.message.reply_text("❌ City not found. Try again.")
            else:
                temp = res["main"]["temp"]
                desc = res["weather"][0]["description"]
                humidity = res["main"]["humidity"]
                wind = res["wind"]["speed"]
                await update.message.reply_text(
                    f"🌤 Weather in {city}:\n"
                    f"Temperature: {temp}°C\n"
                    f"Description: {desc}\n"
                    f"Humidity: {humidity}%\n"
                    f"Wind Speed: {wind} m/s"
                )
        except:
            await update.message.reply_text("❌ Failed to fetch weather. Try again later.")
        context.user_data["awaiting_weather"] = False

# ------------------ APP SETUP ------------------
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_subscription, pattern="check"))
app.add_handler(CallbackQueryHandler(menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_message))

print("Bot running…")
app.run_polling()
