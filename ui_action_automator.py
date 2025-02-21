import time
import re
import numpy as np
from PIL import Image
from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.element_finder import ElementFinder
from utils.gesture_handler import GestureHandler
from utils.data_saver import DataSaver

class UIActionAutomator:
    def __init__(self, driver):
        self.driver = driver
        self.action_handler = GestureHandler(driver)
        self.element_finder = ElementFinder(driver)
        self.data_saver = DataSaver()
        self.app_name = self.driver.capabilities.get("appPackage", "unknown_app")
        self.initial_view_hierarchy = None

    def ensure_app_running(self):
        """앱이 실행 중인지 확인하고, 실행되지 않았다면 실행"""
        print(f"🔍 현재 실행 중인 앱: {self.driver.current_package}")
        print(f"🔍 현재 실행 중인 액티비티: {self.driver.current_activity}")
              
        try:
            current_package = self.driver.current_package
            if current_package != self.app_name:
                print(f"🚀 {self.app_name} 앱 실행 중...")
                self.driver.activate_app(self.app_name)
                time.sleep(5)  # 앱 실행 대기
                return True
            return True
        except Exception as e:
            print(f"⚠️ 앱 실행 확인 중 오류 발생: {e}")
            return False
        
    # 스크린샷 촬영 및 저장
    def take_screenshot(self, action_name, stage="before", element_id=None, bounds=None):
        # 스크린샷 저장
        screenshot_path = self.data_saver.save_screenshot(self.driver, self.app_name, action_name, stage)

        # view hierarchy 저장
        self.data_saver.save_view_hierarchy(self.driver, self.app_name, action_name, stage)

        # simplified view hierarchy 저장
        self.data_saver.save_simplified_view_hierarchy(self.driver, self.app_name, action_name, stage)

        # action data 저장
        self.data_saver.save_action_data(self.app_name, action_name, element_id, bounds)

        print(f"스크린샷 저장됨: {screenshot_path}")
        return screenshot_path

    def clear_data(self, app_name, action):
        self.data_saver.delete_data(app_name, action)

    # 이미지 비교
    # TODO: 상단 status bar 영역을 제외하고 비교 -> 시간 혹은 배터리 상태 등이 달라져도 무시
    # TODO: action에 의한 유의미한 변화를 감지해야 됨 -> 동영상 플레이어의 경우, 동영상이 재생되어도 화면에 변화가 없음 -> 어떻게 해결할 것인가?
    # TODO: 단순한 이미지 비교로는 부족함 -> OCR을 이용하여 텍스트 비교, 픽셀 단위 비교 등을 고려해야 함
    def compare_images(self, img1_path, img2_path):
        image1 = Image.open(img1_path)
        image2 = Image.open(img2_path)

        img1_array = np.array(image1)
        img2_array = np.array(image2)
        
        # Status bar 영역 제외 (상단 50픽셀 정도)
        status_bar_height = 50
        img1_array = img1_array[status_bar_height:, :, :]
        img2_array = img2_array[status_bar_height:, :, :]
        
        # Calculate the difference and set a threshold
        diff = np.abs(img1_array - img2_array)
        diff_percentage = np.sum(diff > 0) / diff.size
        
        # 1% 이상의 픽셀이 변경되었을 때 변화가 있다고 판단
        return diff_percentage > 0.01
    
    def go_back_to_initial_screen(self, max_attempts=5, timeout=3):
        """액션 수행 후 원래 화면으로 돌아가기"""
        print("원래 화면으로 복귀 중...")
        
        if not self.initial_view_hierarchy:
            print("⚠️ 초기 화면 정보가 없습니다.")
            return False

        for attempt in range(max_attempts):
            current_view = self.driver.page_source
            
            if self.is_same_screen(self.initial_view_hierarchy, current_view):
                print(f"✅ 원래 화면으로 복귀 완료! (시도: {attempt + 1})")
                return True
            
            # self.driver.back()
            driver.press_keycode(4)
            time.sleep(timeout)

            if attempt == max_attempts - 1:
                try:
                    self.driver.activate_app(self.app_name)
                    time.sleep(timeout)
                    print("✅ 홈 화면으로 이동 후 앱 재실행 성공!")
                    return True
                except Exception as e:
                    print(f"⚠️ 앱 실행 확인 중 오류 발생: {e}")
                    return False
        
        print("⚠️ 원래 화면으로 돌아가지 못함")
        return False

    def is_same_screen(self, view1, view2):
        """두 개의 View Hierarchy가 같은 화면인지 비교"""
        return view1 == view2  # 간단 비교 (필요시 개선)
    
    def run_test_on_ui_elements(self):
        # TODO: action을 수행한 이후 다시 원래 화면으로 돌아와야 함
        if not self.ensure_app_running():
            print("⚠️ 앱 실행 실패")
            return
        
         # 앱 로드 대기
        time.sleep(5) 

        elements = self.element_finder.find_interactive_elements()
        self.initial_view_hierarchy = self.driver.page_source

        for idx, element in enumerate(elements):
            bounds = element.attrib.get("bounds")
            if not bounds:
                continue

            match = re.findall(r"\d+", bounds)
            if len(match) != 4:
                continue

            x1, y1, x2, y2 = map(int, match)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            print(f"[{idx+1}/{len(elements)}] UI 요소 테스트 중: 위치=({center_x}, {center_y})")

            # TODO: swipe, double_tap, pinch_zoom 추가해야 함
            actions = ["tap", "long_press"]

            for action in actions:
                # 액션 수행 전 스크린샷
                before_screenshot = self.take_screenshot(action, "before", element_id=idx, bounds=bounds)
                before_view_hierarchy = self.driver.page_source

                # 액션 실행
                if action == "tap":
                    self.action_handler.perform_tap(center_x, center_y)
                elif action == "long_press":
                    self.action_handler.perform_long_press(center_x, center_y)
                elif action == "swipe":
                    # 위로 swipe
                    self.action_handler.perform_swipe(center_x, center_y, center_x, center_y - 200)
                
                 # UI 변화 대기
                if action == "tap":
                    time.sleep(10)
                elif action == "long_press":
                    time.sleep(0.1)

                # 액션 수행 후 스크린샷
                after_screenshot = self.take_screenshot(action, "after", element_id=idx, bounds=bounds)
                after_view_hierarchy = self.driver.page_source

                # 변화 감지 및 데이터 처리
                screen_changed = self.compare_images(before_screenshot, after_screenshot)
                view_changed = not self.is_same_screen(before_view_hierarchy, after_view_hierarchy)

                if view_changed:
                    print(f"✅ {action} 수행 후 변화 감지됨!")

                    if not self.go_back_to_initial_screen():
                        print("⚠️ 원래 화면으로 돌아가기 실패")
                        return
                else:
                    print(f"❌ {action} 수행 후 변화 없음. 폴더 삭제")
                    self.clear_data(self.app_name, action)

                time.sleep(5)  # 다음 액션 대기

if __name__ == "__main__":
    # TODO: 여러 개의 앱을 테스트해야 함.
    # TODO: 테스트할 앱의 모든 화면에 대해서 테스트를 진행해야 함. -> 모든 activity에 대해서 테스트를 진행해야 함
    desired_caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "emulator-5556",
        # "appPackage": "com.google.android.youtube",
        # "appActivity": ".app.honeycomb.Shell$HomeActivity",
        "appPackage": "com.twitter.android",
        "appActivity": ".StartActivity",
        "autoGrantPermissions": True,
        "noReset": True
    }

    try:
        driver = webdriver.Remote("http://localhost:4723", options=UiAutomator2Options().load_capabilities(desired_caps))
        tester = UIActionAutomator(driver)
        tester.run_test_on_ui_elements()

    except Exception as e:
        print(f"⚠️ 테스트 실행 중 오류 발생: {e}")

    finally:
        driver.quit()