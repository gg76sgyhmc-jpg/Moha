# Moha

مستودع المهارات. أي مهارة تنضاف هنا تصير متاحة في **كل** المشاريع والمحادثات
بعد تركيبها مرة وحدة — مو داخل هذا المستودع فقط.

## التركيب (مرة وحدة)

```
/plugin marketplace add gg76sgyhmc-jpg/Moha
/plugin install omniroute@moha-skills
```

بعدها المهارات تشتغل في أي جلسة، وأي مشروع.

## التحديث

لما تنضاف مهارات جديدة هنا:

```
/plugin marketplace update moha-skills
```

## المحتوى

| الحزمة | العدد | الوصف |
| --- | --- | --- |
| `omniroute` | 46 | تشغيل OmniRoute عبر الـ CLI والـ REST API |

مهارات `omniroute` مصدرها [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute)
(رخصة MIT)، وتنقسم إلى:

- **`cli-*`** (21) — أوامر الطرفية: `cli-serve`، `cli-routing`، `cli-models`،
  `cli-chat`، `cli-keys`، `cli-mcp`، `cli-eval` وغيرها
- **`omni-*`** (23) — واجهة REST المتوافقة مع OpenAI: `omni-auth`،
  `omni-providers`، `omni-inference`، `omni-cache`، `omni-webhooks`،
  `omni-budget` وغيرها
- **`config-codex-cli`** — ربط Codex CLI بـ OmniRoute كخلفية
- **`ponytail`** — مهارة خارجية مستقلة ([المصدر](https://github.com/DietrichGebert/ponytail)، MIT)

## البنية

```
.claude-plugin/marketplace.json      فهرس الحزم
plugins/<حزمة>/
  .claude-plugin/plugin.json         تعريف الحزمة
  skills/<مهارة>/SKILL.md            المهارات
```

لإضافة حزمة جديدة: أنشئ المجلد بنفس البنية، ثم أضِف مدخلًا في `marketplace.json`.
