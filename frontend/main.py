"""
/*
* Mobile Chat App to freely communicate with an LLM locally on your mobile device, to chat without surveillance.
* Main file (main.py) SOURCE CODE.
* Copyright (C) 2025  LTS-VVE
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by the Free Software Foundation,
* either version 3 of the License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
* See the GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License along with this program.
* If not, see <http://www.gnu.org/licenses/>.
*/
"""
import flet as ft
import os
import sys
import json
import time
import re
import urllib.request
import threading
from datetime import datetime
from translations import get_translation
from strict import strict_content

# Define file paths for persistent storage
SETTINGS_FILE = "settings.json"
CHAT_HISTORY_FILE = "chat_history.json"
RESPONSES_FILE = "responses.txt"

# Global language (updated during setup)
current_language = "en"

# Global language options shared across setup screens
LANGUAGE_OPTIONS = [
    ft.dropdown.Option("en", "English (en)"),
    ft.dropdown.Option("sq", "Shqip (sq)"),
    ft.dropdown.Option("de", "Deutsch (de)"),
    ft.dropdown.Option("da", "Dansk (da)"),
    ft.dropdown.Option("hu", "Magyar (hu)"),
    ft.dropdown.Option("ga", "Gaeilge (ga)"),
    ft.dropdown.Option("it", "Italiano (it)"),
    ft.dropdown.Option("no", "Norsk (no)"),
    ft.dropdown.Option("uk", "українська (uk)"),
    ft.dropdown.Option("ro", "Română (ro)"),
    ft.dropdown.Option("ru", "Русский (ru)"),
    ft.dropdown.Option("es", "Español (es)"),
    ft.dropdown.Option("fr", "Français (fr)"),
    ft.dropdown.Option("sv", "svenska (sv)"),
    ft.dropdown.Option("zh", "简体中文 (zh)"),
    ft.dropdown.Option("zh-hk", "粵語 (Cantonese) (zh-hk)"),
    ft.dropdown.Option("ja", "日本語 (ja)"),
    ft.dropdown.Option("ko", "한국어 (ko)"),
    ft.dropdown.Option("hi", "हिंदी (hi)"),
    ft.dropdown.Option("ta", "தமிழ் (ta)"),
    ft.dropdown.Option("he", "עִברִית (he)"),
    ft.dropdown.Option("ar", "عربي (ar)"),
    ft.dropdown.Option("am", "አማርኛ (am)"),
    ft.dropdown.Option("sw", "Kiswahili (sw)"),
    ft.dropdown.Option("fa", "فارسی (fa)"),
    ft.dropdown.Option("ne", "नेपाली (ne)"),
    ft.dropdown.Option("tl", "Tagalog/Filipino (tl)"),
    ft.dropdown.Option("bg", "Български (bg)"),
    ft.dropdown.Option("th", "ภาษาไทย (th)"),
    ft.dropdown.Option("pt", "Português (pt)"),
    ft.dropdown.Option("pt-br", "Português (Brasil) (pt-br)"),
    ft.dropdown.Option("id", "Bahasa Indonesia (id)"),
    ft.dropdown.Option("el", "ελληνικά (el)"),
    ft.dropdown.Option("hr", "Hrvatski (hr)"),
    ft.dropdown.Option("sr", "Srpski (sr)"),
    ft.dropdown.Option("fi", "Suomi (fi)"),
    ft.dropdown.Option("mk", "македонски (mk)"),
    ft.dropdown.Option("pl", "Polski (pl)"),
    ft.dropdown.Option("tr", "Türkçe (tr)"),
    ft.dropdown.Option("ka", "ქართული (ka)"),
    ft.dropdown.Option("kk", "Қазақ тілі (kk)"),
    ft.dropdown.Option("ms", "Melayu (ms)"),
    ft.dropdown.Option("vi", "Tiếng Việt (vi)"),
    ft.dropdown.Option("cs", "čeština (cs)"),
    ft.dropdown.Option("la", "Latin (la)"),
]

# Global generation control variables
is_generating = False
stop_generation_flag = False

def translate(key):
    global current_language
    return get_translation(current_language, key)

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            return (
                settings.get("ip", "127.0.0.1"),
                settings.get("port", 5000),
                settings.get("username", "User"),
                settings.get("theme_mode", "dark"),
                settings.get("temperature", 0.7),
                settings.get("language", "en"),
                settings.get("custom_endpoint", "/api/v1/query"),
                settings.get("filter_mode", "on"),
            )
    except (FileNotFoundError, json.JSONDecodeError):
        return "127.0.0.1", 5000, "User", "dark", 0.7, "en", "/api/v1/query", "on"

def save_settings(ip, port, username, theme_mode, temperature, custom_endpoint, filter_mode):
    global current_language
    settings = {
        "ip": ip,
        "port": port,
        "username": username,
        "theme_mode": theme_mode,
        "temperature": temperature,
        "language": current_language,
        "custom_endpoint": custom_endpoint,
        "filter_mode": filter_mode,
    }
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)

def load_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_chat_history(chat_messages):
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(chat_messages, file)

def erase_all_chats(page):
    def on_confirm_click(e):
        global chat_history
        chat_history = []
        save_chat_history(chat_history)
        try:
            os.remove(CHAT_HISTORY_FILE)
            os.remove(RESPONSES_FILE)
        except FileNotFoundError:
            pass
        page.chat_area.controls.clear()
        dialog.open = False
        page.update()
    def on_cancel_click(e):
        dialog.open = False
        page.update()
    dialog = ft.AlertDialog(
        title=ft.Text(translate("deletion_confirmation")),
        content=ft.Text(translate("deletion_warning")),
        actions=[
            ft.ElevatedButton(
                translate("confirm"),
                on_click=on_confirm_click,
                style=ft.ButtonStyle(bgcolor=ft.colors.RED_600, color="white")
            ),
            ft.ElevatedButton(translate("cancel"), on_click=on_cancel_click)
        ]
    )
    dialog.open = True
    page.add(dialog)
    page.update()

def get_ollama_response(message, ip, port, temperature, custom_endpoint):
    url = f"http://{ip}:{port}{custom_endpoint}"
    headers = {"Content-Type": "application/json"}
    data = {"prompt": message, "temperature": temperature}
    try:
        data_bytes = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
        response_data = ""
        with urllib.request.urlopen(req) as response:
            for line in response:
                line = line.decode("utf-8")
                if line.startswith("data:"):
                    response_part = json.loads(line[5:]).get("response", "")
                    response_data = response_part
                    print(response_part)
        return response_data
    except Exception as e:
        return f"Failed to connect to server at {url}. {translate('check_ip_port')} Error: {str(e)}"

def save_ollama_response(response):
    with open(RESPONSES_FILE, "a") as file:
        file.write(response + "\n")

def create_glowing_chat_bubble(message, is_user=False, theme_mode="dark", bgcolor="#424242", glow_color="#8A2BE2", text_color=None):
    if text_color is None:
        text_color = "white" if theme_mode == "dark" else "black"
    return ft.Container(
        content=ft.Text(
            message,
            color=text_color,
            size=14,
            weight=ft.FontWeight.NORMAL,
            selectable=True,
            text_align=ft.TextAlign.LEFT if not is_user else ft.TextAlign.RIGHT,
        ),
        bgcolor=ft.colors.with_opacity(0.3, bgcolor),
        border_radius=20,
        padding=ft.padding.all(12),
        animate=ft.animation.Animation(300, "easeOut"),
        animate_opacity=ft.animation.Animation(300, "easeOut"),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.colors.with_opacity(0.3, glow_color),
            offset=ft.Offset(0, 0)
        ),
        ink=True,
        expand=True,
        margin=ft.margin.only(left=0 if is_user else 8, right=8 if is_user else 0),
    )

def get_greeting():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return translate("good_morning")
    elif 12 <= current_hour < 18:
        return translate("good_afternoon")
    else:
        return translate("good_evening")

def stream_ai_response(user_message, ip, port, temperature, custom_endpoint, ai_bubble, page, loading_color):
    global stop_generation_flag
    message_md = ft.Markdown("", selectable=True)
    progress_ring = ft.ProgressRing(width=20, height=20, color=loading_color)
    cursor = ft.Text("|", size=14, weight=ft.FontWeight.BOLD)
    ai_bubble.content = ft.Column([message_md, progress_ring, cursor])
    page.update()

    cursor_active = True
    def blink_cursor():
        nonlocal cursor_active
        while cursor_active:
            cursor.visible = not cursor.visible
            page.update()
            time.sleep(0.5)
        cursor.visible = False
        page.update()
    cursor_thread = threading.Thread(target=blink_cursor)
    cursor_thread.start()

    full_response = ""
    url = f"http://{ip}:{port}{custom_endpoint}"
    headers = {"Content-Type": "application/json"}
    data = {"prompt": user_message, "temperature": temperature}
    try:
        data_bytes = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            for line in response:
                if stop_generation_flag:
                    break
                line = line.decode("utf-8")
                if line.startswith("data:"):
                    try:
                        json_content = json.loads(line[5:].strip())
                        chunk = json_content.get("response", "")
                    except Exception:
                        chunk = ""
                    full_response += chunk
                    message_md.value = full_response
                    page.update()
    except Exception as e:
        full_response = f"Error: {str(e)}"
        message_md.value = full_response
        page.update()

    cursor_active = False
    cursor_thread.join()
    if progress_ring in ai_bubble.content.controls:
        ai_bubble.content.controls.remove(progress_ring)
    if cursor in ai_bubble.content.controls:
        ai_bubble.content.controls.remove(cursor)
    page.update()
    return full_response

def typewriter_animation(response_text, chat_row, page, delay=0.001):
    chat_bubble = chat_row.controls[1]
    message_text = ft.Text("", size=14, weight=ft.FontWeight.NORMAL)
    chat_bubble.content = ft.Column([message_text])
    cursor = ft.Text("|", size=14, weight=ft.FontWeight.BOLD)
    chat_bubble.content.controls.append(cursor)
    page.update()

    cursor_active = True
    def blink_cursor():
        nonlocal cursor_active
        while cursor_active:
            cursor.visible = not cursor.visible
            page.update()
            time.sleep(0.2)
        cursor.visible = False
        page.update()
    cursor_thread = threading.Thread(target=blink_cursor)
    cursor_thread.start()

    message = ""
    for char in response_text:
        message += char
        message_text.value = message
        page.update()
        time.sleep(delay)
    
    cursor_active = False
    cursor_thread.join()
    if cursor in chat_bubble.content.controls:
        chat_bubble.content.controls.remove(cursor)
    page.update()

def run_setup(page: ft.Page, ip, port, username, theme_mode, temperature, language, custom_endpoint, filter_mode):
    wizard_state = {
        "language": language,
        "theme_mode": theme_mode,
        "username": username
    }
    step_index = 0
    setup_container = ft.Container(expand=True)
    
    install_commands = """THIS IS ONLY A TEST
Please copy and paste the following commands into Termux to install the required backend components.
If already installed, you may continue to the next step.

Example:
pkg install python
pip install ollama-sdk
...
"""
    def go_next(value=None):
        nonlocal step_index, wizard_state
        global current_language
        if step_index == 0:
            wizard_state["language"] = value
            current_language = value
        elif step_index == 1:
            pass
        elif step_index == 2:
            wizard_state["theme_mode"] = value
        elif step_index == 3:
            wizard_state["username"] = value if value.strip() != "" else "User"
        step_index += 1
        setup_container.content = render_step(step_index)
        page.update()
        if step_index == 6:
            current_language = wizard_state["language"]
            save_settings(ip, port, wizard_state["username"], wizard_state["theme_mode"], temperature, custom_endpoint, filter_mode)
            exit_container = ft.Container(
                expand=True,
                bgcolor="#000000",
                alignment=ft.Alignment.CENTER,
                content=ft.Text(translate("exiting"), color="white", size=20)
            )
            page.clean()
            page.add(exit_container)
            page.update()
            time.sleep(1)
            sys.exit(0)
    
    def go_back():
        nonlocal step_index
        if step_index > 0:
            step_index -= 1
            setup_container.content = render_step(step_index)
            page.update()

    def render_step(step):
        def nav_row():
            controls = []
            if step > 0 and step < 6:
                controls.append(ft.IconButton(
                    icon=ft.icons.ARROW_BACK_ROUNDED,
                    icon_color="#595959",
                    on_click=lambda e: go_back()
                ))
            if step < 6:
                controls.append(ft.IconButton(
                    icon=ft.icons.ARROW_FORWARD_ROUNDED,
                    icon_color="white",
                    on_click=lambda e: go_next(input_value.value if input_value is not None else None)
                ))
            return ft.Row(controls, alignment=ft.MainAxisAlignment.END)
        
        input_value = None
        if step == 0:
            return ft.Column(
                [
                    ft.Icon(ft.icons.PUBLIC, size=60, color="white"),
                    ft.Text(
                        translate("setup_choose_language") if translate("setup_choose_language") != "" else "Setup: Choose App Language",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Dropdown(
                        value=wizard_state["language"] if wizard_state["language"] else "en",
                        options=LANGUAGE_OPTIONS,
                        width=300,
                        on_change=lambda e: go_next(e.control.value)
                    ),
                    nav_row()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        elif step == 1:
            return ft.Column(
                [
                    ft.Icon(ft.icons.SYSTEM_UPDATE_ALT_ROUNDED, size=60, color="white"),
                    ft.Text(
                        translate("setup_install_instructions") if translate("setup_install_instructions") != "" else "Setup: Installation Instructions",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(
                        content=ft.TextField(value=install_commands, read_only=True, multiline=True, expand=True),
                        padding=10,
                        bgcolor="#303030",
                        border_radius=10,
                    ),
                    ft.IconButton(
                        icon=ft.icons.COPY,
                        icon_color="white",
                        on_click=lambda e: page.set_clipboard(install_commands)
                    ),
                    nav_row()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        elif step == 2:
            return ft.Column(
                [
                    ft.Icon(ft.icons.CONTRAST, size=60, color="white"),
                    ft.Text(
                        translate("setup_choose_theme") if translate("setup_choose_theme") != "" else "Setup: Choose The Theme",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.RadioGroup(
                        content=ft.Column([
                            ft.Radio(label=translate("light_mode") if translate("light_mode") != "" else "Light Mode", value="light"),
                            ft.Radio(label=translate("dark_mode") if translate("dark_mode") != "" else "Dark Mode", value="dark"),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        value=wizard_state["theme_mode"],
                        on_change=lambda e: go_next(e.control.value)
                    ),
                    nav_row()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        elif step == 3:
            input_value = ft.TextField(
                hint_text=translate("setup_enter_username") if translate("setup_enter_username") != "" else "Enter your name...",
                value=wizard_state["username"],
                width=300
            )
            return ft.Column(
                [
                    ft.Icon(ft.icons.PERSON_ROUNDED, size=60, color="white"),
                    ft.Text(
                        translate("setup_choose_username") if translate("setup_choose_username") != "" else "Setup: Choose Your Name",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    input_value,
                    nav_row()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        elif step == 4:
            status_text = ft.Text(translate("not_connected"), size=16, color="red")
            def test_connection(e):
                try:
                    url = f"http://{ip}:{port}/api/v1/status"
                    response = urllib.request.urlopen(url, timeout=2)
                    if response.status == 200:
                        status_text.value = translate("connected")
                        status_text.color = "green"
                    else:
                        status_text.value = translate("not_connected")
                        status_text.color = "red"
                except Exception:
                    status_text.value = translate("not_connected")
                    status_text.color = "red"
                page.update()
            return ft.Column(
                [
                    ft.Icon(ft.icons.DNS_ROUNDED, size=60, color="white"),
                    ft.Text(
                        translate("setup_internet_setup") if translate("setup_internet_setup") != "" else "Setup: Check Backend Connection",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.ElevatedButton(
                        translate("test_connection") if translate("test_connection") != "" else "Test Connection",
                        on_click=test_connection,
                        bgcolor="black",
                        color="white"
                    ),
                    status_text,
                    nav_row()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        elif step == 5:
            return ft.Column(
                [
                    ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=60, color="GREEN"),
                    ft.Text(
                        translate("setup_complete"),
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        translate("restart_required"),
                        size=16
                    ),
                    ft.ElevatedButton(
                        translate("ok"),
                        on_click=lambda e: go_next(),
                        bgcolor=ft.colors.BLACK,
                        color="white"
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
    setup_container.content = render_step(step_index)
    page.views.append(ft.View("/setup", controls=[setup_container], padding=20))
    page.go("/setup")

def main(page: ft.Page):
    global current_language, is_generating, stop_generation_flag
    if not os.path.exists(SETTINGS_FILE):
        run_setup(page, "127.0.0.1", 5000, "User", "dark", 0.7, "en", "/api/v1/query", "on")
        return

    ip, port, username, theme_mode, temperature, current_language, custom_endpoint, filter_mode = load_settings()
    chat_history = load_chat_history()

    page.title = "ReliaChat"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 400
    page.window_height = 700
    page.window_icon = "assets/icon.png"
    
    if theme_mode == "light":
        page.bgcolor = "#FFFFFF"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme_color = ft.colors.PURPLE
    else:
        page.bgcolor = "#000000"
        page.theme_mode = ft.ThemeMode.DARK
        page.theme_color = ft.colors.PURPLE
    page.update()

    splash_image = "assets/light_splash.png" if theme_mode == "light" else "assets/dark_splash.png"
    splash_screen = ft.Container(
        content=ft.Image(src=splash_image, expand=True),
        expand=True,
        bgcolor="#FFFFFF" if theme_mode == "light" else "#000000",
        animate_opacity=ft.animation.Animation(1000, "easeInOut")
    )
    def show_splash_screen():
        page.add(splash_screen)
        page.update()
        time.sleep(2)
        splash_screen.visible = False
        page.remove(splash_screen)
        page.update()
    show_splash_screen()

    sidebar_text_color = "black" if theme_mode == "light" else "white"
    loading_color = "black" if theme_mode == "light" else "white"

    def toggle_sidebar(e):
        sidebar.visible = not sidebar.visible
        page.update()

    def copy_to_clipboard(e, text):
        page.set_clipboard(text)
        page.snack_bar = ft.SnackBar(ft.Text(translate("copied_to_clipboard")))
        page.snack_bar.open = True
        page.update()

    def update_language(language):
        nonlocal ip, port, username, theme_mode, temperature, custom_endpoint, filter_mode
        global current_language
        current_language = language
        save_settings(ip, port, username, theme_mode, temperature, custom_endpoint, filter_mode)
        page.update()

    def show_settings_dialog():
        ip, port, username, theme_mode, temperature, language, custom_endpoint, filter_mode = load_settings()
        connection_status = translate("not_connected")
        model_name = "Unknown"
        try:
            response = urllib.request.urlopen(f"http://{ip}:{port}/api/v1/status", timeout=2)
            if response.status == 200:
                response_data = json.loads(response.read().decode("utf-8"))
                connection_status = translate("connected")
                model_name = response_data.get("model_name", "Unknown")
        except Exception as e:
            print(f"Error checking status: {e}")
        ip_field = ft.TextField(
            hint_text=translate("local_ip"),
            value=ip,
            autofocus=True,
            expand=True,
            color="black" if theme_mode == "light" else "white",
            bgcolor=ft.colors.GREY_300 if theme_mode == "light" else ft.colors.GREY_800,
            border_radius=20,
        )
        port_field = ft.TextField(
            hint_text=translate("port"),
            value=str(port),
            expand=True,
            color="black" if theme_mode == "light" else "white",
            bgcolor=ft.colors.GREY_300 if theme_mode == "light" else ft.colors.GREY_800,
            border_radius=20,
        )
        username_field = ft.TextField(
            hint_text=translate("username"),
            value=username,
            expand=True,
            color="black" if theme_mode == "light" else "white",
            bgcolor=ft.colors.GREY_300 if theme_mode == "light" else ft.colors.GREY_800,
            border_radius=20,
        )
        custom_endpoint_field = ft.TextField(
            hint_text=translate("custom_endpoint"),
            value=custom_endpoint,
            expand=True,
            color="black" if theme_mode == "light" else "white",
            bgcolor=ft.colors.GREY_300 if theme_mode == "light" else ft.colors.GREY_800,
            border_radius=20,
        )
        temperature_input = ft.TextField(
            hint_text=translate("temperature"),
            value=str(temperature),
            expand=True,
            color="black" if theme_mode == "light" else "white",
            bgcolor=ft.colors.GREY_300 if theme_mode == "light" else ft.colors.GREY_800,
            border_radius=20,
        )
        filter_toggle = ft.Switch(
            value=(filter_mode == "on"),
            active_color="white",
            inactive_thumb_color="gray",
            active_track_color="red",
            inactive_track_color="gray",
            on_change=lambda e: None,
        )
        theme_toggle = ft.Switch(
            value=(theme_mode == "light"),
            active_color="white",
            inactive_thumb_color="gray",
            active_track_color="#86759c",
            inactive_track_color="gray",
            on_change=lambda e: None,
        )
        connection_status_text = ft.Text(
            connection_status,
            color="green" if connection_status == translate("connected") else "red",
            size=12,
            weight=ft.FontWeight.BOLD,
        )
        language_dropdown = ft.Dropdown(
            value=current_language,
            options=LANGUAGE_OPTIONS,
            on_change=lambda e: update_language(e.control.value),
        )
        def save_settings_action(e):
            save_settings(
                ip_field.value,
                int(port_field.value),
                username_field.value,
                "light" if theme_toggle.value else "dark",
                float(temperature_input.value),
                custom_endpoint_field.value,
                "on" if filter_toggle.value else "off",
            )
            dlg.open = False
            page.update()
        def cancel_settings_action(e):
            dlg.open = False
            page.update()
        content = ft.Column([
            ip_field,
            port_field,
            username_field,
            language_dropdown,
            custom_endpoint_field,
            ft.Row([ft.Text(translate("filter_mode")), filter_toggle]),
            ft.Row([ft.Text(translate("dark_mode")), theme_toggle, ft.Text(translate("light_mode"))],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([ft.Text(translate("temperature")), temperature_input]),
            ft.Row([ft.Text(translate("connection_status")), connection_status_text]),
            ft.Row([
                ft.ElevatedButton(
                    translate("cancel"),
                    on_click=cancel_settings_action,
                    bgcolor=ft.colors.RED_800,
                    color="white",
                    expand=True
                ),
                ft.ElevatedButton(
                    translate("save"),
                    on_click=save_settings_action,
                    bgcolor=ft.colors.WHITE,
                    color="black",
                    expand=True
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
        ], spacing=2)
        dlg_content = ft.Container(
            content=content,
            padding=10,
            bgcolor="#FFFFFF" if theme_mode == "light" else "#000000",
            border_radius=20,
        )
        dlg = ft.AlertDialog(
            title=ft.Text(translate("settings"), color="black" if theme_mode == "light" else "white"),
            content=dlg_content,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()
    chat_area = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    page.chat_area = chat_area

    def send_message(e=None):
        global is_generating, stop_generation_flag
        if input_field.value.strip():
            user_message = input_field.value
            user_bubble = create_glowing_chat_bubble(
                user_message,
                is_user=True,
                theme_mode=theme_mode,
                bgcolor="#8f8f8f",
                glow_color="#8f8f8f",
                text_color=sidebar_text_color
            )
            user_row = ft.Row(
                [ft.Container(width=40), user_bubble, ft.Icon(ft.icons.PERSON_ROUNDED, color="#a3a3a3")],
                alignment=ft.MainAxisAlignment.END,
            )
            chat_area.controls.append(user_row)
            page.update()

            ip, port, username, _, temperature, _, custom_endpoint, filter_mode = load_settings()
            if filter_mode != "off" and strict_content(user_message):
                blocked_message = translate("content_blocked")
                ai_bubble = create_glowing_chat_bubble(
                    blocked_message,
                    is_user=False,
                    theme_mode=theme_mode,
                    bgcolor="red",
                    glow_color="red",
                    text_color=sidebar_text_color
                )
                ai_row = ft.Row(
                    [ft.Icon(ft.icons.SHIELD_ROUNDED, color="red"), ai_bubble, ft.Container(width=40)],
                    alignment=ft.MainAxisAlignment.START,
                )
                chat_area.controls.append(ai_row)
                page.update()
                typewriter_animation(blocked_message, ai_row, page)
                chat_history.append({"user": "You", "message": user_message, "is_user": True})
                chat_history.append({"user": "AI", "message": blocked_message, "is_user": False})
                save_chat_history(chat_history)
                input_field.value = ""
                page.update()
                return

            ai_bubble = create_glowing_chat_bubble(
                "",
                is_user=False,
                theme_mode=theme_mode,
                bgcolor=ft.colors.with_opacity(0.3, "#86759c"),
                glow_color="#86759c",
                text_color=sidebar_text_color
            )
            ai_row = ft.Row(
                [
                    ft.Icon(ft.icons.BLUR_ON_ROUNDED, color="#86759c"),
                    ai_bubble,
                    ft.IconButton(
                        ft.icons.COPY,
                        on_click=lambda e: copy_to_clipboard(e, ai_bubble.content.controls[0].value),
                        icon_color="black" if theme_mode == "light" else "white",
                    ),
                    ft.Container(width=40),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
            chat_area.controls.append(ai_row)
            send_icon_button.visible = False
            stop_icon_button.visible = True
            page.update()

            is_generating = True
            stop_generation_flag = False
            def update_ai_response():
                global is_generating, stop_generation_flag
                full_response = stream_ai_response(user_message, ip, port, temperature, custom_endpoint, ai_bubble, page, loading_color)
                is_generating = False
                stop_generation_flag = False
                send_icon_button.visible = True
                stop_icon_button.visible = False
                chat_history.append({"user": "You", "message": user_message, "is_user": True})
                chat_history.append({"user": "AI", "message": full_response, "is_user": False})
                save_chat_history(chat_history)
                save_ollama_response(full_response)
                page.update()
            threading.Thread(target=update_ai_response, daemon=True).start()
            input_field.value = ""
            page.update()

    chat_history = load_chat_history()
    for message in chat_history:
        is_user = message.get("is_user", message["user"] == "You")
        bubble = create_glowing_chat_bubble(
            message["message"],
            is_user=is_user,
            theme_mode=theme_mode,
            bgcolor="#8f8f8f" if is_user else ("red" if message["message"] == translate("content_blocked") else "#86759c"),
            glow_color="#8f8f8f" if is_user else ("red" if message["message"] == translate("content_blocked") else "#86759c"),
            text_color=sidebar_text_color
        )
        if is_user:
            row = ft.Row(
                [ft.Container(width=40), bubble, ft.Icon(ft.icons.PERSON_ROUNDED, color="#a3a3a3")],
                alignment=ft.MainAxisAlignment.END,
            )
        else:
            row = ft.Row(
                [
                    ft.Icon(ft.icons.HISTORY_ROUNDED, color="red" if message["message"] == translate("content_blocked") else "#86759c"),
                    bubble,
                    ft.IconButton(
                        ft.icons.COPY,
                        on_click=lambda e, text=message["message"]: copy_to_clipboard(e, text),
                        icon_color="black" if theme_mode == "light" else "white",
                    ),
                    ft.Container(width=40),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
        chat_area.controls.append(row)

    input_field = ft.TextField(
        hint_text=translate("type_prompt"),
        autofocus=True,
        expand=True,
        on_submit=send_message,
        border_radius=20,
        bgcolor=ft.colors.GREY_200 if theme_mode == "light" else ft.colors.GREY_800,
        color="black" if theme_mode == "light" else "white",
        cursor_color="#BB86FC",
        cursor_width=2,
        text_size=14,
    )

    send_icon_button = ft.IconButton(
        ft.icons.SEND_ROUNDED,
        on_click=send_message,
        icon_color="black" if theme_mode == "light" else "white",
    )
    stop_icon_button = ft.IconButton(
        ft.icons.STOP_CIRCLE_ROUNDED,
        on_click=lambda e: stop_generation(),
        icon_color="red",
        visible=False,
    )

    def stop_generation():
        global stop_generation_flag, is_generating
        if is_generating:
            stop_generation_flag = True
            is_generating = False
            send_icon_button.visible = True
            stop_icon_button.visible = False
            page.update()

    greeting = get_greeting()
    top_bar = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    ft.icons.MENU_ROUNDED,
                    on_click=toggle_sidebar,
                    icon_color="black" if theme_mode == "light" else "white",
                    bgcolor=None,
                ),
                ft.Text(
                    f"{greeting}, {username}",
                    size=16,
                    color="black" if theme_mode == "light" else "white",
                    weight=ft.FontWeight.BOLD,
                ),
                ft.IconButton(
                    ft.icons.BRIGHTNESS_HIGH_ROUNDED if theme_mode == "light" else ft.icons.BRIGHTNESS_LOW_SHARP,
                    on_click=lambda e: page.update(),
                    icon_color="black" if theme_mode == "light" else "white",
                    disabled=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=10,
        bgcolor=ft.colors.GREY_200 if theme_mode == "light" else ft.colors.GREY_900,
        border_radius=20,
    )

    disclaimer_text = ft.Text(
        translate("disclaimer"),
        color="gray",
        size=9,
        weight=ft.FontWeight.W_400,
    )

    warning_text = ft.Row(
        [
            ft.Icon(ft.icons.WARNING_ROUNDED, color=sidebar_text_color),
            ft.Text(
                translate("warn_setup_local_server"),
                color="gray",
                size=11.5,
                weight=ft.FontWeight.BOLD,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=10,
    )

    sidebar = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(translate("settings"), size=20, weight=ft.FontWeight.BOLD, color=sidebar_text_color),
                        ft.IconButton(ft.icons.MENU_OPEN_ROUNDED, on_click=toggle_sidebar, icon_color=sidebar_text_color),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.TextButton(
                    translate("settings"),
                    icon="SETTINGS_OUTLINED",
                    on_click=lambda _: show_settings_dialog(),
                    style=ft.ButtonStyle(color=sidebar_text_color, elevation=2),
                ),
                ft.TextButton(
                    translate("help"),
                    icon="SUPPORT_OUTLINED",
                    on_click=lambda _: page.launch_url("https://relia.rf.gd/docs"),
                    style=ft.ButtonStyle(color=sidebar_text_color, elevation=2),
                ),
                ft.TextButton(
                    translate("privacy_policy"),
                    icon="POLICY_OUTLINED",
                    on_click=lambda _: page.launch_url("https://relia.rf.gd/privacy-policy"),
                    style=ft.ButtonStyle(color=sidebar_text_color, elevation=2),
                ),
                ft.TextButton(
                    translate("about"),
                    icon="INFO_OUTLINED",
                    on_click=lambda _: page.launch_url("https://relia.rf.gd/about"),
                    style=ft.ButtonStyle(color=sidebar_text_color, elevation=2),
                ),
                ft.TextButton(
                    translate("terms_of_use"),
                    icon="RULE_OUTLINED",
                    on_click=lambda _: page.launch_url("https://relia.rf.gd/terms-and-conditions"),
                    style=ft.ButtonStyle(color=sidebar_text_color, elevation=2),
                ),
                ft.TextButton(
                    translate("erase_all_chats"),
                    icon="DELETE_FOREVER_OUTLINED",
                    on_click=lambda _: erase_all_chats(page),
                    style=ft.ButtonStyle(color=sidebar_text_color, bgcolor=ft.colors.RED_600, elevation=2),
                ),
                ft.TextButton(
                    "ReliaChat's Work",
                    disabled=False,
                    icon="ADD_LINK_OUTLINED",
                    on_click=lambda _: page.launch_url("https://relia.rf.gd/credits"),
                    style=ft.ButtonStyle(color=sidebar_text_color),
                ),
                ft.Text(translate("version"), size=10, color=sidebar_text_color),
            ],
            spacing=10,
        ),
        width=260,
        height=9000,
        visible=False,
        bgcolor=ft.colors.with_opacity(0.67, "#FFFFFF" if theme_mode == "light" else "#000000"),
        border_radius=10,
        blur=ft.Blur(5, 5),
        animate=ft.animation.Animation(1000, "easeInOut"),
        ink=True,
    )

    layout = ft.Stack(
        [
            ft.Column(
                [
                    top_bar,
                    disclaimer_text,
                    warning_text,
                    ft.Container(
                        content=chat_area,
                        expand=True,
                        bgcolor="#FFFFFF" if theme_mode == "light" else "#000000",
                        padding=10,
                        border_radius=20,
                    ),
                    ft.Row(
                        [
                            input_field,
                            send_icon_button,
                            stop_icon_button,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                expand=True,
            ),
            sidebar,
        ],
        expand=True,
    )

    page.add(layout)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
