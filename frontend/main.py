"""
/*
* Mobile Chat App to freely communicate with an LLM locally on your mobile device, to chat without surveillance.
* Main file (main.py) SOURCE CODE.
* Copyright (C) 2025  LTS-VVE
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
"""
import flet as ft
import os
import json
import time
import urllib.request
import threading
from datetime import datetime
from translations import get_translation
from strict import strict_content

# Define file paths for persistent storage
SETTINGS_FILE = "settings.json"
CHAT_HISTORY_FILE = "chat_history.json"
RESPONSES_FILE = "responses.txt"

current_language = "en"

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
    # Confirmation dialog without unsupported animation parameters.
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
                    response_data = response_part  # Use the latest part.
                    print(response_part)
        return response_data
    except Exception as e:
        return f"Failed to connect to server at {url}. Please check the IP and Port. Error: {str(e)}"

def save_ollama_response(response):
    with open(RESPONSES_FILE, "a") as file:
        file.write(response + "\n")

def create_glowing_chat_bubble(message, is_user=False, theme_mode="dark", bgcolor="#424242", glow_color="#8A2BE2"):
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

def typewriter_animation(response_text, chat_row, page, delay=0.02):
    # Adjust animation speed depending on word count.
    words = response_text.split()
    if len(words) > 20:
        delay = 0.005  # Speed up longer responses.
    chat_bubble = chat_row.controls[1]
    message = ""
    # Show loading messages first.
    loading_messages = [translate("processing_query"), translate("analyzing"), translate("analyzing"), translate("analyzing")]
    for msg in loading_messages:
        chat_bubble.content.value = msg
        page.update()
        time.sleep(1)
    # Set up typewriter animation.
    message_text = ft.Text("", size=14, weight=ft.FontWeight.NORMAL)
    chat_bubble.content = ft.Column([message_text])
    page.update()
    
    cursor = ft.Text("|", size=14, weight=ft.FontWeight.BOLD)
    chat_bubble.content.controls.append(cursor)
    page.update()

    cursor_animation_active = True

    def blink_cursor():
        nonlocal cursor_animation_active
        while cursor_animation_active:
            cursor.visible = not cursor.visible
            page.update()
            time.sleep(0.5)
        cursor.visible = False
        page.update()

    cursor_thread = threading.Thread(target=blink_cursor)
    cursor_thread.start()

    for char in response_text:
        message += char
        message_text.value = message
        page.update()
        time.sleep(delay)
    cursor_animation_active = False
    cursor_thread.join()
    page.update()

def main(page: ft.Page):
    global current_language
    ip, port, username, theme_mode, temperature, current_language, custom_endpoint, filter_mode = load_settings()
    chat_history = load_chat_history()  # Local list for chat history

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

    # Splash screen with fade-in/fade-out animation.
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

    # Determine sidebar text and loading indicator colors.
    sidebar_text_color = "black" if theme_mode == "light" else "white"
    loading_color = sidebar_text_color  # Link loading indicator color to sidebar color

    # Sidebar toggle with fade animation.
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

        # Check server status.
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
            inactive_track_color="sidebar_text_color",
            on_change=lambda e: None,
        )
        theme_toggle = ft.Switch(
            value=(theme_mode == "light"),
            active_color="white",
            inactive_thumb_color="gray",
            active_track_color="#86759c",
            inactive_track_color="sidebar_text_color",
            on_change=lambda e: None,
        )
        connection_status_text = ft.Text(
            connection_status,
            color="green" if connection_status == translate("connected") else "red",
            size=12,
            weight=ft.FontWeight.BOLD,
        )
        language_options = [
            ft.dropdown.Option("en", "English 🇺🇸"),
            ft.dropdown.Option("sq", "Shqip 🇦🇱"),
            ft.dropdown.Option("de", "Deutsch 🇩🇪"),
            ft.dropdown.Option("da", "Dansk 🇩🇰"),
            ft.dropdown.Option("hu", "Magyar 🇭🇺"),
            ft.dropdown.Option("ga", "Gaeilge 🇮🇪"),
            ft.dropdown.Option("it", "Italiano 🇮🇹"),
            ft.dropdown.Option("no", "Norsk 🇳🇴"),
            ft.dropdown.Option("uk", "українська 🇺🇦"),
            ft.dropdown.Option("ro", "Română 🇷🇴"),
            ft.dropdown.Option("ru", "Русский 🇷🇺"),
            ft.dropdown.Option("es", "Español 🇪🇸"),
            ft.dropdown.Option("fr", "Français 🇫🇷"),
            ft.dropdown.Option("sv", "svenska 🇸🇪"),
            ft.dropdown.Option("zh", "简体中文 🇨🇳"),
            ft.dropdown.Option("zh-hk", "廣州話 🇭🇰"),
            ft.dropdown.Option("ja", "日本語 🇯🇵"),
            ft.dropdown.Option("ko", "한국어 🇰🇷"),
            ft.dropdown.Option("hi", "हिंदी 🇮🇳"),
            ft.dropdown.Option("ta", "தமிழ் 🇱🇰"),
            ft.dropdown.Option("he", "עִברִית 🇮🇱"),
            ft.dropdown.Option("ar", "عربي 🇦🇪"),
            ft.dropdown.Option("am", "አማርኛ 🇪🇹"),
            ft.dropdown.Option("sw", "Kiswahili 🇹🇿"),
            ft.dropdown.Option("fa", "فارسی 🇮🇷"),
            ft.dropdown.Option("ne", "नेपाली 🇳🇵"),
            ft.dropdown.Option("tl", "Filipino 🇵🇭"),
            ft.dropdown.Option("bg", "Български 🇧🇬"),
            ft.dropdown.Option("th", "ภาษาไทย 🇹🇭"),
            ft.dropdown.Option("pt", "Português 🇵🇹"),
            ft.dropdown.Option("pt-br", "Português (Brasil) 🇧🇷"),
            ft.dropdown.Option("id", "Bahasa Indonesia 🇮🇩"),
            ft.dropdown.Option("el", "ελληνικά 🇬🇷"),
            ft.dropdown.Option("hr", "Hrvatski 🇭🇷"),
            ft.dropdown.Option("sr", "Srpski 🇷🇸"),
            ft.dropdown.Option("fi", "Suomi 🇫🇮"),
            ft.dropdown.Option("mk", "македонски 🇲🇰"),
            ft.dropdown.Option("pl", "Polski 🇵🇱"),
            ft.dropdown.Option("tr", "Türkçe 🇹🇷"),
            ft.dropdown.Option("ka", "ქართული 🇬🇪"),
            ft.dropdown.Option("kk", "Қазақ тілі 🇰🇿"),
            ft.dropdown.Option("ms", "Melayu 🇲🇾"),
            ft.dropdown.Option("vi", "Tiếng Việt 🇻🇳"),
            ft.dropdown.Option("cs", "čeština 🇨🇿"),
            ft.dropdown.Option("la", "Latina 🇺🇳"),
        ]
        language_dropdown = ft.Dropdown(
            value=current_language,
            options=language_options,
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
            ft.Row([ft.Text(translate("dark_mode")), theme_toggle, ft.Text(translate("light_mode"))], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([ft.Text(translate("temperature")), temperature_input]),
            ft.Row([ft.Text(translate("connection_status")), connection_status_text]),
            ft.Row([
                ft.ElevatedButton(translate("cancel"), on_click=cancel_settings_action, bgcolor=ft.colors.RED_800, color="white", expand=True),
                ft.ElevatedButton(translate("save"), on_click=save_settings_action, bgcolor=ft.colors.WHITE, color="black", expand=True)
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

    chat_area = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True
    )
    page.chat_area = chat_area

    def send_message(e=None):
        if input_field.value.strip():
            user_message = input_field.value
            
            user_bubble = create_glowing_chat_bubble(
                user_message,
                is_user=True,
                theme_mode=theme_mode,
                bgcolor="#8f8f8f",
                glow_color="#8f8f8f",
            )
            user_row = ft.Row(
                [
                    ft.Container(width=40),
                    user_bubble,
                    ft.Icon(ft.icons.PERSON_ROUNDED, color="sidebar_text_color"),
                ],
                alignment=ft.MainAxisAlignment.END,
            )
            chat_area.controls.append(user_row)
            page.update()

            ip, port, username, _, temperature, _, custom_endpoint, filter_mode = load_settings()

            # Apply strict content filter.
            if filter_mode != "off" and strict_content(user_message):
                blocked_message = translate("content_blocked")
                ai_bubble = create_glowing_chat_bubble(
                    blocked_message,
                    is_user=False,
                    theme_mode=theme_mode,
                    bgcolor="red",
                    glow_color="red",
                )
                ai_row = ft.Row(
                    [
                        ft.Icon(ft.icons.SHIELD_ROUNDED, color="red"),
                        ai_bubble,
                        ft.Container(width=40),
                    ],
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

            # Add a loading indicator for the pending response.
            loading_indicator = ft.ProgressRing(width=30, height=30, color=loading_color)
            loading_row = ft.Row(
                [
                    ft.Icon(ft.icons.ASSISTANT_ROUNDED, color="#86759c"),
                    ft.Container(content=loading_indicator, padding=10),
                    ft.Container(width=40),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
            chat_area.controls.append(loading_row)
            page.update()

            # Get AI response.
            ai_response = get_ollama_response(user_message, ip, port, temperature, custom_endpoint)

            # Remove loading indicator.
            if loading_row in chat_area.controls:
                chat_area.controls.remove(loading_row)
            page.update()

            # Create AI bubble and animate response.
            ai_bubble = create_glowing_chat_bubble(
                ai_response,
                is_user=False,
                theme_mode=theme_mode,
                bgcolor=ft.colors.with_opacity(0.3, "#86759c"),
                glow_color="#86759c",
            )
            ai_row = ft.Row(
                [
                    ft.Icon(ft.icons.ASSISTANT_ROUNDED, color="#86759c"),
                    ai_bubble,
                    ft.IconButton(
                        ft.icons.COPY,
                        on_click=lambda e: copy_to_clipboard(e, ai_response),
                        icon_color="black" if theme_mode == "light" else "white",
                    ),
                    ft.Container(width=40),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
            chat_area.controls.append(ai_row)
            page.update()
            typewriter_animation(ai_response, ai_row, page)
            chat_history.append({"user": "You", "message": user_message, "is_user": True})
            chat_history.append({"user": "AI", "message": ai_response, "is_user": False})
            save_chat_history(chat_history)
            save_ollama_response(ai_response)
            input_field.value = ""
            page.update()

    # Load previous chat history into chat area.
    chat_history = load_chat_history()
    for message in chat_history:
        is_user = message.get("is_user", message["user"] == "You")
        bubble = create_glowing_chat_bubble(
            message["message"],
            is_user=is_user,
            theme_mode=theme_mode,
            bgcolor="#8f8f8f" if is_user else ("red" if message["message"] == translate("content_blocked") else "#86759c"),
            glow_color="#8f8f8f" if is_user else ("red" if message["message"] == translate("content_blocked") else "#86759c"),
        )
        if is_user:
            row = ft.Row(
                [
                    ft.Container(width=40),
                    bubble,
                    ft.Icon(ft.icons.PERSON_ROUNDED, color="sidebar_text_color"),
                ],
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
                    icon="DELETE_OUTLINE_OUTLINED",
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
                ft.Text(translate("version"), size=10, color="sidebar_text_color"),
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
        ink=True
    )

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

    greeting = get_greeting()
    top_bar = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    ft.icons.MENU_ROUNDED,
                    on_click=toggle_sidebar,
                    icon_color="black" if theme_mode == "light" else "white",
                    bgcolor=None
                ),
                ft.Text(
                    f"{greeting}, {username}",
                    size=16,
                    color="black" if theme_mode == "light" else "white",
                    weight=ft.FontWeight.BOLD,
                ),
                ft.IconButton(
                    ft.icons.WB_SUNNY if theme_mode == "light" else ft.icons.BRIGHTNESS_2,
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
        color="yellow",
        size=11,
    )

    warning_text = ft.Row(
        [
            ft.Icon(ft.icons.WARNING_ROUNDED, color="red"),
            ft.Text(
                translate("warn_setup_local_server"),
                color="red",
                size=11.5,
                weight=ft.FontWeight.BOLD
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=10,
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
                        border_radius=20
                    ),
                    ft.Row([
                        input_field,
                        ft.Container(
                            content=ft.IconButton(
                                ft.icons.SEND_ROUNDED,
                                on_click=send_message,
                                bgcolor=None,
                                icon_color="black" if theme_mode == "light" else "white"
                            ),
                            bgcolor=None,
                            padding=10,
                        ),
                    ]),
                ],
                expand=True,
            ),
            sidebar
        ],
        expand=True,
    )

    show_splash_screen()
    page.add(layout)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
