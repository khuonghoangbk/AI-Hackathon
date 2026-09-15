# Deploy lên GreenNode AgentBase

Thư mục này ghi lại cách triển khai Agent Service (`api/` + `agent/`) lên GreenNode AgentBase, dùng các skill có sẵn ở repo cha (`../../skills/`).

## Điều kiện

- Có IAM Service Account (Client ID + Client Secret). Xem `../../skills/agentbase/SKILL.md` mục Authentication.
- Đã điền `.env` (LLM: `GREENNODE_API_BASE`, `GREENNODE_API_KEY`, `MODEL_*`).
- Docker Desktop đang chạy (skill deploy tự build & push image).

## Runtime contract (bắt buộc)

Agent Service phải đáp ứng contract của AgentBase Runtime:
- Lắng nghe cổng theo biến môi trường runtime cấp.
- Có healthcheck `GET /health` trả trạng thái HEALTHY — đã hiện thực trong `api/main.py`.

Xem chi tiết: `../../skills/agentbase/references/runtime-contract.md`.

## Các bước (dùng skill trong coding agent)

1. Nạp skill GreenNode:
   > "Import skill từ repo greennode-agentbase-skills vào folder agent"
2. Scaffold/kiểm tra cấu hình:
   > `/agentbase-wizard` — làm theo 9 bước, hoặc `/agentbase-wizard test` để validate local/docker.
3. Deploy:
   > `/agentbase-deploy` — build image từ Agent Service, push lên Container Registry, tạo Custom Agent runtime, cấp public endpoint.
4. Cấu hình LLM key trên nền tảng (nếu cần):
   > `/agentbase-llm api-keys create giaingan-key`
5. Theo dõi:
   > `/agentbase-monitor runtime-logs <runtime-id>`

## Sau khi có endpoint

- Trỏ dashboard về endpoint: đặt `window.API_BASE` trong `web/index.html` (xem `web/README.md`).
- Dashboard có thể deploy tách rời trên Vercel/Firebase, gọi vào endpoint agent.

## Ghi chú MVP

Bản demo dùng dữ liệu mô phỏng (`data_mock/`, `config/`) thay cho ECM/Core/BPM thật. Nêu rõ điều này trong pitch, không để giám khảo tự phát hiện.
