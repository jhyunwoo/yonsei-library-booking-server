# 1. 베이스 이미지 설정
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# 화면 깨짐 방지를 위한 언어 설정 추가
ENV LANG C.UTF-8

# 4. root 사용자로 전환하여 패키지 설치
USER root

# 5. Chromium 브라우저, 드라이버 및 디버깅용 유틸리티 설치
# 한글 폰트 및 기타 라이브러리 추가
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    fonts-nanum* \
    && rm -rf /var/lib/apt/lists/*

# 6. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. 애플리케이션 코드 복사
COPY . .

# 8. Non-root 유저 생성 및 전환
RUN groupadd --system nonroot && useradd --system --gid nonroot nonroot

# 9. 임시 폴더 및 스크린샷 폴더 생성 및 권한 부여
RUN mkdir /app/temp /app/screenshots && chown -R nonroot:nonroot /app/temp /app/screenshots
USER nonroot

# 10. 포트 노출
EXPOSE 8000

# 11. 애플리케이션 실행 (Gunicorn 타임아웃을 120초로 설정)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "1", "app:app"]