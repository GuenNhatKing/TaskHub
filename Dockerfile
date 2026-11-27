# Stage 1: Builder - Cài đặt dependencies
FROM python:3.14-slim AS builder
WORKDIR /app

# Thêm /root/.local/bin vào đầu danh sách PATH hiện tại
ENV PATH="/root/.local/bin:$PATH"

# Copy mã nguồn
COPY . .

# Cài curl
RUN apt-get update && apt-get install -y --no-install-recommends curl

# Cài uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Cài đặt các thư viện
RUN uv sync --frozen --no-dev

# Stage 2: Runtime - Chạy ứng dụng
FROM python:3.14-slim AS runtime
WORKDIR /app

# Thêm /app/.venv/bin vào đầu danh sách PATH hiện tại
ENV PATH="/app/.venv/bin:$PATH"

# Tạo một nhóm người dùng tên appgroup với ID là 1000
# Tạo một người dùng mới tên appuser với ID 1000, thuộc nhóm appgroup, 
# sử dụng shell /bin/bash và tạo sẵn thư mục cá nhân (/home/appuser)
# Theo mặc định, container chạy dưới quyền root. Việc tạo appuser giúp hạn chế rủi ro bảo mật
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Chép mã nguồn và thư viện từ giai đoạn Build
COPY --from=builder --chown=appuser:appgroup /app /app

# Chuyển sang người dùng appuser
USER appuser

# Khai báo cổng
EXPOSE 8000

# Lệnh khởi chạy ứng dụng
CMD ["uvicorn", "taskhub.main:app", "--host", "0.0.0.0", "--port", "8000"]
