import flet as ft
import requests
import json
import urllib.parse
import os
import time
import asyncio

COOKIE_FILE = "cookie_spx.txt"

def load_cookie():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_cookie(cookie_str):
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(cookie_str)

def main(page: ft.Page):
    # Cấu hình Page
    page.title = "SPX Hub Search"
    page.window_width = 450
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F4F6F9"  
    page.padding = 0
    
    # MÀU CHỦ ĐẠO CHÍNH THỨC CỦA SHOPEE/SPX
    PRIMARY_COLOR = "#EE4D2D"

    page.fonts = {
        "Be Vietnam Pro": "https://github.com/google/fonts/raw/main/ofl/bevietnampro/BeVietnamPro-Regular.ttf"
    }
    page.theme = ft.Theme(font_family="Be Vietnam Pro", color_scheme_seed=PRIMARY_COLOR)

    def modern_card(content_control, padding=20):
        return ft.Container(
            content=content_control,
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            padding=padding,
            shadow=ft.BoxShadow(
                spread_radius=0, 
                blur_radius=20, 
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            ),
            margin=ft.Margin.symmetric(horizontal=15, vertical=8)
        )

    # --- KHU VỰC CÀI ĐẶT COOKIE ---
    cookie_input = ft.TextField(
        label="Dán cookie",
        value=load_cookie(),
        multiline=True,
        min_lines=8,
        max_lines=15,
        border_radius=12,
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
        expand=True
    )

    def toggle_settings(e):
        settings_ui.visible = not settings_ui.visible
        main_ui.visible = not main_ui.visible
        page.update()

    def save_cookie_action(e):
        save_cookie(cookie_input.value)
        toggle_settings(e)

    def clear_cookie_action(e):
        cookie_input.value = ""
        page.update()

    settings_ui = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=toggle_settings, icon_color=ft.Colors.GREY_800),
                ft.Text("CẤU HÌNH HỆ THỐNG", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.GREY_800),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=ft.Colors.GREY_200, height=20),
            cookie_input,
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        content=ft.Text("XOÁ HẾT", weight=ft.FontWeight.BOLD),
                        on_click=clear_cookie_action,
                        style=ft.ButtonStyle(
                            color=PRIMARY_COLOR,
                            bgcolor=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            side=ft.BorderSide(1, PRIMARY_COLOR)
                        ),
                        height=50,
                        expand=True
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("LƯU & ĐÓNG", weight=ft.FontWeight.BOLD), 
                        on_click=save_cookie_action,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE, 
                            bgcolor=PRIMARY_COLOR,
                            shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                        height=50,
                        expand=True
                    )
                ], spacing=10),
                padding=ft.Padding.only(top=10)
            )
        ], expand=True),
        expand=True,
        visible=False,
        padding=20,
        bgcolor=ft.Colors.WHITE
    )

    # --- UI Elements Giao Diện Chính ---
    hub_list = [
        "45-DLK Buon Don Hub",
        "45-DLK Buon Ho Hub",
        "45-DLK Buon Ma Thuot 02 Hub",
        "45-DLK Buon Ma Thuot 03 Hub",
        "45-DLK Buon Ma Thuot 04 Hub",
        "45-DLK Buon Ma Thuot Hub",
        "45-DLK Cu Kuin Hub",
        "45-DLK Cu Mgar Hub",
        "45-DLK Ea Hleo 02 Hub",
        "45-DLK Ea Hleo Hub",
        "45-DLK Ea Kar 02 Hub",
        "45-DLK Ea Kar Hub",
        "45-DLK Ea Sup Hub",
        "45-DLK Krong Ana Hub",
        "45-DLK Krong Bong Hub",
        "45-DLK Krong Buk Hub",
        "45-DLK Krong Nang 02 Hub",
        "45-DLK Krong Nang Hub",
        "45-DLK Krong Pak 02 Hub",
        "45-DLK Krong Pak Hub",
        "45-DLK Lak Hub",
        "45-DLK MBH 02 Buon Ho Hub",
        "45-DLK MBH Buon Ho Hub",
        "45-DLK MBH Krong Nang Hub",
        "45-DLK Mdrak Hub",
        "47-DKG Cu Jut Hub",
        "47-DKG Dak Mil 02 Hub",
        "47-DKG Dak Mil Hub",
        "47-DKG Krong No Hub"
    ]

    input_field = ft.TextField(
        label="Nhập tên HUB để tìm kiếm...",
        border_radius=12,
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
        content_padding=15,
        text_size=14,
        expand=True
    )

    suggestions_listview = ft.ListView(expand=1, spacing=0, padding=0)
    suggestions_container = ft.Container(
        content=suggestions_listview,
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        border=ft.Border.all(1, ft.Colors.GREY_200),
        padding=0,
        visible=False,
        height=200,
    )

    def select_hub(hub_name):
        input_field.value = hub_name
        suggestions_container.visible = False
        page.update()

    def filter_hubs(e):
        query = input_field.value.lower() if input_field.value else ""
        suggestions_listview.controls.clear()
        
        matches = [h for h in hub_list if query in h.lower()]
        
        if not matches:
            suggestions_listview.controls.append(ft.ListTile(title=ft.Text("Không tìm thấy HUB", color=ft.Colors.GREY_500)))
        else:
            for match in matches:
                suggestions_listview.controls.append(
                    ft.ListTile(
                        title=ft.Text(match, size=13),
                        on_click=lambda e, m=match: select_hub(m)
                    )
                )
        
        suggestions_container.visible = True
        page.update()

    input_field.on_change = filter_hubs
    input_field.on_focus = lambda e: filter_hubs(e) if not input_field.value else None
    
    num_to_text = ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
    num_don_text = ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
    
    table_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
    error_text = ft.Text("", color=ft.Colors.RED_500, visible=False, size=13)

    is_loading = [False]

    def fetch_hub_data(hub_name, cookie_str):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://spx.shopee.vn/",
            "Cookie": cookie_str
        }
        
        encoded_hub_name = urllib.parse.quote_plus(hub_name)
        api_url = f"https://spx.shopee.vn/api/in-station/general_to/outbound/search?pageno=1&count=24&receiver={encoded_hub_name}&status=2&ctime=1781110800,1781715599"
        
        try:
            response = requests.get(api_url, headers=headers, timeout=15)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Lỗi HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": f"Lỗi kết nối: {str(e)}"}

    def show_error(msg):
        error_text.value = msg
        error_text.visible = True
        page.update()

    def hide_error():
        error_text.visible = False
        page.update()

    async def on_search_click(e):
        if is_loading[0]:
            return # Block spam click
            
        hide_error()
        suggestions_container.visible = False
        hub_name = input_field.value
        cookie_str = load_cookie() 
        
        if not hub_name:
            show_error("⚠️ Vui lòng nhập tên HUB!")
            return
            
        if not cookie_str:
            show_error("⚠️ Vui lòng bấm vào icon Cài đặt góc phải để dán Cookie!")
            return

        is_loading[0] = True

        # Đổi hẳn sang một button dạng loading để ép UI phải render lại
        button_container.content = loading_button
        
        table_container.controls.clear()
        table_container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(color=PRIMARY_COLOR, width=40, height=40, stroke_width=3),
                    ft.Text("Đang đồng bộ dữ liệu...", color=ft.Colors.GREY_500, size=14)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                alignment=ft.Alignment.CENTER,
                padding=50
            )
        )
        
        page.update()
        
        # Nhường quyền cho event loop xử lý UI và drop các click bị thừa
        await asyncio.sleep(0.1)

        try:
            # Chạy request.get ở một thread riêng biệt để không block Flet event loop
            result = await asyncio.to_thread(fetch_hub_data, hub_name, cookie_str)
            table_container.controls.clear()

            if result["success"]:
                data = result["data"]
                items = []
                
                if isinstance(data, dict):
                    if "data" in data and isinstance(data["data"], dict) and "list" in data["data"]:
                        items = data["data"]["list"]
                    elif "data" in data and isinstance(data["data"], list):
                        items = data["data"]

                if not items and isinstance(data, list):
                    items = data

                if not items:
                    table_container.controls.append(
                        ft.Container(
                            content=ft.Text("Không tìm thấy dữ liệu từ HUB này.", color=ft.Colors.RED_400),
                            padding=20, alignment=ft.Alignment.CENTER
                        )
                    )
                    num_to_text.value = "0"
                    num_don_text.value = "0"
                else:
                    total_qty = 0
                    num_to = len(items)
                    rows = []
                    for item in items:
                        to_number = str(item.get("to_number", "N/A"))
                        quantity = item.get("quantity", 0)
                        total_qty += int(quantity) if str(quantity).isdigit() else 0
                        
                        rows.append(
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(to_number, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_800)),
                                    ft.DataCell(ft.Text(str(quantity), color=PRIMARY_COLOR, weight=ft.FontWeight.BOLD))
                                ]
                            )
                        )
                    
                    num_to_text.value = f"{num_to}"
                    num_don_text.value = f"{total_qty}"
                    
                    data_table = ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("TO Number", color=ft.Colors.GREY_500, size=12)),
                            ft.DataColumn(ft.Text("Số lượng", color=ft.Colors.GREY_500, size=12), numeric=True),
                        ],
                        rows=rows,
                        horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_100),
                        heading_row_height=40,
                        data_row_min_height=50,
                        divider_thickness=0,
                        column_spacing=20
                    )
                    
                    table_card = ft.Container(
                        content=data_table,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        border=ft.Border.all(1, ft.Colors.GREY_200),
                        padding=0
                    )
                    table_container.controls.append(table_card)

            else:
                show_error(result["error"])

        finally:
            is_loading[0] = False
            # Khôi phục nút bấm
            button_container.content = search_button
            page.update()

    search_button = ft.ElevatedButton(
        content=ft.Text("Tra cứu", weight=ft.FontWeight.BOLD, size=14), 
        on_click=on_search_click,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE, 
            bgcolor=PRIMARY_COLOR,
            shape=ft.RoundedRectangleBorder(radius=12)
        ),
        height=48,
        expand=True
    )

    loading_button = ft.ElevatedButton(
        content=ft.Row([
            ft.ProgressRing(width=16, height=16, color=ft.Colors.WHITE, stroke_width=2),
            ft.Text("Đang tải", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=13)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE, 
            bgcolor=ft.Colors.GREY_400, # Nút xám mờ khi đang tải
            shape=ft.RoundedRectangleBorder(radius=12)
        ),
        disabled=True,
        height=48,
        expand=True
    )
    
    button_container = ft.Container(content=search_button, expand=True)

    def reset_input(e):
        input_field.value = ""
        suggestions_container.visible = False
        page.update()

    reset_button = ft.ElevatedButton(
        content=ft.Text("Nhập lại", weight=ft.FontWeight.BOLD, size=14),
        on_click=reset_input,
        style=ft.ButtonStyle(
            color=PRIMARY_COLOR,
            bgcolor=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=12),
            side=ft.BorderSide(1, PRIMARY_COLOR)
        ),
        height=48,
        expand=True
    )

    # --- Main UI ---
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.LOCAL_SHIPPING, color=PRIMARY_COLOR, size=28),
                    ft.Text("SPX Tracking", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                ], spacing=10),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS_OUTLINED, 
                    icon_color=ft.Colors.GREY_600,
                    on_click=toggle_settings,
                    tooltip="Cài đặt cấu hình"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.Padding.only(left=20, right=10, top=45, bottom=5)
    )

    search_card = modern_card(
        ft.Column([
            error_text,
            input_field,
            ft.Row([reset_button, button_container], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            suggestions_container,
        ], spacing=10)
    )

    summary_card = modern_card(
        ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=PRIMARY_COLOR, size=28),
            ft.Row([
                num_to_text,
                ft.Text("TO -", size=15, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_500),
                num_don_text,
                ft.Text("đơn hàng", size=15, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_500),
            ], spacing=6, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
        padding=15
    )

    list_container = ft.Container(
        content=table_container,
        padding=ft.Padding.symmetric(horizontal=15),
        expand=True
    )

    main_ui = ft.Column(
        [
            header,
            search_card,
            summary_card,
            list_container
        ],
        expand=True,
        visible=True,
        spacing=0
    )

    # --- Gắn vào Page ---
    page.add(main_ui, settings_ui)

ft.run(main)
