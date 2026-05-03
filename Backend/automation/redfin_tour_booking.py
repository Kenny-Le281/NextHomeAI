from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
from models.booking_request import BookingRequest
import re

def _generate_time_slots():
    slots = []
    for hour in range(9, 21):
        minutes = [0, 30] if hour < 20 else [0]

        for minute in minutes:
            h = hour % 12 or 12
            suffix = "am" if hour < 12 else "pm"
            slots.append(f"{h}:{minute:02d} {suffix}")
    return slots

def _normalize_time_to_nearest_half_hour(preferred_time: str) -> str:
    if not preferred_time:
        raise ValueError("Missing preferred time")

    text = preferred_time.strip().lower().replace(".", "")

    match = re.search(r"(\d{1,2})(?::(\d{1,2}))?\s*(am|pm)?", text)

    if not match:
        raise ValueError(f"Invalid preferred time: {preferred_time}")

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    suffix = match.group(3)

    if suffix is None:
        raise ValueError(
            f"Preferred time must include am or pm: {preferred_time}"
        )

    if hour < 1 or hour > 12:
        raise ValueError(f"Invalid hour in preferred time: {preferred_time}")

    if minute < 0 or minute > 59:
        raise ValueError(f"Invalid minute in preferred time: {preferred_time}")

    if suffix == "am":
        hour_24 = 0 if hour == 12 else hour
    else:
        hour_24 = 12 if hour == 12 else hour + 12

    total_minutes = hour_24 * 60 + minute
    rounded_total_minutes = round(total_minutes / 30) * 30

    rounded_hour_24 = rounded_total_minutes // 60
    rounded_minute = rounded_total_minutes % 60

    earliest = 9 * 60
    latest = 20 * 60

    if rounded_total_minutes < earliest:
        rounded_hour_24 = 9
        rounded_minute = 0
    elif rounded_total_minutes > latest:
        rounded_hour_24 = 20
        rounded_minute = 0

    rounded_suffix = "am" if rounded_hour_24 < 12 else "pm"
    rounded_hour_12 = rounded_hour_24 % 12 or 12

    return f"{rounded_hour_12}:{rounded_minute:02d} {rounded_suffix}"

def _normalize_listing_url(url: str) -> str:
    url = url.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return f"https://www.redfin.ca{url}"
    return f"https://www.redfin.ca/{url.lstrip('/')}"


def _click_request_showing(page):
    page.wait_for_timeout(5000)

    button = page.get_by_role("button", name="Request showing")

    button.wait_for(state="visible", timeout=15000)

    button.click()

    print("Clicked Request showing button")


def _click_next(page):

    page.get_by_role("button", name="Next", exact=True).click()

    print("Clicked Next")

def _select_virtual_tour_option(page):

    page.get_by_role("option", name="Video tour").click()

    print("Selected virtual tour")

def _skip_verification_code(page):

    page.get_by_role("button", name="Can't receive a text?").click()

    print("Entered verification code")

def _enter_virtual_tour_info(page, booking):

    page.get_by_role("option", name="Zoom").click()
    page.get_by_role("textbox", name="Email").click()
    page.get_by_role("textbox", name="Email").fill(booking.email)

    print("Entered Zoom information")


def _select_date(page, preferred_date):

    preferred_dateString = preferred_date.strftime("%Y-%m-%d")
    target_date = datetime.strptime(preferred_dateString, "%Y-%m-%d")
    today = datetime.today()

    diff_days = (target_date.date() - today.date()).days
    if diff_days < 0:
        raise ValueError("Cannot book a past date")
    

    weeks_ahead = diff_days // 7


    dialog = page.locator("#bp-dialog-content")

    for _ in range(weeks_ahead):
        next_btn = dialog.locator("div[role='button'][aria-label='next']")
        next_btn.wait_for(state="visible", timeout=10000)
        next_btn.click()

    day_text = (
        target_date.strftime("%A")
        + str(target_date.day)
        + target_date.strftime("%b")
    )

    page.get_by_text(day_text, exact=True).click()
    page.wait_for_timeout(5000)
    print("Clicked day button")


def _enter_user_info(page, booking):

    page.get_by_role("textbox", name="First Name").click()
    page.get_by_role("textbox", name="First Name").fill(booking.full_name.split()[0])
    page.get_by_role("textbox", name="Last Name").click()
    page.get_by_role("textbox", name="Last Name").fill(booking.full_name.split()[1])
    email_input = page.get_by_role("textbox", name="Email")
    if email_input.count() > 0:
        email_input.first.click()
        email_input.fill(booking.email)
    page.get_by_role("textbox", name="Phone").click()
    page.get_by_role("textbox", name="Phone").fill(booking.phone)
    page.get_by_role("textbox", name="Notes (optional)").click()
    notes_input = page.get_by_role("textbox", name="Notes (optional)")
    if booking.message:
        notes_input.click()
        notes_input.fill(booking.message)
    page.get_by_role("radio", name="No").check()
    page.get_by_role("checkbox", name="Email").check()
    page.get_by_role("checkbox", name="Phone").check()
    page.get_by_role("checkbox", name="Text").check()

    print("Entered user info")


def _select_time_if_available(page, preferred_time):
    print("Checking for time selection...")

    dialog = page.locator("#bp-dialog-content")
    dialog.wait_for(state="visible")

    time_buttons = dialog.locator("button:has-text('am'), button:has-text('pm')")

    if time_buttons.count() == 0:
        print("No time selection UI present → skipping")
        return True

    print("Time selection UI detected")

    all_slots = _generate_time_slots()
    preferred_time = _normalize_time_to_nearest_half_hour(preferred_time)
    print(f"Normalized preferred time: {preferred_time}")

    start_index = all_slots.index(preferred_time) if preferred_time in all_slots else 0

    search_order = all_slots[start_index:] + all_slots[:start_index]

    time_dropdown = dialog.locator("button").filter(has_text="am").or_(dialog.locator("button").filter(has_text="pm")).first
    time_dropdown.click()

    for slot in search_order:
        button = dialog.page.get_by_role("button", name=slot)

        if button.count() > 0 and button.is_enabled():
            button.scroll_into_view_if_needed()
            button.click()
            print(f"Selected time: {slot}")
            return True

    print("No available time slots after preferred time")
    return False


def submit_redfin_tour_request(booking: BookingRequest, headless: bool = False,):
    if not booking.listing_url:
        return {
            "status": "error",
            "message": "Missing listing URL."
        }

    listing_url = _normalize_listing_url(booking.listing_url)
    page = None

    try:
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=headless)
            context = browser.new_context()
            page = context.new_page()

            page.goto(listing_url)

            _click_request_showing(page)
            
            _select_date(page, booking.preferred_date)

            _select_time_if_available(page, booking.preferred_time)

            if booking.virtual_tour:
                _select_virtual_tour_option(page)

            _click_next(page)

            if booking.virtual_tour:
                _enter_virtual_tour_info(page, booking)
                _click_next(page)

            _enter_user_info(page, booking)

            _click_next(page)

            _skip_verification_code(page)

            page.wait_for_timeout(5000)
            
            browser.close()

    except PlaywrightTimeoutError:
        return {
            "status": "error",
            "message": "Timed out while interacting with the Request Showing flow."
        }
    except Exception as exc:

        message = str(exc)
        if "Executable doesn't exist" in message:
            return {
                "status": "error",
                "message": (
                    "Playwright browser binaries are not installed. "
                    "Run: playwright install"
                ),
            }

        return {
            "status": "error",
            "message": f"Unexpected Playwright error: {exc}",
        }