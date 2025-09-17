import time
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def book_room(student_id, password, start_time, duration, library, room, room_number, participants):
    temp_dir = tempfile.mkdtemp(dir="/app/temp")
    driver = None
    try:
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium"
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080") # 스크린샷을 위한 해상도 설정
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")

        service = Service(executable_path="/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15) # 대기 시간을 15초로 늘림

        # --- 디버깅을 위한 함수 ---
        def save_debug_info(driver, step_name):
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            # 스크린샷 저장
            screenshot_path = f"/app/screenshots/{timestamp}_{step_name}.png"
            driver.save_screenshot(screenshot_path)
            # HTML 소스 저장
            html_path = f"/app/screenshots/{timestamp}_{step_name}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"❌ 에러 발생: {step_name}. 디버그 파일 저장 완료: {screenshot_path}")

        # 1. 로그인 페이지 이동 및 로그인
        try:
            driver.get("https://library.yonsei.ac.kr/login")
            wait.until(EC.presence_of_element_located((By.ID, "id"))).send_keys(student_id)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.CSS_SELECTOR, ".loginBtn > input").click()
            # 로그인 성공 확인: '로그아웃' 버튼이 나타날 때까지 대기
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Logout')]")))
            print("✅ 로그인 성공")
        except TimeoutException as e:
            save_debug_info(driver, "login_failed")
            return f"❌ 로그인 실패. 아이디/비밀번호를 확인하거나 웹사이트 상태를 점검하세요."
        except Exception as e:
            save_debug_info(driver, "login_error")
            return f"❌ 로그인 중 알 수 없는 에러 발생: {e}"

        # 2. 시설 예약 페이지로 이동
        try:
            driver.get("https://library.yonsei.ac.kr/fac/floor")
            print("✅ 시설 예약 페이지로 이동")
        except Exception as e:
            save_debug_info(driver, "navigation_error")
            return f"❌ 시설 예약 페이지 이동 실패: {e}"

        # 3. 예약 절차 진행 (각 단계마다 try-except로 감싸고 디버깅 정보 저장)
        try:
            # 날짜 선택 (오늘은 0번째, 내일은 1번째... 6일 뒤는 6번째)
            date_options = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//td[1]//div[contains(@class, 'selectFacility')]")))
            date_options[6].click() # 6일 뒤 예약
            print("✅ 날짜 선택 완료")

            # 도서관 선택
            library_map = {"학술정보관": 0, "중앙도서관": 1}
            lib_index = library_map.get(library)
            if lib_index is None: return f"❌ 잘못된 도서관 이름: {library}"
            library_options = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//td[2]//div[contains(@class, 'selectFacility')]")))
            library_options[lib_index].click()
            print(f"✅ 도서관 '{library}' 선택 완료")

            # 장소 그룹 선택
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[normalize-space()='{room}']"))).click()
            print(f"✅ 장소 그룹 '{room}' 선택 완료")

            # 방 번호 선택
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[normalize-space()='{room_number}']"))).click()
            print(f"✅ 방 번호 '{room_number}' 선택 완료")

            # 이용 시간 선택
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[normalize-space()='{duration}']"))).click()
            print(f"✅ 이용 시간 '{duration}' 선택 완료")

            # 시작 시간 선택
            time_map = {f"{h:02d}:{m:02d}": i for i, (h, m) in enumerate(((h, m) for h in range(9, 21) for m in (0, 30)), 1)}
            time_n = time_map.get(start_time)
            if time_n is None: return f"❌ 잘못된 시작 시간: {start_time}"
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"div.graphView > div:nth-of-type({time_n})"))).click()
            print(f"✅ 시작 시간 '{start_time}' 선택 완료")

            # 참가자 등록
            for p in participants:
                wait.until(EC.presence_of_element_located((By.ID, "partyMemberId"))).send_keys(p['id'])
                wait.until(EC.presence_of_element_located((By.ID, "partyMemberName"))).send_keys(p['phone'])
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='참가자등록']"))).click()
                time.sleep(1) # 참가자 등록 후 잠시 대기
            print("✅ 참가자 등록 완료")

            # 이용 목적 선택
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.mat-select-value"))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='스터디']"))).click()
            print("✅ 이용 목적 '스터디' 선택 완료")

            # 스터디명 입력
            wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder=' 스터디명을 입력해주세요.']"))).send_keys("전공 수업 스터디")
            print("✅ 스터디명 입력 완료")

            # 최종 예약하기
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='예약하기']"))).click()
            print("✅ 예약하기 버튼 클릭")

            # 완료 팝업의 닫기 버튼 클릭
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='닫기']"))).click()
            print("🎉 예약 최종 완료!")

        except TimeoutException as e:
            save_debug_info(driver, "booking_step_failed")
            return f"❌ 예약 과정 중 특정 요소를 찾지 못했습니다. 웹사이트 UI가 변경되었을 수 있습니다."
        except Exception as e:
            save_debug_info(driver, "booking_step_error")
            return f"❌ 예약 과정 중 알 수 없는 에러 발생: {e}"

        return "Success"

    except Exception as e:
        if driver:
            save_debug_info(driver, "unexpected_function_error")
        print(f"An error occurred: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        if driver:
            driver.quit()
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)