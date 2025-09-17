# 1. 베이스 이미지 설정
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- [추가된 부분 시작] ---
# root 사용자로 전환하여 패키지 설치
USER root

# Chromium 브라우저와 chromedriver 설치
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver
# --- [추가된 부분 끝] ---

# 4. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 애플리케이션 코드 복사
COPY . .

# 6. Non-root 유저 생성 및 전환
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# --- [추가된 부분 시작] ---
# nonroot 유저가 소유한 임시 폴더를 생성
RUN mkdir /app/temp && chown -R nonroot:nonroot /app/temp
# --- [추가된 부분 끝] ---

USER nonroot

# 7. 포트 노출
EXPOSE 8000

# 8. 애플리케이션 실행
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]