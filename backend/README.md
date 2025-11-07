# Backend (SpringBoot)

1) 设置环境变量 (任选其一):
   - Kimi:  `setx KIMI_API_KEY "your-key"`
   - Qwen:  `setx QWEN_API_KEY "your-key"` 并在 application.yml 将 provider 改为 qwen
2) 进入 backend 目录:  `mvn spring-boot:run`
3) POST `http://127.0.0.1:8080/api/ai/ask-sync` (form-data: image, question)


