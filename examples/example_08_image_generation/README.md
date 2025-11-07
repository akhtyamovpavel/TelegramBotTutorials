# Example 8: Image Generation - AI Image Creation

**[Русская версия / Russian version](./README_RU.md)**

## 🎯 What You'll Learn

- Generating images with PIL/Pillow
- Sending images to users
- Integration with Stable Diffusion, DALL-E
- Creating charts with Matplotlib

## 🚀 Quick Start

```bash
cd aiogram  # or python_telegram_bot
pip install -r requirements.txt
export BOT_TOKEN="your_token_here"
python bot.py
```

## 💻 Key Code

```python
from PIL import Image, ImageDraw
from io import BytesIO

# Generate image
def generate_image(text):
    img = Image.new('RGB', (512, 512), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), text, fill=(255, 255, 0))

    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

# Send image (aiogram)
from aiogram.types import BufferedInputFile

image = generate_image("Hello!")
await message.answer_photo(
    BufferedInputFile(image.read(), filename="image.png"),
    caption="Generated image"
)
```

## 📖 Full Documentation

See [Russian version (README_RU.md)](./README_RU.md) for complete image generation guide.

---

**[Full documentation in Russian](./README_RU.md)**
