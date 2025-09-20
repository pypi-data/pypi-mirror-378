# discord_program_manager

مكتبة بايثون للتحكم في بوت ديسكورد وتشغيل برامج من الروابط عبر أوامر الديسكورد.

## الاستخدام

```python
from discord_program_manager import DiscordProgramManager

manager = DiscordProgramManager("توكن البوت", 1418059815888097350)
manager.run()
```

## الميزات
- إرسال رسالة منشن للجميع عند التشغيل
- استقبال أمر `-addprogram <رابط>` وتحميل وتشغيل البرنامج
