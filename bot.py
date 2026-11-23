import os
import re
import base64
import json, os, logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "")
STAFF_GROUP_ID = -1003938928447
OWNER_ID = 7585488033
SALES_FILE = "/data/data/com.termux/files/home/msana_sales.json"
logging.basicConfig(level=logging.INFO)

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
WEBAPP_URL = "https://dynamic-frangollo-0b20b5.netlify.app/"
DAILY_SALES = json.load(open(SALES_FILE)) if os.path.exists(SALES_FILE) else []
USER_CARTS, USER_META, AWAITING_RECEIPT, AWAITING_NOTE, BOT_OPEN = {}, {}, set(), set(), True

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
    buttons = [[InlineKeyboardButton(cat["title"], callback_data=cid)] for cid, cat in MENU.items()]
    buttons.append([InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")])
    return InlineKeyboardMarkup(buttons)

def map_miniapp_id(iid):
    all_keys = [k for c in MENU.values() for k in c["items"].keys()]
    if iid in all_keys:
        return iid
    if iid.startswith("m") and iid[1:].isdigit():
        idx = int(iid[1:]) - 1
        if 0 <= idx < len(all_keys):
            return all_keys[idx]
    if iid.startswith("d") and iid[1:].isdigit():
        idx = 38 + int(iid[1:])
        if 0 <= idx < len(all_keys):
            return all_keys[idx]
    return iid

def map_miniapp_id(iid):
    all_keys = [k for c in MENU.values() for k in c["items"].keys()]
    if iid in all_keys:
        return iid
    if iid.startswith("m") and iid[1:].isdigit():
        idx = int(iid[1:]) - 1
        if 0 <= idx < len(all_keys):
            return all_keys[idx]
    if iid.startswith("d") and iid[1:].isdigit():
        idx = 38 + int(iid[1:])
        if 0 <= idx < len(all_keys):
            return all_keys[idx]
    return iid

def map_miniapp_id(iid):
    all_keys = [k for c in MENU.values() for k in c["items"].keys()]
    if iid in all_keys:
        return iid
    if iid.startswith("m") and iid[1:].isdigit():
        idx = int(iid[1:]) - 1
        if 0 <= idx < len(all_keys):
            return all_keys[idx]
    if iid.startswith("d") and iid[1:].isdigit():
        idx = 38 + int(iid[1:])
        if 0 <= idx < len(all_keys):
            return all_keys[idx]
    return iid

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text and "o_" in update.message.text:
        m = re.search(r"o_([^_]+)_([^_]+)_([A-Za-z0-9_-]+)", update.message.text)
        if m:
            try:
                tbl_raw, pay_code, items_str = m.group(1), m.group(2), m.group(3)
                table_info = "Takeaway / Delivery" if tbl_raw == "TW" else f"Table {tbl_raw}"
                pay = "📱 Telebirr (0911043647)" if pay_code == "T" else "💵 Cash / At Table"
                lines, total = [], 0
                for pair in items_str.split("-"):
                    if "x" in pair:
                        iid, qty_s = pair.rsplit("x", 1)
                        qty = int(qty_s)
                        item = get_item(iid)
                        if item:
                            sub = item["price"] * qty
                            total += sub
                            lines.append(f"- {item['name']} x{qty} ({sub} ETB)")
                user = update.effective_user
                if not BOT_OPEN:
                    return await update.message.reply_text("🔴 Sorry, Msana Restaurant is currently closed.")
                DAILY_SALES.append({"time": datetime.now().strftime("%H:%M"), "user": user.full_name, "table": table_info, "total": total, "pay": pay})
                json.dump(DAILY_SALES, open(SALES_FILE, "w"), ensure_ascii=False)
                order_text = "\n".join(lines) + f"\n\n🪑 Location: {table_info}\n💰 Total: {total} ETB\n💳 Payment: {pay}"
                extra = "\n\n📸 Please send/attach your Telebirr receipt screenshot or SMS right here!" if "Telebirr" in pay else ""
                if "Telebirr" in pay:
                    AWAITING_RECEIPT.add(user.id)
                await update.message.reply_text(
                    f"✅ **Order Received & Sent to Kitchen!**\n\n{order_text}{extra}\n\n⏳ Waiting for staff confirmation...",
                    reply_markup=main_menu_keyboard(),
                    parse_mode="Markdown"
                )
                staff_kb = InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ Accept Order", callback_data=f"staff_ok_{user.id}"),
                    InlineKeyboardButton("❌ Reject Order", callback_data=f"staff_no_{user.id}")
                ]])
                await context.bot.send_message(
                    chat_id=STAFF_GROUP_ID,
                    text=f"🔔 New Mini App Order from {user.full_name} (@{user.username or 'N/A'})\n\n{order_text}",
                    reply_markup=staff_kb
                )
                print("SUCCESS: SENT TO BOTH CUSTOMER & STAFF GROUP!")
                return
            except Exception as e:
                print("START ORDER ERROR:", e)
                await update.message.reply_text(f"⚠️ Order error: {e}")
                return

    status = "" if BOT_OPEN else "\n\n🔴 **Note: Restaurant ordering is currently CLOSED.**"
    text = f"👋 **Welcome to Msana Restaurant!**\nእንኳን ወደ ምሳና ሬስቶራንት በደህና መጡ!\n\nTap **📱 Launch Mini App** below to order visually, or use the quick menu buttons:{status}"
    if update.message:
        wkb = ReplyKeyboardMarkup([
            [KeyboardButton("📱 Launch Mini App", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton("🍽️ Chat Menu"), KeyboardButton("🛒 View Cart")],
            [KeyboardButton("📅 Reserve Table"), KeyboardButton("🔔 Call Waiter")]
        ], resize_keyboard=True)
        await update.message.reply_text(text, reply_markup=wkb, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not BOT_OPEN:
        msg = "🔴 Sorry, Msana Restaurant is currently closed for orders."
        return await (update.message.reply_text(msg) if update.message else update.callback_query.answer(msg, show_alert=True))
    text = "📋 **Select a Category / ምድብ ይምረጡ:**"
    if update.message:
        await update.message.reply_text(text, reply_markup=categories_keyboard(), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=categories_keyboard(), parse_mode="Markdown")

async def show_category_items(query, cat_id):
    cat = MENU[cat_id]
    buttons = [[InlineKeyboardButton(f"{v['name']} — {v['price']} ETB ➕", callback_data=f"add_{k}")] for k, v in cat["items"].items()]
    buttons += [[InlineKeyboardButton("⬅️ Back to Categories", callback_data="show_menu")], [InlineKeyboardButton("🛒 View Cart", callback_data="view_cart")]]
    await query.edit_message_text(f"**{cat['title']}**\nTap an item to add it to your cart:", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = USER_CARTS.get(update.effective_user.id, {})
    if not cart:
        text, kb = "🛒 Your cart is currently empty.", InlineKeyboardMarkup([[InlineKeyboardButton("🍽️ Browse Menu", callback_data="show_menu")]])
    else:
        lines, total = ["🛒 **Your Order Cart:**\n"], 0
        for iid, qty in cart.items():
            item = get_item(iid)
            if item:
                sub = item["price"] * qty; total += sub; lines.append(f"• {item['name']} x{qty} = **{sub} ETB**")
        lines.append(f"\n💰 **Total: {total} ETB**")
        text = "\n".join(lines)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Checkout / Order", callback_data="choose_table")], [InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")], [InlineKeyboardButton("➕ Add More Items", callback_data="show_menu")]])
    if update.message:
        await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
async def choose_table(query, context):
    if not BOT_OPEN:
        return await query.answer("🔴 Ordering is currently closed.", show_alert=True)
    if not USER_CARTS.get(query.from_user.id):
        return await query.answer("Your cart is empty!", show_alert=True)
    rows = [[InlineKeyboardButton(f"🪑 Table {i}", callback_data=f"tbl_Table {i}") for i in range(r, r + 3)] for r in range(1, 16, 3)]
    rows.append([InlineKeyboardButton("🥡 Takeaway / Delivery", callback_data="tbl_Takeaway / Delivery")])
    rows.append([InlineKeyboardButton("⬅️ Back to Cart", callback_data="view_cart")])
    await query.edit_message_text("🪑 **Select Your Table or Order Type:**", reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")

async def ask_note_step(target, uid):
    is_query = hasattr(target, "edit_message_text")
    meta = USER_META.get(uid, {})
    note_preview = f"\n📝 **Current Note:** _{meta['note']}_" if meta.get("note") else ""
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✍️ Write Last-Minute Note", callback_data="write_note")], [InlineKeyboardButton("💳 Continue to Payment ➡️", callback_data="choose_payment")], [InlineKeyboardButton("⬅️ Change Table", callback_data="choose_table")]])
    text = f"📍 **Order Type:** {meta.get('table', 'N/A')}{note_preview}\n\nAdd a **last-minute message/note** for the kitchen or continue to payment:"
    await (target.edit_message_text(text, reply_markup=kb, parse_mode="Markdown") if is_query else target.reply_text(text, reply_markup=kb, parse_mode="Markdown"))

async def choose_payment(query, context):
    cart = USER_CARTS.get(query.from_user.id, {})
    if not cart:
        return await query.answer("Your cart is empty!", show_alert=True)
    total = sum(get_item(iid)["price"] * qty for iid, qty in cart.items() if get_item(iid))
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("📱 Pay with Telebirr (0911043647)", callback_data="pay_telebirr")], [InlineKeyboardButton("💵 Pay Cash / At Table", callback_data="pay_cash")], [InlineKeyboardButton("⬅️ Back", callback_data="back_to_note")]])
    await query.edit_message_text(f"💳 **Choose Payment Method**\n\n💰 **Total Amount: {total} ETB**", reply_markup=kb, parse_mode="Markdown")

async def show_telebirr_info(query, context):
    user = query.from_user
    cart = USER_CARTS.get(user.id, {})
    if not cart:
        return await query.answer("Your cart is empty!", show_alert=True)
    total = sum(get_item(iid)["price"] * qty for iid, qty in cart.items() if get_item(iid))
    AWAITING_RECEIPT.add(user.id)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm Transfer (No Screenshot)", callback_data="submit_telebirr")], [InlineKeyboardButton("💵 Switch to Cash", callback_data="pay_cash")], [InlineKeyboardButton("⬅️ Back", callback_data="choose_payment")]])
    await query.edit_message_text(f"📱 **Telebirr Payment Details**\n\n📞 **Number:** `0911043647`\n💰 **Amount:** **{total} ETB**\n\nPay via Telebirr App or dial `*127#`, then send your receipt screenshot/SMS here OR tap **✅ Confirm Transfer**:", reply_markup=kb, parse_mode="Markdown")

async def finalize_order(target, context, payment_method, photo_file_id=None):
    is_query = hasattr(target, "from_user") and hasattr(target, "edit_message_text")
    user = target.from_user
    AWAITING_RECEIPT.discard(user.id); AWAITING_NOTE.discard(user.id)
    cart = USER_CARTS.get(user.id, {})
    if not cart:
        return
    meta = USER_META.pop(user.id, {})
    table_info, note_info = meta.get("table", "Not specified"), meta.get("note", "None")
    lines, total = [], 0
    for iid, qty in cart.items():
        item = get_item(iid)
        if item:
            sub = item["price"] * qty; total += sub; lines.append(f"- {item['name']} x{qty} ({sub} ETB)")
    DAILY_SALES.append({"time": datetime.now().strftime("%H:%M"), "user": user.full_name, "table": table_info, "total": total, "pay": payment_method})
    json.dump(DAILY_SALES, open(SALES_FILE, "w"), ensure_ascii=False)
    USER_CARTS[user.id] = {}
    order_text = "\n".join(lines) + f"\n\n🪑 Location: {table_info}\n📝 Note: {note_info}\n💰 Total: {total} ETB\n💳 Payment: {payment_method}"
    cust_msg = f"⏳ Order Sent to Kitchen!\n\n{order_text}\n\nWaiting for staff confirmation..."
    await (target.edit_message_text(cust_msg, reply_markup=main_menu_keyboard()) if is_query else target.reply_text(cust_msg, reply_markup=main_menu_keyboard()))
    staff_kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept Order", callback_data=f"staff_ok_{user.id}"), InlineKeyboardButton("❌ Reject Order", callback_data=f"staff_no_{user.id}")]])
    if photo_file_id:
        await context.bot.send_photo(chat_id=STAFF_GROUP_ID, photo=photo_file_id, caption=f"🧾 Telebirr Receipt from {user.full_name} ({table_info})")
    await context.bot.send_message(chat_id=STAFF_GROUP_ID, text=f"🔔 New Order from {user.full_name} (@{user.username or 'N/A'})\n\n{order_text}", reply_markup=staff_kb)
async def webapp_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("MINI APP ORDER RECEIVED:", update.effective_message.web_app_data.data)
    user = update.effective_user
    if not BOT_OPEN:
        return await update.message.reply_text("🔴 Sorry, Msana Restaurant is currently closed.")
    data = json.loads(update.effective_message.web_app_data.data)
    lines = [f"- {it["name"]} x{it["qty"]} ({it["price"] * it["qty"]} ETB)" for it in data["items"]]
    total = data["total"]
    table_info = data.get("table", "Not specified")
    pay = data.get("payment", "Cash")
    note = data.get("note", "None")
    DAILY_SALES.append({"time": datetime.now().strftime("%H:%M"), "user": user.full_name, "table": table_info, "total": total, "pay": pay})
    json.dump(DAILY_SALES, open(SALES_FILE, "w"), ensure_ascii=False)
    order_text = "\n".join(lines) + f"\n\n🪑 Location: {table_info}\n📝 Note: {note}\n💰 Total: {total} ETB\n💳 Payment: {pay}"
    if "Telebirr" in pay:
        AWAITING_RECEIPT.add(user.id)
    await update.message.reply_text(f"⏳ Order Sent to Kitchen!\n\n{order_text}\n\nWaiting for staff confirmation...", reply_markup=main_menu_keyboard())
    staff_kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accept Order", callback_data=f"staff_ok_{user.id}"), InlineKeyboardButton("❌ Reject Order", callback_data=f"staff_no_{user.id}")]])
    try:
        await context.bot.send_message(chat_id=STAFF_GROUP_ID, text=f"🔔 New Mini App Order from {user.full_name} (@{user.username or "N/A"})\n\n{order_text}", reply_markup=staff_kb)
        print("SENT TO STAFF GROUP OK!")
    except Exception as e:
        print("STAFF GROUP ERROR:", e)
        await update.message.reply_text(f"⚠️ Staff alert error: {e}")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    step = USER_META.get(uid, {}).get("step")
    txt = update.message.text.strip()
    if step == "table":
        USER_META[uid]["table"] = txt
        USER_META[uid]["step"] = "note"
        return await update.message.reply_text("✍️ Any special note or phone number? (Reply **none** to skip)", parse_mode="Markdown")
    if step == "note":
        USER_META[uid]["note"] = "" if txt.lower() == "none" else txt
        USER_META[uid]["step"] = None
        return await update.message.reply_text("💳 Choose payment method:", reply_markup=payment_keyboard())

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in AWAITING_RECEIPT:
        if USER_CARTS.get(uid):
            await finalize_order(update.message, context, "📱 Telebirr (0911043647) + Screenshot", photo_file_id=update.message.photo[-1].file_id)
        else:
            AWAITING_RECEIPT.discard(uid)
            await context.bot.send_photo(chat_id=STAFF_GROUP_ID, photo=update.message.photo[-1].file_id, caption=f"🧾 Telebirr Receipt from {update.effective_user.full_name}")
            await update.message.reply_text("✅ Telebirr receipt forwarded to staff!")

def build_sales_report():
    if not DAILY_SALES:
        return "📊 Daily Sales Report: No orders recorded yet today."
    rev = sum(s["total"] for s in DAILY_SALES)
    tb = sum(s["total"] for s in DAILY_SALES if "Telebirr" in s["pay"])
    lines = [f"📊 Daily Sales Report ({len(DAILY_SALES)} orders):\n"] + [f"• [{s['time']}] {s['user']} ({s['table']}): {s['total']} ETB [{s['pay']}]" for s in DAILY_SALES] + [f"\n📱 Telebirr: {tb} ETB\n💵 Cash: {rev - tb} ETB\n💰 Total Revenue: {rev} ETB"]
    return "\n".join(lines)

def admin_keyboard(is_owner=False):
    status = "🟢 OPEN" if BOT_OPEN else "🔴 CLOSED"
    rows = [[InlineKeyboardButton("🟢 Open Bot", callback_data="adm_open"), InlineKeyboardButton("🔴 Close Bot", callback_data="adm_close")]]
    if is_owner:
        rows += [[InlineKeyboardButton("📊 Daily Sales Report", callback_data="adm_sales")], [InlineKeyboardButton("🗑️ Clear Today's Sales", callback_data="adm_clear_sales")]]
    return InlineKeyboardMarkup(rows), f"⚙️ **Msana Admin Control Panel**\nCurrent Status: **{status}**"

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != STAFF_GROUP_ID and update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("⛔ Staff/Admin only.")
    kb, txt = admin_keyboard(update.effective_user.id == OWNER_ID)
    await update.message.reply_text(txt, reply_markup=kb, parse_mode="Markdown")

async def pause_bot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_OPEN
    if update.effective_chat.id != STAFF_GROUP_ID and update.effective_user.id != OWNER_ID:
        return
    BOT_OPEN = not BOT_OPEN
    await update.message.reply_text("🟢 Msana Bot is now OPEN!" if BOT_OPEN else "🔴 Msana Bot is now PAUSED!")

async def open_bot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_OPEN
    if update.effective_chat.id != STAFF_GROUP_ID and update.effective_user.id != OWNER_ID:
        return
    BOT_OPEN = True; await update.message.reply_text("🟢 Msana Bot is now OPEN!")

async def close_bot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_OPEN
    if update.effective_chat.id != STAFF_GROUP_ID and update.effective_user.id != OWNER_ID:
        return
    BOT_OPEN = False; await update.message.reply_text("🔴 Msana Bot is now CLOSED!")

async def sales_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("⛔ Owner only command.")
    await context.bot.send_message(chat_id=OWNER_ID, text=build_sales_report())

async def book_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = "📅 Table Reservation Request Sent!\nOur staff has been notified."
    await (update.message.reply_text(text, reply_markup=main_menu_keyboard()) if update.message else update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard()))
    await context.bot.send_message(chat_id=STAFF_GROUP_ID, text=f"📅 Table Reservation Request from {user.full_name} (@{user.username or 'N/A'})")

async def call_waiter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = "🔔 Waiter Called! Someone will be at your table right away."
    await (update.message.reply_text(text, reply_markup=main_menu_keyboard()) if update.message else update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard()))
    await context.bot.send_message(chat_id=STAFF_GROUP_ID, text=f"🔔 Waiter Requested by {user.full_name} (@{user.username or 'N/A'})")
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_OPEN
    q, uid = update.callback_query, update.callback_query.from_user.id
    d = q.data
    if d == "show_menu":
        AWAITING_RECEIPT.discard(uid); AWAITING_NOTE.discard(uid); await q.answer(); await show_menu(update, context)
    elif d in MENU:
        await q.answer(); await show_category_items(q, d)
    elif d.startswith("add_"):
        item = get_item(d[4:])
        if item:
            USER_CARTS.setdefault(uid, {})[d[4:]] = USER_CARTS.get(uid, {}).get(d[4:], 0) + 1
            await q.answer(f"✅ Added {item['name']}!")
    elif d == "view_cart":
        AWAITING_RECEIPT.discard(uid); AWAITING_NOTE.discard(uid); await q.answer(); await view_cart(update, context)
    elif d == "clear_cart":
        AWAITING_RECEIPT.discard(uid); AWAITING_NOTE.discard(uid); USER_CARTS[uid] = {}; USER_META.pop(uid, None); await q.answer("🗑️ Cart cleared!"); await view_cart(update, context)
    elif d == "choose_table":
        await q.answer(); await choose_table(q, context)
    elif d.startswith("tbl_"):
        USER_META.setdefault(uid, {})["table"] = d[4:]; await q.answer(); await ask_note_step(q, uid)
    elif d == "write_note":
        AWAITING_NOTE.add(uid); await q.answer(); await q.edit_message_text("✍️ **Type your last-minute message/note now:**")
    elif d == "back_to_note":
        AWAITING_RECEIPT.discard(uid); await q.answer(); await ask_note_step(q, uid)
    elif d == "choose_payment":
        AWAITING_NOTE.discard(uid); await q.answer(); await choose_payment(q, context)
    elif d == "pay_telebirr":
        await q.answer(); await show_telebirr_info(q, context)
    elif d == "submit_telebirr":
        await q.answer(); await finalize_order(q, context, "📱 Telebirr (0911043647) - Confirmed")
    elif d == "pay_cash":
        await q.answer(); await finalize_order(q, context, "💵 Cash / At Table")
    elif d == "adm_open":
        BOT_OPEN = True; await q.answer("Bot Opened!"); kb, txt = admin_keyboard(uid == OWNER_ID)
        try: await q.edit_message_text(txt, reply_markup=kb, parse_mode="Markdown")
        except Exception: pass
    elif d == "adm_close":
        BOT_OPEN = False; await q.answer("Bot Closed!"); kb, txt = admin_keyboard(uid == OWNER_ID)
        try: await q.edit_message_text(txt, reply_markup=kb, parse_mode="Markdown")
        except Exception: pass
    elif d == "adm_sales":
        if uid != OWNER_ID: return await q.answer("⛔ Owner only!", show_alert=True)
        await q.answer(); await context.bot.send_message(chat_id=OWNER_ID, text=build_sales_report())
    elif d == "adm_clear_sales":
        if uid != OWNER_ID: return await q.answer("⛔ Owner only!", show_alert=True)
        DAILY_SALES.clear(); json.dump(DAILY_SALES, open(SALES_FILE, "w")); await q.answer("🗑️ Daily sales cleared!", show_alert=True)
    elif d.startswith("staff_ok_"):
        cust_id = int(d.rsplit("_", 1)[1])
        await q.answer("Order Accepted!")
        ready_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🍽️ Mark Order Ready", callback_data=f"staff_ready_{cust_id}")]])
        await q.edit_message_text(q.message.text + f"\n\n👨‍🍳 ACCEPTED BY {q.from_user.first_name} (Preparing...)", reply_markup=ready_kb)
        try:
            await context.bot.send_message(chat_id=cust_id, text="✅ Great news! Your Msana Restaurant order has been ACCEPTED by our staff and is being prepared!")
            print("CUSTOMER ACCEPTED DM SENT TO:", cust_id)
        except Exception as e:
            print("CUSTOMER DM ERROR:", e)
    elif d.startswith("staff_ready_"):
        cust_id = int(d.rsplit("_", 1)[1])
        await q.answer("Marked as Ready!")
        await q.edit_message_text(q.message.text.replace("(Preparing...)", "") + f"\n🍽️ READY FOR PICKUP/SERVING (by {q.from_user.first_name})")
        try:
            await context.bot.send_message(chat_id=cust_id, text="🍽️ Your Msana Restaurant order is READY! Enjoy your meal!")
            print("CUSTOMER READY DM SENT TO:", cust_id)
        except Exception as e:
            print("CUSTOMER DM ERROR:", e)
    elif d.startswith("staff_no_"):
        cust_id = int(d.rsplit("_", 1)[1])
        await q.answer("Order Rejected!")
        await q.edit_message_text(q.message.text + f"\n\n❌ REJECTED BY {q.from_user.first_name}")
        try:
            await context.bot.send_message(chat_id=cust_id, text="❌ Sorry, your order could not be accepted right now. Please contact our staff or call a waiter.")
            print("CUSTOMER REJECT DM SENT TO:", cust_id)
        except Exception as e:
            print("CUSTOMER DM ERROR:", e)
    elif d == "reserve_table":
        await q.answer(); await book_table(update, context)
    elif d == "call_waiter":
        await q.answer(); await call_waiter(update, context)

def main():
    print("Starting Msana restaurant bot...")
    app = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).build()
    for cmd, fn in [("start", start), ("menu", show_menu), ("cart", view_cart), ("reserve", book_table), ("waiter", call_waiter), ("admin", admin_panel), ("pause", pause_bot_cmd), ("open", open_bot_cmd), ("close", close_bot_cmd), ("sales", sales_cmd)]:
        app.add_handler(CommandHandler(cmd, fn))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data_handler))
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, text_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
