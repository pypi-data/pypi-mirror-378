import sys
import time
import random
import asyncio
from datetime import datetime
from logging import Logger
from typing import TYPE_CHECKING, Any

from DrissionPage import ChromiumOptions, ChromiumPage
from DrissionPage.common import wait_until
from DrissionPage.errors import ContextLostError, ElementNotFoundError, WaitTimeoutError

from v2dl.common.const import BASE_URL
from v2dl.common.cookies import load_cookies
from v2dl.common.error import BotError
from v2dl.web_bot.base import BaseBehavior, BaseBot, BaseScroll

if TYPE_CHECKING:
    from v2dl.common import Config
    from v2dl.security import AccountManager, KeyManager


class DrissionBot(BaseBot):
    def __init__(
        self,
        config: "Config",
        key_manager: "KeyManager",
        account_manager: "AccountManager",
    ) -> None:
        super().__init__(config, key_manager, account_manager)
        self.config = config
        self.init_driver()
        self.cloudflare = DriCloudflareHandler(self.page, self.logger)

    def init_driver(self) -> None:
        co = ChromiumOptions()
        args = self.parse_chrome_args()
        if len(args) > 0:
            for arg in args:
                co.set_argument(*arg)
                self.logger.info(f"Apply custom chrome args: {arg}")

        # Do NOT use preset user_agent for drissionpage
        if self.config.static_config.custom_user_agent:
            self.logger.info(
                f"Apply custom user agent: {self.config.static_config.custom_user_agent}"
            )
            co.set_user_agent(user_agent=self.config.static_config.custom_user_agent)

        if not self.config.static_config.use_default_chrome_profile:
            user_data_dir = self.prepare_chrome_profile()
            co.set_user_data_path(user_data_dir)
        else:
            co.use_system_user_path()

        self.page = ChromiumPage(addr_or_opts=co, timeout=0.8)  # type: ignore
        self.page.set.scroll.smooth(on_off=True)
        self.page.set.scroll.wait_complete(on_off=True)

        self.scroller = DriScroll(self.page, self.config, self.logger)

    def close_driver(self) -> None:
        self.page.quit()

    async def auto_page_scroll(
        self,
        url: str,
        max_retry: int = 3,
        page_sleep: int = 5,
    ) -> str:
        self.url = url

        for attempt in range(max_retry):
            try:
                self.page.get(url)

                # handle page redirection fail
                if not self.handle_redirection_fail(url, max_retry, page_sleep):
                    self.logger.error(
                        "Reconnection fail for URL %s. Please check your network status.",
                        url,
                    )
                    break

                if self.cloudflare.handle_simple_block(attempt, max_retry):
                    continue

                # main business
                self.handle_login()
                self.handle_read_limit()
                self.handle_image_captcha()
                self.page.run_js("document.body.style.zoom='50%'")
                await self.scroller.scroll_to_bottom()

                # Sleep to avoid Cloudflare blocking
                self.logger.debug("Scrolling finished, pausing to avoid blocking")
                # DriBehavior.random_sleep(page_sleep, page_sleep + 5)
                break

            except ContextLostError:
                self.handle_login()

            except Exception as e:
                self.logger.exception(
                    "Request failed for URL %s - Attempt %d/%d. Error: %s",
                    url,
                    attempt + 1,
                    max_retry,
                    e,
                )
                # DriBehavior.random_sleep(page_sleep, page_sleep + 5)

        if not self.page.html:
            error_template = "Failed to retrieve URL after {} attempts: '{}'"
            error_msg = error_template.format(max_retry, url)
            self.logger.error(error_msg)
            return error_msg
        elif self.simple_blockage_check(self.page.html):
            raise RuntimeError(
                f"Unexpected error: Base URL '{BASE_URL}' not found in the HTML result.\n"
                "This indicates the request was blocked by an anti-bot check. Suggested actions:\n"
                "  - Change the header using: v2dl <url> --user-agent '<custom user agent>'\n"
                "  - Run in a clean internet environment\n"
                "  - Turn off the VPN if enabled"
            )
        else:
            return self.page.html

    def handle_redirection_fail(self, url: str, max_retry: int, sleep_time: int) -> bool:
        # If read limit exceed, not a redirection fail.
        # If not exceed read limit, check url.
        if self.check_read_limit() or (self.page.url == url and self.page.states.is_alive):
            return True
        retry = 1
        while retry <= max_retry:
            self.logger.warning(
                "Redirection handle failed for URL %s - Attempt %d/%d.",
                url,
                retry,
                max_retry,
            )
            DriBehavior.random_sleep(sleep_time, sleep_time + 5 * random.uniform(1, retry * 5))

            if self.cloudflare.handle_simple_block(retry, max_retry):
                self.logger.warning("Failed to solve Cloudflare turnstile challenge")
                continue

            self.page.get(url)
            retry += 1
            if self.page.url == url and self.page.states.is_alive:
                return True

        return self.page.url == url and self.page.states.is_alive

    def handle_login(self) -> bool:
        """handle login and return the bool represents if login success or not"""
        success = False
        if self.page("xpath=//h1[contains(@class, 'login-box-msg')]"):
            DriBehavior.random_sleep()
            self.logger.info("Login page detected - Starting login process")
            try:
                accounts = self.account_manager.get_all_accounts()
                for _ in accounts:
                    # if no any available account, `AccountManager.random_pick` will execute sys.exit
                    self.account = self.account_manager.random_pick()

                    # this will update cookies_valid
                    if self.cookies_login():
                        return True

                    email_field = self.page("#email")
                    password_field = self.page("#password")

                    # self.handle_cloudflare_recaptcha()
                    email_field.clear(True)
                    password_field.clear(True)

                    DriBehavior.human_like_type(email_field, self.account)
                    DriBehavior.random_sleep(0.01, 0.3)
                    DriBehavior.human_like_type(
                        password_field, self.account_manager.get_pw(self.account, self.private_key)
                    )
                    DriBehavior.random_sleep(0.01, 0.5)

                    login_button = self.page(
                        'xpath=//button[@type="submit" and @class="btn btn-primary"]',
                    )
                    login_button.click()

                    if not self.page(
                        'xpath=//div[contains(@class, "alert-danger") and @role="alert"]',
                        timeout=0.5,
                    ):
                        success = True
                        self.logger.info("Account %s login successful with password", self.account)
                        return success
                    else:
                        self.logger.info(
                            "Account %s Login failed. Checking error messages",
                            self.account,
                        )
                        self.account_manager.update_runtime_state(
                            self.account,
                            "password_valid",
                            False,
                        )
                        self.check_login_errors()
                        return success

            except ElementNotFoundError as e:
                self.logger.error("Login form element not found: %s", e)
                raise
            except WaitTimeoutError as e:
                self.logger.error("Timeout waiting for element: %s", e)
                raise
            except Exception as e:
                self.logger.error("Unexpected error during login: %s", e)
                raise

        else:
            return True

        if not success:
            self.logger.info("Automated login failed. Please login yourself.")
            sys.exit("Automated login failed.")
        return False

    def handle_image_captcha(self) -> bool:
        """Handle image captcha and waiting for manual input if present."""
        xpath = 'xpath=//div[@class="col-md-6 captcha-container card p-3"]'
        captcha_container = self.page(xpath)

        if captcha_container:
            self.logger.info("Image captcha detected - Waiting for manual input")

            while True:
                try:
                    current_captcha = self.page(xpath, timeout=1)
                    if not current_captcha:
                        self.logger.info("Captcha completed - continuing process")
                        break

                    DriBehavior.random_sleep(1, 2)

                except Exception:
                    self.logger.info("Captcha completed - continuing process")
                    break
        else:
            self.logger.debug("No image captcha detected")

        return True

    def cookies_login(self) -> bool:
        account_info = self.account_manager.read(self.account)
        if account_info is None:
            raise BotError("Unexpected error while reading account '%s'", account_info)

        cookies_path = account_info.get("cookies")
        if cookies_path:
            cookies = load_cookies(cookies_path)
            self.page.set.cookies.clear()
            self.page.set.cookies(cookies)
            DriBehavior.random_sleep(0, 3)
            self.page.refresh()
            DriBehavior.random_sleep(0, 3)
            self.page.get(self.url)

        if not self.page(
            'xpath=//div[contains(@class, "alert-danger") and @role="alert"]', timeout=0.5
        ):
            self.logger.info("Account %s login successful with cookies", self.account)
            return True

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.account_manager.update_runtime_state(self.account, "cookies_valid", False)
        self.account_manager.update_account(self.account, "exceed_time", now)
        return False

    def check_login_errors(self) -> None:
        error_message = self.page('xpath=//div[@class="errorMessage"]')
        if error_message:
            self.logger.error("Login error: %s", error_message.text)
        else:
            self.logger.error("Login failed for unknown reasons")
            sys.exit(1)

    def handle_read_limit(self) -> None:
        if self.check_read_limit():
            # click logout
            self.page(
                'xpath=//ul[@class="nav justify-content-end"]//a[contains(@href, "/user/logout")]'
            ).click()
            now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            self.account_manager.update_runtime_state(self.account, "exceed_quota", True)
            self.account_manager.update_account(self.account, "exceed_quota", True)
            self.account_manager.update_account(self.account, "exceed_time", now)
            self.account = self.account_manager.random_pick()

    def check_read_limit(self) -> bool:
        return "https://www.v2ph.com/user/upgrade" in self.page.url

    def click_logout(self) -> None:
        self.page.ele("@href=/user/logout").click()

    def simple_blockage_check(self, html_content: str) -> bool:
        """Return True if the base URL is not in the HTML content, indicating blockage."""
        return BASE_URL not in html_content


class DriCloudflareHandler:
    """Handles Cloudflare protection detection and bypass attempts.

    Includes methods for dealing with various Cloudflare challenges.
    """

    def __init__(self, page: ChromiumPage, logger: Logger) -> None:
        self.page = page
        self.logger = logger

    def handle_simple_block(self, attempt: int, retries: int) -> bool:
        """Check, handle, and return whether blocked or not."""
        blocked = False
        if self.is_simple_blocked():
            self.logger.info(
                "Cloudflare challenge detected - Solve attempt %d/%d",
                attempt + 1,
                retries,
            )
            blocked = self.handle_cloudflare_turnstile()
        return blocked

    def handle_hard_block(self) -> bool:
        """Check whether blocked or not.

        This is a cloudflare WAF full page block.
        """
        blocked = False
        if self.is_hard_block():
            self.logger.warning("Hard block detected by Cloudflare - Unable to proceed")
            blocked = True
        return blocked

    def is_simple_blocked(self) -> bool:
        title_check = any(text in self.page.title for text in ["請稍候...", "Just a moment..."])
        page_source_check = "Checking your" in self.page.html
        return title_check or page_source_check

    def is_hard_block(self) -> bool:
        is_blocked = "Attention Required! | Cloudflare" in self.page.title
        if is_blocked:
            self.logger.warning("Cloudflare hard block detected")
        return is_blocked

    def handle_cloudflare_turnstile(self) -> bool:
        """鬥志鬥勇失敗."""
        blocked = False
        try:
            container = self.page.s_ele(".cloudflare-container")
            turnstile_box = container.s_ele(".turnstile-box")
            turnstile_div = turnstile_box.s_ele("#cf-turnstile")
            turnstile_div.rect.click_point()  # type: ignore
            self.page.wait(2)
            # pyautogui.moveTo(pos[0], pos[1] + 61, duration=0.5)
            # pyautogui.click()
            self.page.wait(3)
            blocked = True
        except Exception as e:
            self.logger.exception("Failed to solve new Cloudflare turnstile: %s", e)
        return blocked

    def random_sleep(self, min_time: float, max_time: float) -> None:
        time.sleep(random.uniform(min_time, max_time))


class DriBehavior(BaseBehavior):
    @staticmethod
    def human_like_mouse_movement(page: Any, element: Any) -> None:
        # Get the element's position
        rect = element.rect
        action_x = random.randint(-100, 100)
        action_y = random.randint(-100, 100)

        # Move by offset and then to element
        page.mouse.move_to(x=rect["x"] + action_x, y=rect["y"] + action_y)
        page.mouse.move_to(rect["x"], rect["y"])
        DriBehavior.random_sleep(*BaseBehavior.pause_time)

    @staticmethod
    def human_like_click(page: Any, element: Any) -> None:
        DriBehavior.human_like_mouse_movement(page, element)
        page.mouse.click()
        DriBehavior.random_sleep(*BaseBehavior.pause_time)

    @staticmethod
    def human_like_type(element: Any, text: str) -> None:
        for char in text:
            element.input(char)
            time.sleep(random.uniform(0.001, 0.2))
        DriBehavior.random_sleep(*BaseBehavior.pause_time)


class DriScroll(BaseScroll):
    def __init__(self, page: ChromiumPage, config: "Config", logger: Logger) -> None:
        super().__init__(config, logger)
        self.page = page
        self.page.set.scroll.smooth(on_off=True)

    async def scroll_to_bottom(self) -> None:
        attempts = 0
        max_attempts = 10
        wait_time = (1, 2)
        last_position = -123459
        scroll_length = lambda: random.randint(
            self.config.static_config.min_scroll_distance,
            self.config.static_config.max_scroll_distance,
        )

        while attempts < max_attempts:
            scroll = scroll_length()
            self.logger.debug(
                "Current position: %d, scrolling down by %d pixels",
                last_position,
                scroll,
            )
            self.page.run_js(f"window.scrollBy({{top: {scroll}, behavior: 'smooth'}});")
            await asyncio.sleep(random.uniform(*wait_time))

            new_position = self.page.run_js("return window.pageYOffset;")
            if new_position == last_position:
                break
            last_position = new_position
            attempts += 1

    def old_scroll_to_bottom(self) -> None:
        self.logger.info("Start scrolling the page")
        scroll_attempts = 0
        max_attempts = 45
        same_position_count = 0
        max_same_position_count = 3
        last_position = 0.0
        scrolled_up = False

        while scroll_attempts < max_attempts:
            scroll_attempts += 1

            current_position = self.get_current_position()

            if current_position == last_position:
                same_position_count += 1
                if same_position_count >= max_same_position_count:
                    self.logger.debug(
                        "Detected the same position three times in a row, stopping scrolling. Scrolled a total of %d times",
                        scroll_attempts,
                    )
                    break
            else:
                same_position_count = 0

            last_position = current_position

            scrolled_up = self.perform_scroll_action(scrolled_up)

            self.wait_for_content_load()

            self.successive_scroll_count += 1
            if self.successive_scroll_count >= self.max_successive_scrolls:
                pause_time = random.uniform(3, 7)
                self.logger.debug(
                    "Scrolled %d times, pausing for %.2f seconds",
                    self.successive_scroll_count,
                    pause_time,
                )
                time.sleep(pause_time)
                scrolled_up = False
                self.successive_scroll_count = 0
                self.max_successive_scrolls = random.randint(3, 7)

        if scroll_attempts == max_attempts:
            self.logger.info(
                "Reached maximum attempts (%d), scrolling finished, may not have fully reached the bottom",
                max_attempts,
            )
        else:
            self.logger.info("Page scroll completed")

    def perform_scroll_action(self, scrolled_up: bool) -> bool:
        while True:
            action = random.choices(
                ["scroll_down", "scroll_up", "pause", "jump"],
                weights=[0.9, 0.1, 0.1, 0.01],
            )[0]

            if (
                action != "scroll_up" or not scrolled_up
            ):  # 連續捲動時，只要往上捲動過一次就不要再選擇往上
                break

        if action == "scroll_down":
            scroll_length = random.randint(
                self.config.static_config.min_scroll_step,
                self.config.static_config.max_scroll_step,
            )
            self.logger.debug("Trying to scroll down %d", scroll_length)
            self.page.scroll.down(pixel=scroll_length)
            time.sleep(random.uniform(*BaseBehavior.pause_time))
        elif action == "scroll_up":
            scroll_length = random.randint(
                self.config.static_config.min_scroll_step,
                self.config.static_config.max_scroll_step,
            )
            self.logger.debug("Trying to scroll up %d", scroll_length)
            self.page.scroll.up(pixel=scroll_length)
        elif action == "pause":
            pause_time = random.uniform(1, 3)
            self.logger.debug("Pausing for %.2f seconds", pause_time)
            time.sleep(pause_time)
        elif action == "jump":
            self.logger.debug("Jumping to the bottom of the page")
            self.page.scroll.to_bottom()
            # self.page.scroll.to_see("@class=album-photo my-2")

        return action == "scrolled_up"

    # def safe_scroll(self, target_position):
    #     """DrissionPage does not need safe_scroll."""
    #     current_position = self.get_current_position()
    #     step = random.uniform(
    #         self.config.download.min_scroll_step,
    #         self.config.download.max_scroll_step,
    #     )

    #     while abs(current_position - target_position) > step:
    #         self.page.run_js(f"window.scrollTo(0, {current_position + step});")
    #         time.sleep(random.uniform(0.005, 0.1))
    #         new_position = self.get_current_position()
    #         if new_position == current_position:
    #             self.logger.debug(
    #                 "Cannot continue scrolling, target: %d, current: %d", target_position, current_position
    #             )
    #             break
    #         current_position = new_position
    #     self.page.run_js(f"window.scrollTo(0, {target_position});")
    #     return self.get_current_position()

    def get_current_position(self) -> float:
        page_location: float = self.page.run_js("return window.pageYOffset;")
        self.logger.debug("Current vertical position %d", page_location)
        return page_location

    def get_page_height(self) -> float:
        page_height: float = self.page.run_js("return document.body.scrollHeight;")
        self.logger.debug("Total page height %d", page_height)
        return page_height

    def wait_for_content_load(self) -> None:
        try:
            # wait until the callable return true. default time_out=10
            wait_until(lambda: self.page.states.ready_state == "complete", timeout=5)
        except TimeoutError:
            self.logger.warning("Timeout waiting for new content to load")
