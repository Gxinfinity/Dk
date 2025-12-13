# Demon Killer – Single File Advanced Telegram Game Bot
# Safe fantasy RPG for teens. No graphic violence.
# Library: python-telegram-bot v20+

import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🔑 PUT YOUR BOT TOKEN HERE
TOKEN = ""

# -----------------------------
# In-memory database (single file)
# -----------------------------

USERS = {}

DEMONS = [
    {
        "name": "Shadow Imp",
        "hp": 40,
        "atk": 6,
        "img": "https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif",
    },
    {
        "name": "Flame Wraith",
        "hp": 60,
        "atk": 8,
        "img": "https://media.giphy.com/media/l0HlSNOxJB956qwfK/giphy.gif",
    },
    {
        "name": "Frost Oni",
        "hp": 80,
        "atk": 10,
        "img": "https://media.giphy.com/media/26BRrSvJUa0crqw4E/giphy.gif",
    },
]

SHOP = {
    "katana": {"price": 50, "atk": 5},
    "armor": {"price": 40, "def": 4},
    "potion": {"price": 15, "heal": 20},
}

# -----------------------------
# Helpers
# -----------------------------


def get_user(uid):
    if uid not in USERS:
        USERS[uid] = {
            "hp": 100,
            "max_hp": 100,
            "atk": 10,
            "def": 2,
            "coins": 30,
            "inv": [],
        }
    return USERS[uid]


# -----------------------------
# Commands
# -----------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    await update.message.reply_text(
        "🔥 *Demon Killer*\n\n"
        "Fight demons using *Strength* or *Potions*.\n"
        "Use /hunt to begin!",
        parse_mode="Markdown",
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    text = (
        f"👤 *Profile*\n"
        f"❤️ HP: {u['hp']}/{u['max_hp']}\n"
        f"⚔️ ATK: {u['atk']}  🛡️ DEF: {u['def']}\n"
        f"💰 Coins: {u['coins']}\n"
        f"🎒 Inventory: {', '.join(u['inv']) or 'Empty'}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    demon = random.choice(DEMONS).copy()
    context.user_data["demon"] = demon

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💪 Strength", callback_data="fight_strength"),
                InlineKeyboardButton("🧪 Potion", callback_data="fight_potion"),
            ]
        ]
    )

    await update.message.reply_photo(
        photo=demon["img"],
        caption=f"👹 *{demon['name']}*\nHP: {demon['hp']}  ATK: {demon['atk']}",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for item, data in SHOP.items():
        buttons.append(
            [
                InlineKeyboardButton(
                    f"Buy {item} ({data['price']}💰)",
                    callback_data=f"buy_{item}",
                )
            ]
        )

    await update.message.reply_text(
        "🛒 *Shop*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# -----------------------------
# Callbacks
# -----------------------------


async def fight_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    u = get_user(query.from_user.id)
    demon = context.user_data.get("demon")

    if not demon:
        await query.edit_message_text("No demon found. Use /hunt")
        return

    if query.data == "fight_strength":
        damage = max(1, u["atk"] - random.randint(0, 2))
        demon["hp"] -= damage

    elif query.data == "fight_potion":
        if "potion" in u["inv"]:
            u["inv"].remove("potion")
            u["hp"] = min(u["max_hp"], u["hp"] + 20)
        else:
            await query.edit_message_text("❌ No potion left!")
            return

    # Demon attacks back
    u["hp"] -= max(1, demon["atk"] - u["def"])

    if demon["hp"] <= 0:
        reward = random.randint(10, 20)
        u["coins"] += reward
        context.user_data.pop("demon", None)
        await query.edit_message_text(f"🏆 Demon defeated! +{reward} coins")

    elif u["hp"] <= 0:
        u["hp"] = u["max_hp"]
        context.user_data.pop("demon", None)
        await query.edit_message_text("💀 You fainted! HP restored.")

    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("💪 Strength", callback_data="fight_strength"),
                    InlineKeyboardButton("🧪 Potion", callback_data="fight_potion"),
                ]
            ]
        )

        await query.edit_message_caption(
            caption=f"👹 {demon['name']} HP: {demon['hp']}\n❤️ Your HP: {u['hp']}",
            reply_markup=keyboard,
        )


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    u = get_user(query.from_user.id)
    item = query.data.replace("buy_", "")
    data = SHOP[item]

    if u["coins"] < data["price"]:
        await query.edit_message_text("❌ Not enough coins")
        return

    u["coins"] -= data["price"]
    u["inv"].append(item)

    if "atk" in data:
        u["atk"] += data["atk"]
    if "def" in data:
        u["def"] += data["def"]

    await query.edit_message_text(f"✅ Bought {item}!")


# -----------------------------
# Main
# -----------------------------


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("hunt", hunt))
    app.add_handler(CommandHandler("shop", shop))

    app.add_handler(CallbackQueryHandler(fight_callback, pattern="fight_"))
    app.add_handler(CallbackQueryHandler(buy_callback, pattern="buy_"))

    app.run_polling()


if __name__ == "__main__":
    main()