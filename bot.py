import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
TOKEN = "9275528514:AAHqRdDNjQz7Dfj7vv6f_j9v-qZ4Idzt0_Q"
ADMIN_CHAT_ID = 7585488033  # Replace with your numeric Telegram ID

logging.basicConfig(level=logging.INFO)

# --- MENU DATA ---
MENU = {
    "cat_breakfast": {
        "title": "🍳 ቁርስ (Breakfast)",
        "items": {
            "senber_half": {"name": "ሠንበር 1/2", "price": 650},
            "senber_quarter": {"name": "ሠንበር 1/4", "price": 400},
            "dulet": {"name": "ዱለት", "price": 370},
            "special_dulet": {"name": "ስፔሻል ዱለት", "price": 420},
            "enkulal_firfir": {"name": "እንቁላል ፍርፍር", "price": 250},
            "enkulal_besiga": {"name": "እንቁላል በስጋ", "price": 370},
            "be_enkulal_sils": {"name": "በእንቁላል ስልስ", "price": 300},
            "special_chechebsa": {"name": "ስፔሻል ጨጨብሳ", "price": 320},
            "chechebsa": {"name": "ጨጨብሳ", "price": 270},
            "timatim_sils": {"name": "ቲማቲም ስልስ", "price": 250},
            "firfir": {"name": "ፍርፍር", "price": 220},
            "yekurs_combo": {"name": "የቁርስ combo", "price": 460},
            "ruz_tibs_be_enkulal": {"name": "ሩዝ ጥብስ በእንቁላል", "price": 320},
        },
    },
    "cat_fasting": {
        "title": "🥗 የጾም (Fasting)",
        "items": {
            "tegabino": {"name": "ተጋቢኖ", "price": 320},
            "shiro": {"name": "ሽሮ", "price": 260},
            "shiro_shifnfn": {"name": "ሽሮ ሽፍንፍን", "price": 280},
            "gomen": {"name": "ጎመን", "price": 260},
            "dirkosh": {"name": "ድርቆሽ", "price": 270},
            "timatim": {"name": "ቲማቲም", "price": 220},
            "soya_tibs": {"name": "ሶያ ጥብስ", "price": 260},
            "dinich_tibs_firfir": {"name": "ድንች ጥብስ ፍርፍር", "price": 280},
            "ruz_tibs_atkilt": {"name": "ሩዝ ጥብስ በአትክልት", "price": 270},
            "ruz_tibs_soya": {"name": "ሩዝ ጥብስ በሶያ", "price": 300},
            "pasta_besigo": {"name": "ፖስታ በስጎ", "price": 240},
            "pasta_be_atkilt": {"name": "ፖስታ በአትክልት", "price": 270},
            "pasta_besoya": {"name": "ፖስታ በሶያ", "price": 300},
        },
    },
    "cat_nonfasting": {
        "title": "🥩 የፍስክ (Non-Fasting)",
        "items": {
            "tibs": {"name": "ጥብስ", "price": 380},
            "minchet": {"name": "ምንቸት", "price": 350},
            "banatu": {"name": "ባናቱ", "price": 430},
            "tibs_firfir": {"name": "ጥብስ ፍርፍር", "price": 350},
            "bozena": {"name": "ቦዘና", "price": 350},
            "gomen_besiga": {"name": "ጎመን በስጋ", "price": 370},
            "ruz_tibs_besiga": {"name": "ሩዝ ጥብስ በስጋ", "price": 370},
            "dirkosh_besiga": {"name": "ድርቆሽ በስጋ", "price": 420},
            "pasta_besiga": {"name": "ፓስታ በስጋ", "price": 330},
            "shiro_bekibe": {"name": "ሽሮ በቅቤ", "price": 300},
            "dirkosh_bekibe": {"name": "ድርቆሽ በቅቤ", "price": 330},
        },
    },
    "cat_agelgil": {
        "title": "🧺 አገልግል (Agelgil)",
        "items": {
            "agelgil_full": {"name": "የፍስክ ሙሉ (Full)", "price": 850},
            "agelgil_half": {"name": "የፍስክ ግማሽ (Half)", "price": 500},
        },
    },
    "cat_drinks": {
        "title": "🥤 መጠጦች (Drinks)",
        "items": {
            "water_2l": {"name": "ውሀ Water 2L", "price": 70},
            "water_1l": {"name": "ውሀ Water 1L", "price": 60},
            "water_half": {"name": "ውሀ Water 1/2", "price": 50},
            "softdrink": {"name": "ለስላሳ Softdrink", "price": 80},
            "single": {"name": "ሲንግል Single", "price": 60},
            "beer": {"name": "ቢራ Beer", "price": 120},
            "special_beer": {"name": "ስፔሻል ቢራ Special Beer", "price": 130},
            "ariki": {"name": "አረቄ Ariki", "price": 70},
            "coffee": {"name": "ቡና Coffee", "price": 50},
            "tea": {"name": "ሻይ Tea", "price": 40},
        },
    },
}

# --- STATE ---
USER_CARTS = {}
DAILY_SALES = []
BOT_PAUSED = False


def get_item(item_id):
    for cat in MENU.values():
        if item_id in cat["items"]:
            return cat["items"][item_id]
    return None


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍽️ Menu / ሜኑ", callback_data="show_menu")],
        [InlineKeyboardButton("🛒 View Cart / ቅርጫት", callback_data="view_cart")],
        [InlineKeyboardButton("📅 Reserve Table / ቦታ ያዙ", callback_data="reserve_table")],
        [InlineKeyboardButton("🔔 Call Waiter / አስተናጋጅ ጥራ", callback_data="call_waiter")],
    ])


def categories_keyboard():
    buttons = [
        [InlineKeyboardButton(cat["title"], callback_data=cat_id)]
        for cat_id, cat in MENU.items()
    ]
    buttons.append([InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")])
    return InlineKeyboardMarkup(buttons)


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Start Msana Restaurant Bot"),
        BotCommand("menu", "Browse food & drinks"),
        BotCommand("cart", "View your order cart"),
        BotCommand("reserve", "Reserve a table"),
        BotCommand("waiter", "Call a waiter"),
        BotCommand("sales", "Admin: View daily sales"),
        BotCommand("pause", "Admin: Pause/Resume orders"),
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 **Welcome to Msana Restaurant!**\n"
        "እንኳን ወደ ምሳና ሬስቶራንት በደህና መጡ!\n\n"
        "Choose an option below:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if BOT_PAUSED:
        msg = "⏸️ Sorry, ordering is temporarily paused. Please check back soon!"
        if update.message:
            await update.message.reply_text(msg)
        else:
            await update.callback_query.answer(msg, show_alert=True)
        return

    text = "📋 **Select a Category / ምድብ ይምረጡ:**"
    if update.message:
        await update.message.reply_text(text, reply_markup=categories_keyboard(), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=categories_keyboard(), parse_mode="Markdown")


async def show_category_items(query, cat_id):
    cat = MENU[cat_id]
    buttons = []
    for item_id, info in cat["items"].items():
        buttons.append([
            InlineKeyboardButton(
                f"{info['name']} — {info['price']} ETB ➕",
                callback_data=f"add_{item_id}"
            )
        ])
    buttons.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="show_menu")])
    buttons.append([InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")])
    await query.edit_message_text(
        f"**{cat['title']}**\nTap an item to add it to your cart:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cart = USER_CARTS.get(user_id, {})

    if not cart:
        text = "🛒 Your cart is currently empty."
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🍽️ Browse Menu", callback_data="show_menu")]
        ])
    else:
        lines = ["🛒 **Your Order Cart:**\n"]
        total = 0
        for item_id, qty in cart.items():
            item = get_item(item_id)
            if item:
                subtotal = item["price"] * qty
                total += subtotal
                lines.append(f"• {item['name']} x{qty} = **{subtotal} ETB**")
        lines.append(f"\n💰 **Total: {total} ETB**")
        text = "\n".join(lines)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_order")],
            [InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")],
            [InlineKeyboardButton("➕ Add More Items", callback_data="show_menu")],
        ])

    if update.message:
        await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")


async def confirm_order(query, context):
    if BOT_PAUSED:
        await query.answer("⏸️ Ordering is currently paused.", show_alert=True)
        return

    user = query.from_user
    cart = USER_CARTS.get(user.id, {})
    if not cart:
        await query.answer("Your cart is empty!", show_alert=True)
        return

    order_lines = []
    total = 0
    for item_id, qty in cart.items():
        item = get_item(item_id)
        if item:
            subtotal = item["price"] * qty
            total += subtotal
            order_lines.append(f"- {item['name']} x{qty} ({subtotal} ETB)")

    DAILY_SALES.append({
        "time": datetime.now().strftime("%H:%M"),
        "user": user.full_name,
        "total": total,
    })

    USER_CARTS[user.id] = {}

    await query.edit_message_text(
        "✅ **Order Confirmed!**\n\n"
        + "\n".join(order_lines)
        + f"\n\n💰 **Total: {total} ETB**\nThank you for ordering from Msana Restaurant!",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🔔 **New Order from {user.full_name} (@{user.username or 'N/A'})**\n\n"
                 + "\n".join(order_lines)
                 + f"\n\n💰 **Total: {total} ETB**",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.warning(f"Could not notify admin: {e}")


