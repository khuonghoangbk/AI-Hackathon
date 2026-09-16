# agentbase/ — Skill deploy lên GreenNode AgentBase

Thư mục này chứa skill AgentBase để triển khai agent lên GreenNode (sinh public
endpoint = Link Demo 4a). Skill được **import từ repo GreenNode**, không tự viết tay.

## Cài skill (một lần, trong vibe code — Claude Code/Codex/OpenCode)

```
claude plugin marketplace add vngcloud/greennode-agentbase-skills
/plugin install greennode-agentbase@greennode-agentbase
```

## Deploy (bám giaingan-thuchien.md Bước D)

Đặt trước biến môi trường:
```
GREENNODE_CLIENT_ID=...
GREENNODE_CLIENT_SECRET=...
```

Chạy wizard trong vibe code:
```
/agentbase-wizard
```

Các bước wizard quan trọng cho dự án này:
- Framework: **Basic** (agent xử lý theo request, không cần chat)
- Bỏ qua Memory, Identity/Auth (chỉ gọi MaaS nội bộ)
- Customize code: gắn 7 bước + route /check, /batch vào entrypoint
- Environment: chọn GreenNode AI Platform làm LLM, set model GLM 5.2 + Qwen Flash
- Local test: `test validate` → `local` → `docker` (cần Docker Desktop đang chạy)
- Deploy: `/agentbase-deploy` → build & push → lấy endpoint URL
- Verify: `curl <endpoint>/health` trả 200

## Lưu ý

- Runtime AgentBase yêu cầu container mở **cổng 8080** và có **`GET /health`** trả 200.
  API trong `api/main.py` đã có sẵn `/health` — khi wizard sinh entrypoint, gắn các
  route hiện có vào app của nó.
- File state do wizard sinh (`.agentbase-state.json`, `.greennode.json`) KHÔNG sửa tay
  và KHÔNG commit (đã có trong .gitignore / cần thêm vào .dockerignore).
