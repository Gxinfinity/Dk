# =========================================================
# 🔥 DEMON KILLER UNIVERSE – SINGLE FILE ADVANCED BOT
# Library: python-telegram-bot v20+
# Safe fantasy RPG + mini games + stylish UI
# =========================================================

import random
import asyncio
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ========================
# CONFIG
# ========================

TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

# ========================
# DATABASE (IN-MEMORY)
# ========================

USERS = {}
GLOBAL_BOSS = {"hp": 3000, "alive": True}

# ========================
# DATA
# ========================

DEMONS = [
    {"name": "Shadow Imp", "hp": 40, "atk": 6},
    {"name": "Flame Wraith", "hp": 60, "atk": 8},
    {"name": "Frost Oni", "hp": 80, "atk": 10},
]

SHOP = {
    "katana": {"price": 50, "atk": 5},
    "armor": {"price": 40, "def": 4},
    "potion": {"price": 15, "heal": 20},
}

# ========================
# HELPERS
# ========================

def get_user(uid):
    if uid not in USERS:
        USERS[uid] = {
            "hp": 100,
            "max_hp": 100,
            "atk": 10,
            "def": 2,
            "coins": 50,
            "inv": [],
            "wins": 0,
            "last_daily": None,
        }
    return USERS[uid]


def hp_bar(cur, max_hp):
    filled = int((cur / max_hp) * 10)
    return "█" * filled + "░" * (10 - filled)


async def animate(message, frames, delay=0.4):
    for f in frames:
        await message.edit_text(f)
        await asyncio.sleep(delay)

# ========================
# COMMANDS (CORE RPG)
# ========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    await update.message.reply_text(
        "🔥 *Demon Killer Universe*\n\n"
        "⚔️ RPG • 🎰 Games • 🏆 PvP\n\n"
        "Commands:\n"
        "/hunt /profile /shop /boss /daily /games",
        parse_mode="Markdown",
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    text = (
        f"👤 *Profile*\n"
        f"❤️ HP: {hp_bar(u['hp'], u['max_hp'])} {u['hp']}/{u['max_hp']}\n"
        f"⚔️ ATK: {u['atk']}  🛡️ DEF: {u['def']}\n"
        f"💰 Coins: {u['coins']}\n"
        f"🏆 Wins: {u['wins']}\n"
        f"🎒 Inv: {', '.join(u['inv']) or 'Empty'}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    demon = random.choice(DEMONS).copy()
    context.user_data["demon"] = demon

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚔️ Attack", callback_data="fight_atk"),
            InlineKeyboardButton("🧪 Potion", callback_data="fight_potion"),
        ],
        [InlineKeyboardButton("🏃 Escape", callback_data="fight_run")]
    ])

    await update.message.reply_text(
        f"👹 *{demon['name']}*\n"
        f"❤️ HP: {demon['hp']}  ⚔️ ATK: {demon['atk']}",
        parse_mode="Markdown",
        reply_markup=kb,
    )


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(f"Buy {k} ({v['price']}💰)", callback_data=f"buy_{k}")]
        for k, v in SHOP.items()
    ]
    await update.message.reply_text(
        "🛒 *Shop*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    today = datetime.utcnow().date()

    if u["last_daily"] == today:
        await update.message.reply_text("⏳ Daily already claimed.")
        return

    reward = random.randint(30, 60)
    u["coins"] += reward
    u["last_daily"] = today
    await update.message.reply_text(f"🎁 Daily reward: +{reward} coins")

# ========================
# MINI GAMES
# ========================

async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 Slots", callback_data="game_slots")],
        [InlineKeyboardButton("🎲 Dice", callback_data="game_dice")],
        [InlineKeyboardButton("🪙 Coin Flip", callback_data="game_coin")],
    ])
    await update.message.reply_text("🎮 *Mini Games*", parse_mode="Markdown", reply_markup=kb)


# ========================
# BOSS RAID
# ========================

async def boss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GLOBAL_BOSS["alive"]:
        await update.message.reply_text("🏆 Boss already defeated!")
        return

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Attack Boss", callback_data="boss_attack")]
    ])

    await update.message.reply_text(
        f"👑 *World Boss*\n"
        f"❤️ HP: {GLOBAL_BOSS['hp']}",
        parse_mode="Markdown",
        reply_markup=kb,
    )

# ========================
# CALLBACKS
# ========================

async def fight_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    u = get_user(q.from_user.id)
    demon = context.user_data.get("demon")

    if not demon:
        await q.edit_message_text("No demon. Use /hunt")
        return

    if q.data == "fight_atk":
        dmg = max(1, u["atk"] - random.randint(0, 3))
        demon["hp"] -= dmg

    elif q.data == "fight_potion":
        if "potion" in u["inv"]:
            u["inv"].remove("potion")
            u["hp"] = min(u["max_hp"], u["hp"] + 20)
        else:
            await q.edit_message_text("❌ No potion!")
            return

    elif q.data == "fight_run":
        context.user_data.pop("demon", None)
        await q.edit_message_text("🏃 You escaped!")
        return

    # demon attacks
    u["hp"] -= max(1, demon["atk"] - u["def"])

    if demon["hp"] <= 0:
        reward = random.randint(10, 25)
        u["coins"] += reward
        u["wins"] += 1
        context.user_data.pop("demon", None)
        await q.edit_message_text(f"🏆 Demon defeated! +{reward}💰")

    elif u["hp"] <= 0:
        u["hp"] = u["max_hp"]
        context.user_data.pop("demon", None)
        await q.edit_message_text("💀 You fainted! HP restored.")

    else:
        await q.edit_message_text(
            f"👹 {demon['name']}\n"
            f"❤️ Demon HP: {demon['hp']}\n"
            f"❤️ Your HP: {u['hp']}",
            reply_markup=q.message.reply_markup,
        )


async def buy_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    u = get_user(q.from_user.id)

    item = q.data.replace("buy_", "")
    data = SHOP[item]

    if u["coins"] < data["price"]:
        await q.edit_message_text("❌ Not enough coins")
        return

    u["coins"] -= data["price"]
    u["inv"].append(item)

    if "atk" in data:
        u["atk"] += data["atk"]
    if "def" in data:
        u["def"] += data["def"]

    await q.edit_message_text(f"✅ Bought {item}")


async def games_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    u = get_user(q.from_user.id)

    if q.data == "game_coin":
        win = random.choice([True, False])
        if win:
            u["coins"] += 10
            await q.edit_message_text("🪙 You WON! +10💰")
        else:
            await q.edit_message_text("🪙 You lost!")

    elif q.data == "game_dice":
        roll = random.randint(1, 6)
        await q.edit_message_text(f"🎲 Dice rolled: {roll}")

    elif q.data == "game_slots":
        slots = random.choice(["🍒🍒🍒", "🍋🍋🍒", "🍎🍋🍒"])
        await q.edit_message_text(f"🎰 {slots}")


async def boss_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    u = get_user(q.from_user.id)

    if not GLOBAL_BOSS["alive"]:
        await q.edit_message_text("Boss already defeated")
        return

    dmg = random.randint(5, 15)
    GLOBAL_BOSS["hp"] -= dmg

    if GLOBAL_BOSS["hp"] <= 0:
        GLOBAL_BOSS["alive"] = False
        u["coins"] += 100
        await q.edit_message_text("🏆 WORLD BOSS DEFEATED!\n+100💰")
    else:
        await q.edit_message_text(f"🔥 You hit boss for {dmg}\nBoss HP: {GLOBAL_BOSS['hp']}")

# ========================
# MAIN
# ========================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("hunt", hunt))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("games", games))
    app.add_handler(CommandHandler("boss", boss))

    # Callbacks
    app.add_handler(CallbackQueryHandler(fight_cb, pattern="fight_"))
    app.add_handler(CallbackQueryHandler(buy_cb, pattern="buy_"))
    app.add_handler(CallbackQueryHandler(games_cb, pattern="game_"))
    app.add_handler(CallbackQueryHandler(boss_cb, pattern="boss_"))

    print("🔥 Demon Killer Universe running...")
    app.run_polling()

if __name__ == "__main__":
    main()