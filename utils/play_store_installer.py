from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class PlayStoreInstaller:
    def __init__(self):
        # Appium 설정
        self.caps = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'deviceName': 'emulator-5556',  # 에뮬레이터/디바이스 ID
            'appPackage': 'com.android.vending',  # Play Store 패키지
            'appActivity': 'com.android.vending.AssetBrowserActivity',  # Play Store 메인 액티비티
            'noReset': True
        }
        self.driver = webdriver.Remote("http://localhost:4723", options=UiAutomator2Options().load_capabilities(self.caps))
        self.wait = WebDriverWait(self.driver, 20)

    def install_app(self, package_name):
        try:
            # 검색창 클릭
            search_box = self.wait.until(
                EC.presence_of_element_located((AppiumBy.ID, 'com.android.vending:id/search_box_idle_text'))
            )
            search_box.click()
            
            # 앱 이름 입력
            search_input = self.wait.until(
                EC.presence_of_element_located((AppiumBy.ID, 'com.android.vending:id/search_box_text_input'))
            )
            search_input.send_keys(package_name)
            
            # 검색 실행
            self.driver.press_keycode(66)  # Enter key
            
            # 첫 번째 검색 결과 클릭
            first_result = self.wait.until(
                EC.presence_of_element_located((AppiumBy.ID, 'com.android.vending:id/content_container'))
            )
            first_result.click()
            
            # 설치/업데이트 버튼 찾기 및 클릭
            install_button = self.wait.until(
                EC.presence_of_element_located((AppiumBy.XPATH, 
                    "//android.widget.Button[@resource-id='com.android.vending:id/buy_button']"))
            )
            install_button.click()
            
            # 설치 완료 대기
            print("앱 설치 중...")
            time.sleep(30)  # 설치 완료 대기 시간
            
            print("설치 완료!")
            return True
            
        except Exception as e:
            print(f"설치 중 오류 발생: {str(e)}")
            return False
            
        finally:
            self.driver.quit()

# 사용 예시
if __name__ == "__main__":
    installer = PlayStoreInstaller()
    installer.install_app("com.twitter.android")