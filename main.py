import flet as ft
import requests
import json
import urllib.parse
import os
import time
import asyncio

CONFIG_FILE = "config.json"
COOKIE_FILE = "cookie_spx.txt"

def load_config():
    config = {"cookie": "", "current_station_id": "", "noi_tinh": [], "ngoai_tinh": []}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                config.update(json.load(f))
            except: pass
    elif os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            config["cookie"] = f.read().strip()
    
    # Fallback default values if empty
    if not config.get("noi_tinh") and not config.get("ngoai_tinh"):
        config["noi_tinh"] = [
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
            "45-DLK Mdrak Hub"
        ]
        config["ngoai_tinh"] = [
            "2490 | 45-DLK Buon Don Hub",
            "2491 | 45-DLK Buon Ho Hub"
        ]
    return config

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def main(page: ft.Page):
    page.title = "SOC BMT Tracking"
    page.window_width = 450
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F4F6F9"  
    page.padding = 0
    
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
                spread_radius=0, blur_radius=20, 
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            ),
            margin=ft.Margin.symmetric(horizontal=15, vertical=8)
        )

    config = load_config()

    cookie_input = ft.TextField(
        label="Dán cookie", value=config.get("cookie", ""),
        multiline=True, min_lines=2, max_lines=3,
        border_radius=12, border_color=ft.Colors.GREY_300, focused_border_color=PRIMARY_COLOR, expand=True,
        text_size=13, content_padding=10
    )
    station_id_input = ft.TextField(
        label="ID SOC hiện tại (Định dạng: ID | Tên)", value=config.get("current_station_id", ""),
        border_radius=12, border_color=ft.Colors.GREY_300, focused_border_color=PRIMARY_COLOR, expand=True,
        text_size=13, content_padding=10
    )
    noi_tinh_input = ft.TextField(
        label="Danh sách Hub Nội Tỉnh (Mỗi Hub 1 dòng)", value="\n".join(config.get("noi_tinh", [])),
        multiline=True, min_lines=4, max_lines=5,
        border_radius=12, border_color=ft.Colors.GREY_300, focused_border_color=PRIMARY_COLOR, expand=True,
        text_size=13, content_padding=10
    )
    ngoai_tinh_input = ft.TextField(
        label="Danh sách SOC ( Định dạng ID | Tên )", value="\n".join(config.get("ngoai_tinh", [])),
        multiline=True, min_lines=4, max_lines=5,
        border_radius=12, border_color=ft.Colors.GREY_300, focused_border_color=PRIMARY_COLOR, expand=True,
        text_size=13, content_padding=10
    )

    def toggle_settings(e):
        settings_ui.visible = not settings_ui.visible
        main_ui.visible = not main_ui.visible
        page.update()

    def get_station_name():
        station_str = config.get("current_station_id", "")
        if "|" in station_str:
            return station_str.split("|")[1].strip()
        elif station_str:
            return f"Trạm {station_str}"
        return "SOC"

    def save_settings_action(e):
        config["cookie"] = cookie_input.value
        config["current_station_id"] = station_id_input.value.strip()
        config["noi_tinh"] = [h.strip() for h in noi_tinh_input.value.split("\n") if h.strip()]
        config["ngoai_tinh"] = [h.strip() for h in ngoai_tinh_input.value.split("\n") if h.strip()]
        save_config(config)
        
        # Cập nhật lại title ngay khi lưu config
        station_name = get_station_name()
        is_intra = (current_mode[0] == "noi_tinh")
        header_title.value = f"{station_name} Tracking Intra" if is_intra else f"{station_name} Tracking Extra"
        
        toggle_settings(e)

    def clear_settings_action(e):
        cookie_input.value = ""
        station_id_input.value = ""
        noi_tinh_input.value = ""
        ngoai_tinh_input.value = ""
        page.update()

    settings_ui = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=toggle_settings, icon_color=ft.Colors.GREY_800),
                ft.Text("CẤU HÌNH HỆ THỐNG", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.GREY_800),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=ft.Colors.GREY_200, height=20),
            cookie_input,
            station_id_input,
            noi_tinh_input,
            ngoai_tinh_input,
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        content=ft.Text("XOÁ HẾT", weight=ft.FontWeight.BOLD),
                        on_click=clear_settings_action,
                        style=ft.ButtonStyle(color=PRIMARY_COLOR, bgcolor=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10), side=ft.BorderSide(1, PRIMARY_COLOR)),
                        height=50, expand=True
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("LƯU & ĐÓNG", weight=ft.FontWeight.BOLD), 
                        on_click=save_settings_action,
                        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=PRIMARY_COLOR, shape=ft.RoundedRectangleBorder(radius=10)),
                        height=50, expand=True
                    )
                ], spacing=10),
                padding=ft.Padding.only(top=10)
            ),
            ft.Container(
                content=ft.Text("For support, please contact tri.caoquoc@spxexpress.", size=11, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                padding=ft.Padding(left=0, top=20, right=0, bottom=0),
                alignment=ft.Alignment.CENTER
            )
        ], expand=True, scroll=ft.ScrollMode.AUTO),
        expand=True, visible=False, padding=20, bgcolor=ft.Colors.WHITE
    )


    current_mode = ["noi_tinh"]

    async def handle_drawer_change(e):
        idx = e.control.selected_index
        current_mode[0] = "noi_tinh" if idx == 0 else "ngoai_tinh"
        input_field.value = ""
        suggestions_container.visible = False
        station_name = get_station_name()
        header_title.value = f"{station_name} Tracking Intra" if idx == 0 else f"{station_name} Tracking Extra"
        
        if current_mode[0] == "noi_tinh":
            summary_card.visible = True
            list_container.visible = True
            cards_container.visible = False
        else:
            summary_card.visible = False
            list_container.visible = False
            cards_container.visible = True
            
        await page.close_drawer()
        page.update()

    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="Nội tỉnh", icon=ft.Icons.MAP_OUTLINED, selected_icon=ft.Icons.MAP
            ),
            ft.NavigationDrawerDestination(
                label="Ngoại tỉnh", icon=ft.Icons.LOCAL_SHIPPING_OUTLINED, selected_icon=ft.Icons.LOCAL_SHIPPING
            ),
        ],
        selected_index=0,
        on_change=handle_drawer_change
    )

    async def show_drawer(e):
        await page.show_drawer()

    input_field = ft.TextField(
        label="Nhập tên HUB để tìm kiếm...", border_radius=12, border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR, content_padding=15, text_size=14, expand=True
    )

    suggestions_listview = ft.ListView(expand=1, spacing=0, padding=0)
    suggestions_container = ft.Container(
        content=suggestions_listview, bgcolor=ft.Colors.WHITE, border_radius=12,
        border=ft.Border.all(1, ft.Colors.GREY_200), padding=0, visible=False, height=200,
    )

    def select_hub(hub_name):
        display_name = hub_name
        if current_mode[0] == "ngoai_tinh" and "|" in hub_name:
            display_name = hub_name.split("|")[1].strip()
            
        input_field.value = display_name
        suggestions_container.visible = False
        page.update()

    def filter_hubs(e):
        query = input_field.value.lower() if input_field.value else ""
        suggestions_listview.controls.clear()
        
        active_hubs = config["noi_tinh"] if current_mode[0] == "noi_tinh" else config["ngoai_tinh"]
        
        matches = []
        for h in active_hubs:
            search_text = h.split("|")[1].strip() if "|" in h and current_mode[0] == "ngoai_tinh" else h
            if query in search_text.lower():
                matches.append(h)
        
        if not matches:
            suggestions_listview.controls.append(
                ft.Container(content=ft.Text("Không tìm thấy HUB", color=ft.Colors.GREY_500, size=13), padding=12)
            )
        else:
            for match in matches:
                display_name = match.split("|")[1].strip() if "|" in match and current_mode[0] == "ngoai_tinh" else match
                suggestions_listview.controls.append(
                    ft.Container(
                        content=ft.Text(display_name, size=13, color=ft.Colors.BLACK87),
                        padding=ft.Padding(left=15, top=8, right=15, bottom=8),
                        on_click=lambda e, m=match: select_hub(m),
                        ink=True
                    )
                )
        
        suggestions_container.visible = True
        page.update()

    input_field.on_change = filter_hubs
    input_field.on_focus = lambda e: filter_hubs(e) if not input_field.value else None
    
    packed_value_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    packed_card = ft.Container(
        content=ft.Column([
            ft.Text("📦 SOC Packed", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            packed_value_text,
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.ORANGE_500, border_radius=16, padding=20, expand=True, height=130,
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.ORANGE_500), offset=ft.Offset(0, 4))
    )
    
    received_value_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    received_card = ft.Container(
        content=ft.Column([
            ft.Text("📥 SOC Received", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            received_value_text,
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.GREEN_500, border_radius=16, padding=20, expand=True, height=130,
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=15, color=ft.Colors.with_opacity(0.3, ft.Colors.GREEN_500), offset=ft.Offset(0, 4))
    )

    error_text = ft.Text("", color=ft.Colors.RED_500, visible=False, size=13)
    is_loading = [False]

    def fetch_hub_data(hub_name, cookie_str):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://spx.shopee.vn/",
            "Cookie": cookie_str
        }
        encoded_hub_name = urllib.parse.quote_plus(hub_name)
        
        current_time = int(time.time())
        start_time = current_time - (14 * 24 * 60 * 60)
        end_time = current_time + (24 * 60 * 60)
        
        all_items = []
        pageno = 1
        
        try:
            while True:
                api_url = f"https://spx.shopee.vn/api/in-station/general_to/outbound/search?pageno={pageno}&count=100&receiver={encoded_hub_name}&status=2&ctime={start_time},{end_time}"
                response = requests.get(api_url, headers=headers, timeout=15)
                
                if response.status_code != 200:
                    return {"success": False, "error": f"Lỗi HTTP {response.status_code}: {response.text}"}
                    
                data = response.json()
                items = []
                
                if isinstance(data, dict):
                    if "data" in data and isinstance(data["data"], dict) and "list" in data["data"]:
                        items = data["data"]["list"]
                    elif "data" in data and isinstance(data["data"], list):
                        items = data["data"]
                        
                if not items and isinstance(data, list):
                    items = data
                    
                if not items:
                    break 
                    
                all_items.extend(items)
                
                if len(items) < 100:
                    break
                    
                pageno += 1
                
            return {"success": True, "data": all_items}
            
        except Exception as e:
            return {"success": False, "error": f"Lỗi kết nối: {str(e)}"}

    def fetch_status(status_code, next_id, current_id, cookie_str):
        url = "https://spx.shopee.vn/api/fleet_order/order/tracking_list/search"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Cookie": cookie_str
        }
        payload = {
            "order_status": status_code,
            "count": 24,
            "next_station_ids": str(next_id),
            "current_station_ids": str(current_id),
            "page_no": 1
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {"success": True, "total": data.get("data", {}).get("total", 0)}
            return {"success": False, "error": f"Lỗi HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"success": False, "error": f"Lỗi kết nối: {str(e)}"}

    def fetch_both_statuses(hub_input, config):
        cookie = config.get("cookie", "")
        current_id_str = config.get("current_station_id", "")
        
        if not current_id_str:
            return {"success": False, "error": "❌ Vui lòng nhập ID SOC hiện tại trong phần Cài Đặt!"}
            
        current_id = current_id_str.split("|")[0].strip() if "|" in current_id_str else current_id_str.strip()
        
        if "|" not in hub_input:
            return {"success": False, "error": "❌ Định dạng Hub sai. Yêu cầu có ID (VD: '2490 | Tên Hub')"}
        next_id = hub_input.split("|")[0].strip()
            
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(fetch_status, "33", next_id, current_id, cookie)
            f2 = executor.submit(fetch_status, "8", next_id, current_id, cookie)
            res1 = f1.result()
            res2 = f2.result()
            
        if not res1["success"]: return res1
        if not res2["success"]: return res2
        
        return {"success": True, "packed": res1["total"], "received": res2["total"]}

    def show_error(msg):
        error_text.value = msg
        error_text.visible = True
        page.update()

    def hide_error():
        error_text.visible = False
        page.update()

    async def on_search_click(e):
        if is_loading[0]: return
        hide_error()
        suggestions_container.visible = False
        hub_name = input_field.value
        
        cfg = load_config()
        
        if not hub_name:
            show_error("⚠️ Vui lòng nhập tên HUB!")
            return
        if not cfg.get("cookie"):
            show_error("⚠️ Vui lòng cấu hình Cookie!")
            return

        is_loading[0] = True
        button_container.content = loading_button
        if current_mode[0] == "ngoai_tinh":
            packed_value_text.value = "..."
            received_value_text.value = "..."
            cards_container.visible = True
            summary_card.visible = False
            list_container.visible = False
        else:
            table_container.controls.clear()
            table_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.ProgressRing(color=PRIMARY_COLOR, width=40, height=40, stroke_width=3),
                        ft.Text("Đang đồng bộ...", color=ft.Colors.GREY_500, size=14)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                    alignment=ft.Alignment.CENTER, padding=50
                )
            )
            cards_container.visible = False
            summary_card.visible = True
            list_container.visible = True

        page.update()
        await asyncio.sleep(0.1)

        try:
            original_hub_str = hub_name
            if current_mode[0] == "ngoai_tinh":
                for h in cfg.get("ngoai_tinh", []):
                    if "|" in h and h.split("|")[1].strip().lower() == hub_name.lower():
                        original_hub_str = h
                        break
                        
            if current_mode[0] == "ngoai_tinh":
                result = await asyncio.to_thread(fetch_both_statuses, original_hub_str, cfg)

                if result["success"]:
                    packed_value_text.value = f'{result["packed"]:,}'
                    received_value_text.value = f'{result["received"]:,}'
                else:
                    packed_value_text.value = "0"
                    received_value_text.value = "0"
                    show_error(result["error"])
            else:
                cookie_str = cfg["cookie"]
                result = await asyncio.to_thread(fetch_hub_data, original_hub_str, cookie_str)
                table_container.controls.clear()

                if result["success"]:
                    items = result["data"]
                    if not items:
                        table_container.controls.append(
                            ft.Container(content=ft.Text("Không tìm thấy dữ liệu.", color=ft.Colors.RED_400), padding=20, alignment=ft.Alignment.CENTER)
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
                            sender_name = str(item.get("sender_name", item.get("sender", "N/A")))
                            total_qty += int(quantity) if str(quantity).isdigit() else 0
                            
                            def create_to_click_handler(to_num):
                                async def handler(e):
                                    await page.clipboard.set(to_num)
                                    snack = ft.SnackBar(ft.Text(f"Đã copy mã: {to_num}"), bgcolor=ft.Colors.GREEN_600)
                                    page.snack_bar = snack
                                    snack.open = True
                                    page.update()
                                    
                                    def close_dialog(e):
                                        qr_dialog.open = False
                                        page.update()
                                        
                                    qr_dialog = ft.AlertDialog(
                                        title=ft.Text(f"{to_num}", text_align=ft.TextAlign.CENTER, size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
                                        content=ft.Container(
                                            content=ft.Container(
                                                content=ft.Image(src=f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={to_num}&margin=1", width=220, height=220),
                                                border_radius=16,
                                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                            ),
                                            alignment=ft.Alignment.CENTER, width=250, height=250
                                        ),
                                        actions=[ft.ElevatedButton("Đóng", on_click=close_dialog, bgcolor=ft.Colors.GREY_200, color=ft.Colors.BLACK)],
                                        actions_alignment=ft.MainAxisAlignment.CENTER,
                                        shape=ft.RoundedRectangleBorder(radius=20)
                                    )
                                    page.show_dialog(qr_dialog)
                                return handler

                            rows.append(
                                ft.Container(
                                    content=ft.Row([
                                        ft.Container(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.QR_CODE_SCANNER, size=18, color=PRIMARY_COLOR),
                                                ft.Text(to_number, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR, size=13, expand=True, selectable=True)
                                            ], spacing=5, alignment=ft.MainAxisAlignment.START),
                                            on_click=create_to_click_handler(to_number),
                                            tooltip="Click để copy mã",
                                            expand=4
                                        ),
                                        ft.Text(str(quantity), color=ft.Colors.GREY_800, weight=ft.FontWeight.BOLD, size=13, text_align=ft.TextAlign.CENTER, expand=1),
                                        ft.Text(sender_name, color=ft.Colors.GREY_600, size=12, expand=2, overflow=ft.TextOverflow.ELLIPSIS, text_align=ft.TextAlign.RIGHT)
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=ft.Padding(15, 12, 15, 12),
                                    border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100))
                                )
                            )
                        
                        num_to_text.value = f"{num_to}"
                        num_don_text.value = f"{total_qty}"
                        
                        header_row = ft.Container(
                            content=ft.Row([
                                ft.Text("TO Number", color=ft.Colors.GREY_500, size=12, expand=4),
                                ft.Text("Quantity", color=ft.Colors.GREY_500, size=12, text_align=ft.TextAlign.CENTER, expand=1),
                                ft.Text("Sender", color=ft.Colors.GREY_500, size=12, text_align=ft.TextAlign.RIGHT, expand=2),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=ft.Padding(15, 10, 15, 10),
                            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200))
                        )
                        
                        custom_table = ft.Column(
                            controls=[header_row] + rows,
                            spacing=0
                        )
                        
                        table_container.controls.append(
                            ft.Container(content=custom_table, bgcolor=ft.Colors.WHITE, border_radius=12, border=ft.Border.all(1, ft.Colors.GREY_200), padding=0, clip_behavior=ft.ClipBehavior.HARD_EDGE)
                        )
                else:
                    show_error(result["error"])

        finally:
            is_loading[0] = False
            button_container.content = search_button
            page.update()

    search_button = ft.ElevatedButton(
        content=ft.Text("Tra cứu", weight=ft.FontWeight.BOLD, size=14), on_click=on_search_click,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=PRIMARY_COLOR, shape=ft.RoundedRectangleBorder(radius=12)),
        height=48, expand=True
    )

    loading_button = ft.ElevatedButton(
        content=ft.Row([
            ft.ProgressRing(width=16, height=16, color=ft.Colors.WHITE, stroke_width=2),
            ft.Text("Đang tải", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=13)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREY_400, shape=ft.RoundedRectangleBorder(radius=12)),
        disabled=True, height=48, expand=True
    )
    
    button_container = ft.Container(content=search_button, expand=True)

    def reset_input(e):
        input_field.value = ""
        suggestions_container.visible = False
        page.update()

    reset_button = ft.ElevatedButton(
        content=ft.Text("Nhập lại", weight=ft.FontWeight.BOLD, size=14),
        on_click=reset_input,
        style=ft.ButtonStyle(color=PRIMARY_COLOR, bgcolor=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12), side=ft.BorderSide(1, PRIMARY_COLOR)),
        height=48, expand=True
    )

    # Định nghĩa header_title ở đây để các hàm bên trên gọi được (sẽ được cập nhật lại value lúc khởi tạo)
    header_title = ft.Text("SOC Tracking Intra", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)
    
    # Cập nhật giá trị thật cho header_title
    initial_station_name = get_station_name()
    header_title.value = f"{initial_station_name} Tracking Intra"

    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.Icons.MENU, icon_color=PRIMARY_COLOR, on_click=show_drawer, icon_size=28),
                    header_title,
                ], spacing=5),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS_OUTLINED, 
                    icon_color=ft.Colors.GREY_600,
                    on_click=toggle_settings,
                    tooltip="Cài đặt cấu hình"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.Padding.only(left=5, right=10, top=45, bottom=5)
    )

    search_card = modern_card(
        ft.Column([
            error_text,
            input_field,
            ft.Row([reset_button, button_container], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            suggestions_container,
        ], spacing=10)
    )

    cards_container = ft.Container(
        content=ft.Row([packed_card, received_card], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(horizontal=15, vertical=5),
        visible=False
    )

    num_to_text = ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
    num_don_text = ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
    
    table_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    summary_card = modern_card(
        ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=PRIMARY_COLOR, size=28),
            ft.Row([
                num_to_text, ft.Text("TO -", size=15, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_500),
                num_don_text, ft.Text("đơn hàng", size=15, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_500),
            ], spacing=6, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
        padding=15
    )

    list_container = ft.Container(content=table_container, padding=ft.Padding.symmetric(horizontal=15), expand=True)

    main_ui = ft.Column([header, search_card, summary_card, list_container, cards_container], expand=True, visible=True, spacing=0)

    page.add(main_ui, settings_ui)

ft.run(main)
