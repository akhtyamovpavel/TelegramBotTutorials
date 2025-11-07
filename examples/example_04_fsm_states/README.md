# Example 4: FSM States - State Machine

**[Русская версия / Russian version](./README_RU.md)**

## 🎯 What You'll Learn

- Finite State Machine (FSM)
- Multi-step dialogs
- Storing data between messages
- Input validation

## 🚀 Quick Start

```bash
cd aiogram  # or python_telegram_bot
pip install -r requirements.txt
export BOT_TOKEN="your_token_here"
python bot.py
```

## 💻 Key Concepts

```python
# Define states
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_city = State()

# Handler for state
@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.waiting_for_age)
    await message.answer("How old are you?")
```

## 📖 Full Documentation

See [Russian version (README_RU.md)](./README_RU.md) for detailed FSM guide with examples.

---

**[Full documentation in Russian](./README_RU.md)**
