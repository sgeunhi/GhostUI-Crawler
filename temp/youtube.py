from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver import ActionChains
import time
import os
from datetime import datetime
from PIL import Image, ImageChops
import hashlib

class YouTubeGestureTester:
    def __init__(self):
        self.capabilities = {
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "deviceName": "emulator-5556",
            "appPackage": "com.google.android.youtube",
            "appActivity": "com.google.android.youtube.HomeActivity",
            "autoGrantPermissions": True
        }
        
        self.driver = None
        self.screenshot_dir = "gesture_screenshots"
        
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def start_session(self):
        """Appium 세션 시작"""
        self.driver = webdriver.Remote(
            'http://localhost:4723',
            options=UiAutomator2Options().load_capabilities(self.capabilities)
        )
        time.sleep(5)

    def take_screenshot(self, action_name, stage="before", coordinates=None):
        """스크린샷 촬영 및 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        coord_str = f"_{coordinates[0]}_{coordinates[1]}" if coordinates else ""
        filename = f"{self.screenshot_dir}/{action_name}_{stage}{coord_str}_{timestamp}.png"
        self.driver.get_screenshot_as_file(filename)
        print(f"스크린샷 저장됨: {filename}")

        return self.crop_system_bar(filename)

    def crop_system_bar(self, screenshot_path):
        """상단 시스템 상태 바 영역을 잘라내고 저장"""
        image = Image.open(screenshot_path)
        screen_size = self.driver.get_window_size()
        height = screen_size['height']

        # 상단 바가 포함된 부분 크롭
        cropped_image = image.crop((0, 100, image.width, height))  # (left, top, right, bottom)

        cropped_image.save(screenshot_path)  # 잘라낸 이미지를 덮어쓰기
        return screenshot_path

    def compare_images(self, img1_path, img2_path):
        """두 이미지를 비교하여 변화가 있는지 확인"""
        image1 = Image.open(img1_path)
        image2 = Image.open(img2_path)

        # 이미지 차이를 계산하여 변화가 있으면 True 반환
        diff = ImageChops.difference(image1, image2)
        diff = diff.convert("L")  # 그레이스케일로 변환
        if diff.getbbox():  # 차이가 있다면 bbox 반환
            return True
        return False

    def perform_gesture(self, gesture_type, start_x, start_y, end_x=None, end_y=None):
        """각 제스처 수행: tap, double tap, scroll, long press, drag, pinch"""
        actions = ActionChains(self.driver)
        
        if gesture_type == 'tap':
            actions.move_to_element_with_offset(self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.FrameLayout"), start_x, start_y)
            actions.click()
        elif gesture_type == 'double_tap':
            actions.move_to_element_with_offset(self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.FrameLayout"), start_x, start_y)
            actions.double_click()
        elif gesture_type == 'long_press':
            actions.move_to_element_with_offset(self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.FrameLayout"), start_x, start_y)
            actions.click_and_hold()
            actions.pause(2)  # 2초 동안 홀드
            actions.release()
        elif gesture_type == 'scroll':
            self.driver.swipe(start_x, start_y, start_x, end_y, 1000)
        elif gesture_type == 'drag':
            actions.move_to_element_with_offset(self.driver.find_element(AppiumBy.CLASS_NAME, "android.widget.FrameLayout"), start_x, start_y)
            actions.click_and_hold()
            actions.move_by_offset(end_x - start_x, 0)
            actions.release()
        elif gesture_type == 'pinch':
            pass  # pinch 제스처 추가 필요 
        
        actions.perform()

    def test_gestures_on_all_screen_points(self):
        """화면의 모든 점에 대해 제스처 테스트"""
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']

        # 각 좌표에서 제스처 수행 후 변화가 있을 경우에만 스크린샷 저장
        gestures = ['tap', 'double_tap', 'long_press', 'scroll', 'drag']  # 제스처 목록
        
        for gesture in gestures:
            for x in range(0, width, int(width * 0.01)):  # 1% 간격으로 X 좌표 순회
                for y in range(0, height, int(height * 0.01)):  # 1% 간격으로 Y 좌표 순회
                    print(f"테스트 중: 제스처={gesture}, 좌표=({x}, {y})")
                    
                    # 탭 전 스크린샷 저장
                    before_screenshot = self.take_screenshot(f"{gesture}", "before", coordinates=(x, y))
                    self.perform_gesture(gesture, x, y)
                    time.sleep(1)
                    
                    # 탭 후 스크린샷 저장
                    after_screenshot = self.take_screenshot(f"{gesture}", "after", coordinates=(x, y))
                    
                    # 두 이미지 비교
                    if self.compare_images(before_screenshot, after_screenshot):
                        print(f"좌표=({x}, {y})에서 {gesture} 동작 후 변화가 있음.")

                        # # 변화가 있으면 앱 뒤로가기
                        # self.driver.press_keycode(4)
                        # time.sleep(1)

                        # current_screenshot = self.take_screenshot(f"{gesture}", "restore", coordinates=(x, y))

                        # # 뒤로가기 실패 시 앱 재시작 ??
                        # if not self.compare_images(before_screenshot, current_screenshot):
                        #     print("뒤로가기 실패. 앱 재시작")
                        #     self.driver.launch_app()
                        #     time.sleep(5)

                    else:
                        print(f"좌표=({x}, {y})에서 {gesture} 동작 후 변화 없음")
                        # 변화가 없으면 저장된 스크린샷 삭제
                        os.remove(before_screenshot)
                        os.remove(after_screenshot)

    def run_all_tests(self):
        """모든 제스처 테스트 실행"""
        try:
            self.start_session()
            
            # 각 제스처 테스트 실행
            self.test_gestures_on_all_screen_points()
            
        except Exception as e:
            print(f"테스트 중 오류 발생: {str(e)}")
            
        finally:
            if self.driver:
                self.driver.quit()

def main():
    tester = YouTubeGestureTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()