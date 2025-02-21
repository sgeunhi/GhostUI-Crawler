from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

capabilities = dict(
    platformName="Android",
    automationName="UiAutomator2",
    deviceName="emulator-5556",
    appPackage="com.google.android.youtube",
    appActivity="com.google.android.youtube.HomeActivity",
    language='en',
    locale='US',
    autoGrantPermissions=True
)

appium_server_url = 'http://localhost:4723'

def wait_and_click(driver, by, value, timeout=20):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        element.click()
        return True
    except TimeoutException:
        print(f"Element not found: {value}")
        return False

def scroll_down(driver):
    screen_size = driver.get_window_size()
    start_y = screen_size['height'] * 0.8
    end_y = screen_size['height'] * 0.2
    start_x = screen_size['width'] * 0.5
    
    driver.swipe(start_x, start_y, start_x, end_y, 1000)
    time.sleep(2)

# def find_video_in_results(driver, search_term, max_scrolls=5):
#     scroll_count = 0
#     while scroll_count < max_scrolls:
#         print(f"동영상 검색 시도 {scroll_count + 1}/{max_scrolls}")
        
#         try:
#             # UiSelector를 사용하여 동영상 제목 찾기
#             selector = f'new UiSelector().resourceId("com.google.android.youtube:id/title").textContains("{search_term}")'
#             element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, selector)
#             print(f"동영상 찾음: {element.text}")
#             element.click()
#             return True
#         except Exception as e:
#             print(f"UiSelector로 찾기 실패: {str(e)}")
            
#         # XPath를 사용한 동영상 찾기
#         try:
#             video_elements = driver.find_elements(AppiumBy.XPATH, 
#                 f'//android.widget.TextView[@resource-id="com.google.android.youtube:id/title"]')
            
#             for element in video_elements:
#                 title_text = element.text
#                 print(f"발견된 제목: {title_text}")
#                 if search_term.lower() in title_text.lower():
#                     print(f"매칭되는 동영상 찾음: {title_text}")
#                     element.click()
#                     return True
#         except Exception as e:
#             print(f"XPath로 찾기 실패: {str(e)}")

#         print("스크롤 다운 시도...")
#         scroll_down(driver)
#         scroll_count += 1
#         time.sleep(2)
    
#     return False

def find_video_in_results(driver, search_term, max_scrolls=5):
    scroll_count = 0
    while scroll_count < max_scrolls:
        print(f"동영상 검색 시도 {scroll_count + 1}/{max_scrolls}")
        
        try:
            # description 속성을 사용하여 동영상 찾기
            selector = f'new UiSelector().description("*{search_term}*")'
            print(f"검색 중인 selector: {selector}")
            
            elements = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, selector)
            
            if elements:
                for element in elements:
                    desc = element.get_attribute('content-desc')
                    print(f"발견된 동영상 설명: {desc}")
                    
                    # 동영상이 맞는지 확인 (description에 'video' 포함)
                    if 'video' in desc.lower():
                        print(f"매칭되는 동영상 찾음: {desc}")
                        element.click()
                        return True
            else:
                print("해당 검색어로 동영상을 찾지 못했습니다.")

        except Exception as e:
            print(f"검색 중 오류 발생: {str(e)}")
        
        # 백업 방법: 전체 description 검색
        try:
            selector = 'new UiSelector().descriptionContains("video")'
            elements = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, selector)
            
            for element in elements:
                desc = element.get_attribute('content-desc')
                print(f"검토 중인 동영상: {desc}")
                if search_term.lower() in desc.lower():
                    print(f"매칭되는 동영상 찾음: {desc}")
                    element.click()
                    return True
        except Exception as e:
            print(f"백업 검색 중 오류 발생: {str(e)}")

        print("스크롤 다운 시도...")
        scroll_down(driver)
        scroll_count += 1
        time.sleep(2)
    
    return False

def main():
    driver = None
    try:
        driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
        print("YouTube 앱 실행 완료")
        
        time.sleep(2)
        
        # 권한 허용 팝업 처리
        try:
            permission_buttons = [
                "com.android.permissioncontroller:id/permission_allow_button",
                "com.google.android.packageinstaller:id/permission_allow_button",
                "com.android.packageinstaller:id/permission_allow_button"
            ]
            
            for button_id in permission_buttons:
                try:
                    allow_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((AppiumBy.ID, button_id))
                    )
                    allow_button.click()
                    print("권한 허용됨")
                    time.sleep(1)
                except TimeoutException:
                    continue
        except Exception as e:
            print(f"권한 처리 중 예외 발생 (무시하고 진행): {str(e)}")

        # 검색 버튼 클릭
        print("검색 버튼 클릭 시도...")
        search_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Search"))
        )
        search_button.click()
        print("검색 버튼 클릭 완료")
        time.sleep(2)

        # 검색어 입력
        print("검색어 입력 시도...")
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.ID, "com.google.android.youtube:id/search_edit_text"))
        )
        search_term = "에스파 카리나"
        search_box.send_keys(search_term)
        driver.press_keycode(66)  # 엔터 키
        print("검색어 입력 및 검색 완료")
        time.sleep(3)

        # 동영상 찾기 및 클릭
        print("검색 결과에서 동영상 찾기 시도...")
        if not find_video_in_results(driver, search_term):
            # 검색 실패 시 현재 화면의 요소들 출력
            print("\n현재 화면의 모든 요소:")
            elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
            for elem in elements:
                try:
                    print(f"Text: {elem.text}, Resource-id: {elem.get_attribute('resource-id')}")
                except:
                    continue
            raise Exception("동영상을 찾을 수 없습니다.")
        
        print("동영상 클릭 완료")
        time.sleep(5)

        # 설정 버튼 클릭
        print("설정 버튼 클릭 시도...")
        more_options = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "More options"))
        )
        more_options.click()
        print("설정 버튼 클릭 완료")
        time.sleep(2)

        # 재생 속도 설정
        print("재생 속도 설정 시도...")
        playback_speed = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.TextView[@text='Playback speed']"))
        )
        playback_speed.click()
        time.sleep(2)

        speed_2x = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.TextView[@text='2x']"))
        )
        speed_2x.click()

        print("동영상이 2배속으로 재생 중입니다!")
        time.sleep(10)

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        if driver:
            print("\n현재 화면 구조:")
            print(driver.page_source)
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()