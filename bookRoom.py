import time
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def book_room(student_id, password, start_time,duration, library, room, room_number, participants ):
    # 1. 고유한 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()

    # 드라이버와 브라우저를 try...finally 블록으로 감싸서 항상 종료 및 정리되도록 함
    driver = None
    try:
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium"
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # 2. 생성된 임시 디렉토리를 사용자 데이터 디렉토리로 지정
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")

        # Chromedriver 서비스 설정
        service = Service(executable_path="/usr/bin/chromedriver")

        # 드라이버 초기화
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 연세대학교 도서관 로그인 페이지로 이동합니다.
        driver.get("https://library.yonsei.ac.kr/login")

        # 페이지가 완전히 로드될 때까지 잠시 기다립니다.
        time.sleep(2)

        # 아이디 입력 필드를 찾아 아이디를 입력합니다.
        # 'YOUR_ID'를 실제 아이디로 변경하세요.
        username_input = driver.find_element(By.ID, "id")
        username_input.send_keys(student_id)

        # 비밀번호 입력 필드를 찾아 비밀번호를 입력합니다.
        # 'YOUR_PASSWORD'를 실제 비밀번호로 변경하세요.
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(password)

        # 로그인 버튼을 클릭합니다.
        login_button = driver.find_element(By.CSS_SELECTOR, ".loginBtn > input")
        login_button.click()

        # 로그인 후 페이지가 로드될 때까지 잠시 기다립니다.
        time.sleep(5)

        # --- [추가된 코드] ---
        # 로그인 후 좌석/실 현황 및 예약 페이지로 이동합니다.
        driver.get("https://library.yonsei.ac.kr/relation/seat")
        # --------------------

        time.sleep(5)

        wait = WebDriverWait(driver, 5)

        # '시설현황/예약' 링크가 클릭 가능할 때까지 기다린 후 클릭합니다.
        facility_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/fac']"))
        )
        facility_link.click()

        print("✅ '시설현황/예약' 링크를 클릭했습니다.")

        time.sleep(3)

        element = driver.find_element(By.XPATH, "//td[1]//div[contains(@class, 'selectFacility')][last()]")

        # 해당 요소가 화면에 보이도록 스크롤
        driver.execute_script("arguments[0].scrollIntoView(true);", element)

        try:
            # '날짜' 열(첫 번째 <td>)에 있는 모든 날짜 옵션을 리스트로 가져옵니다.
            date_options = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//td[1]//div[contains(@class, 'selectFacility')]"))
            )

            # 리스트에 요소가 있는지 확인 후, 첫 번째 요소를 클릭합니다.
            if date_options:
                date_options[6].click()
                print("✅ 날짜를 성공적으로 클릭했습니다.")
            else:
                return "❌ 날짜 선택 옵션을 찾지 못했습니다."

        except Exception as e:
            return f"❌ 첫 번째 날짜를 클릭하는 데 실패했습니다: {e}"

        try:
            # '도서관 선택' 열(두 번째 <td>) 아래에 있는 모든 'selectFacility' div 요소를 찾음
            library_options = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//td[2]//div[contains(@class, 'selectFacility')]"))
            )

            # 리스트에 요소가 있는지 확인 후 첫 번째 요소를 클릭
            if library_options:
                if library == "학술정보관":
                    library_options[0].click()
                elif library == "중앙도서관":
                    library_options[1].click()
                print("✅ 도서관 옵션을 성공적으로 클릭했습니다.")
            else:
                return "❌ 도서관 선택 옵션을 찾지 못했습니다."

        except Exception as e:
            return f"❌ 첫 번째 도서관 옵션을 클릭하는 데 실패했습니다: {e}"

        try:
            # '3층 Y-CAST' 텍스트를 가진 div 요소를 찾습니다.
            facility_group_element = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//div[normalize-space()='{room}']"))
            )

            # 찾은 요소를 클릭합니다.
            facility_group_element.click()
            print("✅ 장소 그룹을 성공적으로 클릭했습니다.")

        except Exception as e:
            return f"❌ 장소 그룹을 클릭하는 데 실패했습니다: {e}"

        try:
            # 'Y-CELL 3' 텍스트를 가진 div 요소가 클릭 가능해질 때까지 최대 10초간 기다립니다.
            y_cell_element = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//div[normalize-space()='{room_number}']"))
            )

            # 요소를 클릭합니다.
            y_cell_element.click()
            print("방 번호 성공적으로 클릭했습니다.")

        finally:
            # 테스트가 끝나면 브라우저를 종료합니다.
            # driver.quit()
            pass

        try:
            y_cell_element = wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//div[normalize-space()='{duration}']"))
            )

            # 요소를 클릭합니다.
            y_cell_element.click()
            print("시간 요소를 성공적으로 클릭했습니다.")

        finally:
            # 테스트가 끝나면 브라우저를 종료합니다.
            # driver.quit()
            pass

        try:
            # 부모 요소(.graphView) 안의 두 번째 div가 클릭 가능해질 때까지 10초 대기
            time_n = 0

            if start_time == "09:00":
                time_n = 1
            elif start_time == "09:30":
                time_n = 2
            elif start_time == "10:00":
                time_n = 3
            elif start_time == "10:30":
                time_n = 4
            elif start_time == "11:00":
                time_n = 5
            elif start_time == "11:30":
                time_n = 6
            elif start_time == "12:00":
                time_n = 7
            elif start_time == "12:30":
                time_n = 8
            elif start_time == "13:00":
                time_n = 9
            elif start_time == "13:30":
                time_n = 10
            elif start_time == "14:00":
                time_n = 11
            elif start_time == "14:30":
                time_n = 12
            elif start_time == "15:00":
                time_n = 13
            elif start_time == "15:30":
                time_n = 14
            elif start_time == "16:00":
                time_n = 15
            elif start_time == "16:30":
                time_n = 16
            elif start_time == "17:00":
                time_n = 17
            elif start_time == "17:30":
                time_n = 18
            elif start_time == "18:00":
                time_n = 19
            elif start_time == "18:30":
                time_n = 20
            elif start_time == "19:00":
                time_n = 21
            elif start_time == "19:30":
                time_n = 22
            elif start_time == "20:00":
                time_n = 23
            elif start_time == "20:30":
                time_n = 24

            second_element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"div.graphView > div:nth-of-type({time_n})"))
            )

            # 요소를 클릭합니다.
            second_element.click()
            print("시간 요소를 성공적으로 클릭했습니다.")

        finally:
            # driver.quit() # 작업 완료 후 브라우저 종료
            pass

        for i in range(0, len(participants)):
            input_element = wait.until(
                EC.presence_of_element_located((By.ID, "partyMemberId"))
            )

            # input 요소에 텍스트 입력하기
            input_element.send_keys(participants[i]['id'])

            input_element = wait.until(
                EC.presence_of_element_located((By.ID, "partyMemberName"))
            )

            input_element.send_keys(participants[i]['phone'])

            try:
                # '참가자등록' 텍스트를 가진 button 요소가 클릭 가능해질 때까지 최대 10초 대기
                register_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='참가자등록']"))
                )

                # 찾은 버튼을 클릭합니다.
                register_button.click()
                print("참가자등록 버튼을 성공적으로 클릭했습니다.")

            except Exception as e:
                return f"버튼을 클릭하는 중 오류가 발생했습니다: {e}"

            finally:
                # 작업이 끝나면 브라우저를 닫습니다.
                # driver.quit()
                pass

            time.sleep(2)

        try:
            # 'mat-select-value' 클래스를 가진 div가 클릭 가능해질 때까지 10초 대기
            select_element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.mat-select-value"))
            )

            # 요소를 클릭하여 드롭다운 메뉴를 엽니다.
            select_element.click()
            print("드롭다운 메뉴를 성공적으로 클릭했습니다.")

        finally:
            # driver.quit()
            pass

        try:
            # '스터디' 텍스트를 가진 span 요소가 클릭 가능해질 때까지 10초 대기
            study_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='스터디']"))
            )

            # 찾은 '스터디' 옵션을 클릭합니다.
            study_option.click()
            print("'스터디' 옵션을 성공적으로 선택했습니다.")

        except Exception as e:
            return f"옵션을 선택하는 중 오류가 발생했습니다: {e}"

        finally:
            # driver.quit()
            pass

        try:
            # placeholder가 ' 스터디명을 입력해주세요.'인 input 요소가 나타날 때까지 10초 대기
            study_name_input = wait.until(
                EC.visibility_of_element_located((By.XPATH, "//input[@placeholder=' 스터디명을 입력해주세요.']"))
            )

            # input 요소에 '사진 스터디' 텍스트를 입력합니다.
            study_name_input.send_keys("전공 수업 스터디")
            print("'전공 수업 스터디'를 성공적으로 입력했습니다.")

        except Exception as e:
            return f"텍스트를 입력하는 중 오류가 발생했습니다: {e}"

        finally:
            # driver.quit()
            pass

        try:
            # '참가자등록' 텍스트를 가진 button 요소가 클릭 가능해질 때까지 최대 10초 대기
            register_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='예약하기']"))
            )

            # 찾은 버튼을 클릭합니다.
            register_button.click()
            print("예약 등록 버튼을 성공적으로 클릭했습니다.")

        except Exception as e:
            return f"버튼을 클릭하는 중 오류가 발생했습니다: {e}"

        finally:
            # 작업이 끝나면 브라우저를 닫습니다.
            # driver.quit()
            pass

        try:
            # '닫기' 텍스트를 가진 button 요소가 클릭 가능해질 때까지 10초 대기
            close_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='닫기']"))
            )

            # 찾은 '닫기' 버튼을 클릭합니다.
            close_button.click()
            print("'닫기' 버튼을 성공적으로 클릭했습니다.")

        except Exception as e:
            return f"버튼을 클릭하는 중 오류가 발생했습니다: {e}"

        finally:
            # driver.quit()
            pass

        return "Success"

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        # 3. 모든 작업 후 브라우저 종료 및 임시 디렉토리 삭제
        if driver:
            driver.quit()
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
