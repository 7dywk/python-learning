import os
import json
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from github import Github

# --- НАЛАШТУВАННЯ ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO_NAME)


# --- СТАНИ (FSM) ---
class AddWork(StatesGroup):
    photo = State()
    title = State()
    category = State()
    views = State()


class EditWork(StatesGroup):
    work_index = State()
    field = State()
    new_value = State()


# --- ДОПОМІЖНІ ФУНКЦІЇ ДЛЯ GITHUB ---
def get_portfolio():
    """Стягує актуальний JSON з GitHub"""
    file_gh = repo.get_contents("data/portfolioData.json")
    data = json.loads(file_gh.decoded_content.decode('utf-8'))
    return file_gh, data


def push_portfolio(file_gh, data, commit_message):
    """Пушить оновлений JSON на GitHub"""
    new_json = json.dumps(data, indent=2, ensure_ascii=False)
    repo.update_file(file_gh.path, commit_message, new_json, file_gh.sha)


async def upload_image_to_github(photo: types.PhotoSize, title: str) -> str:
    """Завантажує фото з Телеграму в папку assets на GitHub і повертає шлях"""
    file_info = await bot.get_file(photo.file_id)
    img_name = f"work_{photo.file_id[:8]}.jpg"
    img_path = f"assets/{img_name}"
    file_bytes = await bot.download_file(file_info.file_path)
    repo.create_file(img_path, f"Add img for {title}", file_bytes.read())
    return img_path


# ==========================================
# ГОЛОВНЕ МЕНЮ
# ==========================================
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Завантажити нове", callback_data="menu_add")
    builder.button(text="✏️ Змінити існуюче", callback_data="menu_edit")
    builder.adjust(1)
    await message.answer("Привіт! Що будемо робити з портфоліо?", reply_markup=builder.as_markup())


# ==========================================
# ГІЛКА 1: ДОДАТИ НОВЕ
# ==========================================
@dp.callback_query(F.data == "menu_add")
async def add_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Відправ мені **фотографію** нового прев'ю:", parse_mode="Markdown")
    await state.set_state(AddWork.photo)


@dp.message(AddWork.photo, F.photo)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(photo=photo)
    await message.answer("Чудово. Тепер напиши **назву відео**:")
    await state.set_state(AddWork.title)


@dp.message(AddWork.title, F.text)
async def add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)

    # Кнопки для категорій
    builder = InlineKeyboardBuilder()
    builder.button(text="IRL / Vlogs", callback_data="cat_IRL / Vlogs")
    builder.button(text="Business & Crypto", callback_data="cat_Business & Crypto")
    builder.adjust(1)

    await message.answer("Обери **категорію**:", reply_markup=builder.as_markup())
    await state.set_state(AddWork.category)


@dp.callback_query(AddWork.category, F.data.startswith("cat_"))
async def add_category(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.replace("cat_", "")
    await state.update_data(category=cat)
    await callback.message.edit_text(f"Категорія: {cat}\n\nТепер напиши **перегляди** (наприклад: `500K` або `1.2M`):",
                                     parse_mode="Markdown")
    await state.set_state(AddWork.views)


@dp.message(AddWork.views, F.text)
async def add_views(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    title = user_data['title']
    cat = user_data['category']
    views = message.text
    photo = user_data['photo']

    msg = await message.answer("⏳ Завантажую на сайт, зачекай...")

    try:
        # 1. Вантажимо фото
        img_path = await upload_image_to_github(photo, title)
        # 2. Оновлюємо JSON
        file_gh, data = get_portfolio()
        new_work = {"title": title, "cat": cat, "views": views, "img": img_path}
        data["works"].insert(0, new_work)  # Додаємо на самий початок
        push_portfolio(file_gh, data, f"Add new work: {title}")

        await msg.edit_text(f"✅ Готово! Роботу **«{title}»** додано.\nСайт оновиться за 15 секунд.",
                            parse_mode="Markdown")
        await cmd_start(message, state)
    except Exception as e:
        await msg.edit_text(f"❌ Помилка: {e}")
    finally:
        await state.clear()


# ==========================================
# ГІЛКА 2: РЕДАГУВАННЯ ТА ВИДАЛЕННЯ
# ==========================================
@dp.callback_query(F.data == "menu_edit")
async def edit_start(callback: types.CallbackQuery, state: FSMContext):
    msg = await callback.message.edit_text("⏳ Завантажую список робіт...")

    try:
        _, data = get_portfolio()
        builder = InlineKeyboardBuilder()

        # Виводимо роботи списком кнопок
        for i, work in enumerate(data["works"]):
            # Робимо коротку назву, щоб влізла в кнопку
            short_title = (work['title'][:25] + '..') if len(work['title']) > 25 else work['title']
            btn_text = f"{i + 1}. {short_title} ({work['views']})"
            builder.button(text=btn_text, callback_data=f"edit_wk_{i}")

        builder.button(text="🔙 Назад", callback_data="cancel_edit")
        builder.adjust(1)
        await msg.edit_text("Обери роботу для редагування:", reply_markup=builder.as_markup())
    except Exception as e:
        await msg.edit_text(f"❌ Помилка: {e}")


@dp.callback_query(F.data.startswith("edit_wk_"))
async def edit_work_selected(callback: types.CallbackQuery, state: FSMContext):
    index = int(callback.data.replace("edit_wk_", ""))
    await state.update_data(work_index=index)

    _, data = get_portfolio()
    work = data["works"][index]

    text = (f"**Поточні дані:**\n"
            f"Назва: {work['title']}\n"
            f"Категорія: {work['cat']}\n"
            f"Перегляди: {work['views']}\n\n"
            f"Що хочеш змінити?")

    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Назву", callback_data="edit_field_title")
    builder.button(text="👁 Перегляди", callback_data="edit_field_views")
    builder.button(text="📂 Категорію", callback_data="edit_field_cat")
    builder.button(text="🖼 Фото", callback_data="edit_field_img")
    builder.button(text="❌ ВИДАЛИТИ", callback_data="delete_work")
    builder.button(text="🔙 Назад", callback_data="menu_edit")
    builder.adjust(2, 2, 1, 1)

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=builder.as_markup())


# --- Видалення ---
@dp.callback_query(F.data == "delete_work")
async def process_delete(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    index = user_data['work_index']

    msg = await callback.message.edit_text("⏳ Видаляю...")
    try:
        file_gh, data = get_portfolio()
        title = data["works"][index]["title"]
        del data["works"][index]
        push_portfolio(file_gh, data, f"Delete work: {title}")
        await msg.edit_text(f"🗑 Роботу **«{title}»** видалено!", parse_mode="Markdown")
        await cmd_start(callback.message, state)
    except Exception as e:
        await msg.edit_text(f"❌ Помилка: {e}")
    finally:
        await state.clear()


# --- Редагування конкретного поля ---
@dp.callback_query(F.data.startswith("edit_field_"))
async def ask_new_value(callback: types.CallbackQuery, state: FSMContext):
    field = callback.data.replace("edit_field_", "")
    await state.update_data(field=field)

    if field == "img":
        await callback.message.edit_text("Відправ нове **фото** для цієї роботи:", parse_mode="Markdown")
    elif field == "cat":
        builder = InlineKeyboardBuilder()
        builder.button(text="IRL / Vlogs", callback_data="newval_IRL / Vlogs")
        builder.button(text="Business & Crypto", callback_data="newval_Business & Crypto")
        builder.adjust(1)
        await callback.message.edit_text("Обери нову **категорію**:", reply_markup=builder.as_markup())
        return  # Виходимо, бо значення прийде з callback_query нижче
    else:
        field_ua = "назву" if field == "title" else "перегляди"
        await callback.message.edit_text(f"Напиши нові **{field_ua}**:", parse_mode="Markdown")

    await state.set_state(EditWork.new_value)


# Отримання нової категорії (через кнопку)
@dp.callback_query(EditWork.new_value, F.data.startswith("newval_"))
async def update_category_value(callback: types.CallbackQuery, state: FSMContext):
    new_cat = callback.data.replace("newval_", "")
    await save_edit(callback.message, state, new_cat)


# Отримання тексту (назва або перегляди)
@dp.message(EditWork.new_value, F.text)
async def update_text_value(message: types.Message, state: FSMContext):
    await save_edit(message, state, message.text)


# Отримання нового фото
@dp.message(EditWork.new_value, F.photo)
async def update_photo_value(message: types.Message, state: FSMContext):
    await save_edit(message, state, photo_obj=message.photo[-1])


async def save_edit(message: types.Message, state: FSMContext, text_val=None, photo_obj=None):
    user_data = await state.get_data()
    index = user_data['work_index']
    field = user_data['field']

    msg = await message.answer("⏳ Оновлюю сайт...")
    try:
        file_gh, data = get_portfolio()
        work = data["works"][index]

        if field == "img" and photo_obj:
            new_val = await upload_image_to_github(photo_obj, work['title'])
        else:
            new_val = text_val

        work[field] = new_val
        push_portfolio(file_gh, data, f"Update {field} for {work['title']}")

        await msg.edit_text("✅ Успішно оновлено! Сайт завантажить зміни за 15 секунд.")
        await cmd_start(message, state)
    except Exception as e:
        await msg.edit_text(f"❌ Помилка: {e}")
    finally:
        await state.clear()


@dp.callback_query(F.data == "cancel_edit")
async def cancel_edit(callback: types.CallbackQuery, state: FSMContext):
    await cmd_start(callback.message, state)


async def main():
    print("Бот запущений!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())