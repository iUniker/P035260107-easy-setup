#!/usr/bin/env python3
"""生成 MazerPi MZP351 中文工程测试版 PDF。"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image as RLImage,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


DARK = colors.HexColor("#0C1B19")
INK = colors.HexColor("#14201E")
GREEN = colors.HexColor("#1D6D5D")
LIME = colors.HexColor("#E9FF77")
MUTED = colors.HexColor("#65726E")
PALE = colors.HexColor("#F2F8F4")
PALE_2 = colors.HexColor("#F7F8F3")
BORDER = colors.HexColor("#DDE5DD")
AMBER = colors.HexColor("#FFF1C7")
AMBER_INK = colors.HexColor("#6A4900")
PURPLE = colors.HexColor("#6F55B5")
BLUE = colors.HexColor("#3478D4")
CHANNEL_GREEN = colors.HexColor("#248A62")
RED = colors.HexColor("#C94E5D")
TOUCH = colors.HexColor("#D08A16")
BACKLIGHT = colors.HexColor("#A5508F")
AVAILABLE = colors.HexColor("#147D6A")
PIN_GRAY = colors.HexColor("#77817E")
WHITE = colors.white

REPO_DIR = Path(__file__).resolve().parents[1]
VERSION = (REPO_DIR / "VERSION").read_text(encoding="utf-8").strip()
PRODUCT_IMAGE_DIR = REPO_DIR / "docs" / "assets" / "product-images"
ALIGNMENT_IMAGE = PRODUCT_IMAGE_DIR / "four-hole-alignment.jpg"
PCB_BACK_IMAGE = PRODUCT_IMAGE_DIR / "display-pcb-back.jpg"

ONLINE_COMMAND = (
    "curl -fL --retry 3 --retry-all-errors https://raw.githubusercontent.com/iUniker/"
    "P035260107-easy-setup/main/install.sh -o ~/mazerpi-mzp351-install.sh && "
    "sudo bash ~/mazerpi-mzp351-install.sh --reboot"
)
OFFLINE_COMMAND = "bash INSTALL"
DIAG_COMMAND = "sudo bash diagnose.sh | tee mzp351-diagnostic.txt"
REPO_URL = "https://github.com/iUniker/P035260107-easy-setup"


def register_fonts():
    pdfmetrics.registerFont(TTFont("CN", "/System/Library/Fonts/STHeiti Light.ttc"))
    pdfmetrics.registerFont(TTFont("CNBold", "/System/Library/Fonts/STHeiti Medium.ttc"))
    pdfmetrics.registerFontFamily(
        "CN",
        normal="CN",
        bold="CNBold",
        italic="CN",
        boldItalic="CNBold",
    )


register_fonts()


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCN",
            parent=base["Title"],
            fontName="CNBold",
            fontSize=22,
            leading=28,
            textColor=INK,
            alignment=TA_LEFT,
            wordWrap="CJK",
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCN",
            parent=base["BodyText"],
            fontName="CN",
            fontSize=9.2,
            leading=14,
            textColor=MUTED,
            wordWrap="CJK",
            spaceAfter=7,
        ),
        "section": ParagraphStyle(
            "SectionCN",
            parent=base["Heading2"],
            fontName="CNBold",
            fontSize=13,
            leading=17,
            textColor=INK,
            wordWrap="CJK",
            spaceBefore=2,
            spaceAfter=5,
        ),
        "card_title": ParagraphStyle(
            "CardTitleCN",
            parent=base["Heading3"],
            fontName="CNBold",
            fontSize=10.8,
            leading=14,
            textColor=INK,
            wordWrap="CJK",
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "BodyCN",
            parent=base["BodyText"],
            fontName="CN",
            fontSize=8.4,
            leading=12.3,
            textColor=INK,
            wordWrap="CJK",
        ),
        "body_bold": ParagraphStyle(
            "BodyBoldCN",
            parent=base["BodyText"],
            fontName="CNBold",
            fontSize=8.4,
            leading=12.3,
            textColor=INK,
            wordWrap="CJK",
        ),
        "small": ParagraphStyle(
            "SmallCN",
            parent=base["BodyText"],
            fontName="CN",
            fontSize=7.3,
            leading=10.4,
            textColor=MUTED,
            wordWrap="CJK",
        ),
        "table": ParagraphStyle(
            "TableCN",
            parent=base["BodyText"],
            fontName="CN",
            fontSize=7.1,
            leading=9.5,
            textColor=INK,
            wordWrap="CJK",
        ),
        "table_bold": ParagraphStyle(
            "TableBoldCN",
            parent=base["BodyText"],
            fontName="CNBold",
            fontSize=7.1,
            leading=9.5,
            textColor=INK,
            wordWrap="CJK",
        ),
        "table_head": ParagraphStyle(
            "TableHeadCN",
            parent=base["BodyText"],
            fontName="CNBold",
            fontSize=7.1,
            leading=9.2,
            textColor=WHITE,
            wordWrap="CJK",
        ),
        "code": ParagraphStyle(
            "CodeCN",
            parent=base["Code"],
            fontName="Courier",
            fontSize=6.0,
            leading=8.0,
            textColor=LIME,
            splitLongWords=False,
        ),
        "code_short": ParagraphStyle(
            "CodeShortCN",
            parent=base["Code"],
            fontName="Courier-Bold",
            fontSize=8.0,
            leading=10,
            textColor=LIME,
        ),
        "callout": ParagraphStyle(
            "CalloutCN",
            parent=base["BodyText"],
            fontName="CN",
            fontSize=8.0,
            leading=11.8,
            textColor=AMBER_INK,
            wordWrap="CJK",
        ),
        "center_small": ParagraphStyle(
            "CenterSmallCN",
            parent=base["BodyText"],
            fontName="CN",
            fontSize=7.3,
            leading=10.2,
            alignment=TA_CENTER,
            textColor=MUTED,
            wordWrap="CJK",
        ),
        "pin_left": ParagraphStyle(
            "PinLeftCN",
            parent=base["BodyText"],
            fontName="CNBold",
            fontSize=5.9,
            leading=7.0,
            alignment=TA_RIGHT,
            textColor=INK,
            wordWrap="CJK",
        ),
        "pin_right": ParagraphStyle(
            "PinRightCN",
            parent=base["BodyText"],
            fontName="CNBold",
            fontSize=5.9,
            leading=7.0,
            alignment=TA_LEFT,
            textColor=INK,
            wordWrap="CJK",
        ),
        "pin_number": ParagraphStyle(
            "PinNumberCN",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.1,
            leading=7.0,
            alignment=TA_CENTER,
            textColor=WHITE,
        ),
        "legend": ParagraphStyle(
            "LegendCN",
            parent=base["BodyText"],
            fontName="CN",
            fontSize=6.1,
            leading=7.2,
            textColor=INK,
            wordWrap="CJK",
        ),
        "field": ParagraphStyle(
            "FieldCN",
            parent=base["BodyText"],
            fontName="CN",
            fontSize=7.2,
            leading=10.2,
            textColor=INK,
            wordWrap="CJK",
        ),
    }


S = styles()


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def header_footer(canvas, doc):
    width, height = LETTER
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, height - 0.72 * inch, width, 0.72 * inch, fill=1, stroke=0)
    canvas.setFillColor(LIME)
    canvas.roundRect(0.48 * inch, height - 0.54 * inch, 0.30 * inch, 0.30 * inch, 5, fill=1, stroke=0)
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(0.63 * inch, height - 0.43 * inch, "M")
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(0.88 * inch, height - 0.39 * inch, "MAZERPI")
    canvas.setFont("CN", 7.5)
    canvas.setFillColor(colors.HexColor("#AFC3BD"))
    canvas.drawString(0.88 * inch, height - 0.53 * inch, "屏幕安装与工程测试")
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawRightString(width - 0.50 * inch, height - 0.43 * inch, "MZP351HV00TR / P035260107")

    canvas.setStrokeColor(BORDER)
    canvas.line(0.50 * inch, 0.39 * inch, width - 0.50 * inch, 0.39 * inch)
    canvas.setFillColor(MUTED)
    canvas.setFont("CN", 6.5)
    canvas.drawString(0.50 * inch, 0.22 * inch, f"中文工程测试版 {VERSION} - 未经客户发布")
    canvas.drawRightString(width - 0.50 * inch, 0.22 * inch, f"第 {doc.page} 页")
    canvas.restoreState()


def callout(text: str):
    table = Table([[p(text, "callout")]], colWidths=[5.28 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), AMBER),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#E8C96B")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def code_box(command: str, short=False, width=5.14 * inch):
    style = "code_short" if short else "code"
    table = Table([[p(command, style)]], colWidths=[width])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), DARK),
                ("BOX", (0, 0), (-1, -1), 0.7, DARK),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def number_badge(number: str):
    badge = Table([[p(number, "table_head")]], colWidths=[0.24 * inch], rowHeights=[0.24 * inch])
    badge.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return badge


def preflight_grid():
    items = [
        ("1", "安装屏幕前先断电。"),
        ("2", "确认 40-pin 接口完全对齐。"),
        ("3", "首次测试时移除其他 GPIO HAT。"),
        ("4", "拔掉 HDMI，使用稳定的 5V 电源。"),
    ]
    cells = []
    for number, text in items:
        cell = Table([[number_badge(number), p(text, "small")]], colWidths=[0.31 * inch, 2.14 * inch])
        cell.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        cells.append(cell)
    grid = Table([[cells[0], cells[1]], [cells[2], cells[3]]], colWidths=[2.58 * inch, 2.58 * inch])
    grid.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_2),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return grid


def method_card(label: str, title: str, body_items, command: str, background):
    label_box = Table([[p(label, "table_head")]], colWidths=[0.74 * inch])
    label_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    header = Table([[label_box, p(title, "card_title")]], colWidths=[0.84 * inch, 4.30 * inch])
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    content = [header]
    content.extend(body_items)
    content.extend([Spacer(1, 4), code_box(command, short=(command == OFFLINE_COMMAND))])
    outer = Table([[content]], colWidths=[5.28 * inch])
    outer.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return outer


def system_method_table():
    rows = [
        [p("系统", "table_head"), p("当前建议", "table_head"), p("测试说明", "table_head")],
        [p("Raspberry Pi OS Desktop", "table_bold"), p("联网或离线", "table"), p("正式目标，要求画面和触摸均通过。", "table")],
        [p("Raspberry Pi OS Lite", "table_bold"), p("联网或离线", "table"), p("显示文本登录终端属于正常。", "table")],
        [p("Ubuntu / Kali / DietPi / RetroPie", "table_bold"), p("探索性测试", "table"), p("可先运行同一命令，记录完整输出，暂不对客户承诺。", "table")],
        [p("LibreELEC / Batocera", "table_bold"), p("仅记录", "table"), p("当前脚本可能会安全停止，不要自行加 --force。", "table")],
    ]
    table = Table(rows, colWidths=[1.70 * inch, 0.95 * inch, 2.63 * inch], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def expected_cards():
    desktop = [p("Raspberry Pi OS Desktop", "card_title"), p("重启后等待 30-60 秒，屏幕应显示桌面，触摸应能移动指针。", "body")]
    lite = [p("Raspberry Pi OS Lite", "card_title"), p("屏幕应显示文本登录终端。Lite 本身没有桌面，出现文字界面属于正常。", "body")]
    table = Table([[desktop, lite]], colWidths=[2.58 * inch, 2.58 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), PALE),
                ("BACKGROUND", (1, 0), (1, 0), PALE_2),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def troubleshooting_table():
    rows = [
        [p("现象", "table_head"), p("首先检查", "table_head")],
        [p("白屏或只亮背光", "table_bold"), p("确认安装没有报错，拔掉 HDMI，再检查 40-pin 对齐。", "table")],
        [p("完全不亮", "table_bold"), p("检查 5V 电源、USB 线、排针对齐和 GPIO18 冲突。", "table")],
        [p("有画面，触摸无效", "table_bold"), p("移除其他 SPI 设备，检查 GPIO27 和触摸屏排线。", "table")],
        [p("触摸方向错误", "table_bold"), p("先恢复默认方向；旋转画面后还需要单独设置触摸变换。", "table")],
        [p("闪烁或颜色错误", "table_bold"), p("检查电源质量、排针焊点、接口插入情况和屏幕批次。", "table")],
        [p("程序窗口显示不全", "table_bold"), p("屏幕原生分辨率为 480x320，部分应用需要更大屏幕。", "table")],
    ]
    table = Table(rows, colWidths=[1.68 * inch, 3.60 * inch], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE_2]),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def support_block():
    left = [
        p("失败时收集诊断报告", "card_title"),
        p("在解压后的离线包目录中运行：", "small"),
        Spacer(1, 3),
        code_box(DIAG_COMMAND, width=3.20 * inch),
        Spacer(1, 4),
        p("保存完整终端输出，同时拍摄屏幕现象和 40-pin 连接照片。", "small"),
    ]
    right = [
        p("下载地址", "card_title"),
        p(f'<link href="{REPO_URL}" color="#1D6D5D"><b>github.com/iUniker/<br/>P035260107-easy-setup</b></link>', "body"),
        Spacer(1, 5),
        p("诊断报告不收集密码、Wi-Fi 密码或用户文件。", "small"),
    ]
    table = Table([[left, right]], colWidths=[3.44 * inch, 1.72 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_2),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def numbered_hardware_steps():
    items = [
        ("1", "断开电源和所有连接线。"),
        ("2", "按图对齐四个 PCB 固定孔。"),
        ("3", "确认 40-pin 每一个位置都对齐。"),
        ("4", "保持水平，均匀向下压紧。"),
    ]
    rows = [[number_badge(number), p(text, "body")] for number, text in items]
    table = Table(rows, colWidths=[0.34 * inch, 2.02 * inch])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def connection_reference():
    alignment = RLImage(str(ALIGNMENT_IMAGE), width=2.70 * inch, height=2.17 * inch)
    instructions = [
        p("安全连接", "card_title"),
        numbered_hardware_steps(),
        Spacer(1, 4),
        p("<b>严禁在接口错开一排或一列时通电。</b>错位可能导致主板短路。", "callout"),
    ]
    table = Table([[alignment, instructions]], colWidths=[2.83 * inch, 2.45 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_2),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def legend_badge(label: str, background):
    badge = Table([["", p(label, "legend")]], colWidths=[0.13 * inch, 0.74 * inch])
    badge.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), background),
                ("BOX", (0, 0), (0, 0), 0.3, background),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    return badge


def gpio_legend():
    badges = [
        legend_badge("同步控制", PURPLE),
        legend_badge("蓝色数据", BLUE),
        legend_badge("绿色数据", CHANNEL_GREEN),
        legend_badge("红色数据", RED),
        legend_badge("触摸", TOUCH),
        legend_badge("背光", BACKLIGHT),
        legend_badge("本屏未占用", AVAILABLE),
        legend_badge("电源 / GND", PIN_GRAY),
    ]
    table = Table([badges[:4], badges[4:]], colWidths=[1.30 * inch] * 4)
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    return table


PIN_FUNCTIONS = {
    1: ("3.3V - 电源", PIN_GRAY),
    2: ("5V - 电源", PIN_GRAY),
    3: ("GPIO2 - 垂直同步", PURPLE),
    4: ("5V - 电源", PIN_GRAY),
    5: ("GPIO3 - 水平同步", PURPLE),
    6: ("GND", PIN_GRAY),
    7: ("GPIO4 - 蓝色0", BLUE),
    8: ("GPIO14 - 绿色2", CHANNEL_GREEN),
    9: ("GND", PIN_GRAY),
    10: ("GPIO15 - 绿色3", CHANNEL_GREEN),
    11: ("GPIO17 - 绿色5", CHANNEL_GREEN),
    12: ("GPIO18 - 背光", BACKLIGHT),
    13: ("GPIO27 - 触摸中断", TOUCH),
    14: ("GND", PIN_GRAY),
    15: ("GPIO22 - 红色2", RED),
    16: ("GPIO23 - 红色3", RED),
    17: ("3.3V - 电源", PIN_GRAY),
    18: ("GPIO24 - 红色4", RED),
    19: ("GPIO10 - 触摸 MOSI", TOUCH),
    20: ("GND", PIN_GRAY),
    21: ("GPIO9 - 触摸 MISO", TOUCH),
    22: ("GPIO25 - 本屏未占用", AVAILABLE),
    23: ("GPIO11 - 触摸 SCLK", TOUCH),
    24: ("GPIO8 - 蓝色4", BLUE),
    25: ("GND", PIN_GRAY),
    26: ("GPIO7 - 蓝色3", BLUE),
    27: ("GPIO0 - 像素时钟", PURPLE),
    28: ("GPIO1 - 数据使能", PURPLE),
    29: ("GPIO5 - 蓝色1", BLUE),
    30: ("GND", PIN_GRAY),
    31: ("GPIO6 - 蓝色2", BLUE),
    32: ("GPIO12 - 绿色0", CHANNEL_GREEN),
    33: ("GPIO13 - 绿色1", CHANNEL_GREEN),
    34: ("GND", PIN_GRAY),
    35: ("GPIO19 - 本屏未占用", AVAILABLE),
    36: ("GPIO16 - 绿色4", CHANNEL_GREEN),
    37: ("GPIO26 - 本屏未占用", AVAILABLE),
    38: ("GPIO20 - 红色0", RED),
    39: ("GND", PIN_GRAY),
    40: ("GPIO21 - 红色1", RED),
}


def gpio_pinout():
    rows = []
    style_commands = [
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
    ]
    for row_index in range(20):
        odd_pin = row_index * 2 + 1
        even_pin = odd_pin + 1
        odd_label, odd_color = PIN_FUNCTIONS[odd_pin]
        even_label, even_color = PIN_FUNCTIONS[even_pin]
        rows.append(
            [
                p(odd_label, "pin_left"),
                p(str(odd_pin), "pin_number"),
                p(str(even_pin), "pin_number"),
                p(even_label, "pin_right"),
            ]
        )
        style_commands.extend(
            [
                ("BACKGROUND", (1, row_index), (1, row_index), odd_color),
                ("BACKGROUND", (2, row_index), (2, row_index), even_color),
            ]
        )
    table = Table(rows, colWidths=[2.12 * inch, 0.42 * inch, 0.42 * inch, 2.12 * inch])
    table.setStyle(TableStyle(style_commands))
    return table


def breakout_reference():
    pcb = RLImage(str(PCB_BACK_IMAGE), width=1.70 * inch, height=1.70 * inch)
    notes = [
        p("板载引出接口", "card_title"),
        p("屏幕 PCB 引出了 <b>5V、GPIO26、GPIO19、GPIO25 和 GND</b>。GPIO19、GPIO25 和 GPIO26 不被当前屏幕配置占用。", "body"),
        Spacer(1, 4),
        p("屏幕仍然物理占用整个 40-pin 接口。首次测试时请移除其他 HAT 和 SPI0 设备。", "small"),
        Spacer(1, 4),
        p("3.51 英寸 / 480x320 / RGB565 / 四线电阻触摸 / Raspberry Pi Zero 系列", "small"),
    ]
    table = Table([[pcb, notes]], colWidths=[1.84 * inch, 3.44 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_2),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def test_matrix():
    rows = [
        [p("系统与镜像", "table_head"), p("树莓派型号", "table_head"), p("安装", "table_head"), p("画面", "table_head"), p("触摸", "table_head"), p("重启", "table_head"), p("结果/错误摘要", "table_head")],
        [p("Raspberry Pi OS Desktop 32-bit", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
        [p("Raspberry Pi OS Desktop 64-bit", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
        [p("Raspberry Pi OS Lite 32-bit", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
        [p("Raspberry Pi OS Lite 64-bit", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
        [p("Ubuntu Server / Desktop", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
        [p("Kali Linux", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
        [p("DietPi / Debian", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
        [p("RetroPie Bookworm", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
        [p("LibreELEC (探索性)", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
        [p("Batocera (探索性)", "table_bold"), p("", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("[ ]", "table"), p("", "table")],
    ]
    table = Table(rows, colWidths=[1.42 * inch, 0.72 * inch, 0.45 * inch, 0.45 * inch, 0.45 * inch, 0.45 * inch, 1.34 * inch], repeatRows=1, rowHeights=[0.29 * inch] + [0.34 * inch] * 10)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE_2]),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (2, 1), (5, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def test_record_fields():
    rows = [
        [p("测试人：________________", "field"), p("日期：________________", "field"), p("屏幕批次：________________", "field")],
        [p("Pi 型号：________________", "field"), p("OS 完整版本：________________", "field"), p("内核版本：________________", "field")],
        [p("安装方式：[ ] 联网  [ ] 离线", "field"), p("架构：[ ] 32-bit  [ ] 64-bit", "field"), p("结果：[ ] 通过  [ ] 失败", "field")],
    ]
    table = Table(rows, colWidths=[1.74 * inch, 1.78 * inch, 1.76 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_2),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def functional_checklist():
    left = [
        p("稳定性检查", "card_title"),
        p("[ ] 断电冷启动 3 次，每次均有画面", "body"),
        p("[ ] 系统重启 3 次，每次均恢复显示", "body"),
        p("[ ] 连续运行 30 分钟，无闪烁和花屏", "body"),
        p("[ ] 执行系统更新并重启后再测试", "body"),
    ]
    right = [
        p("显示和触摸", "card_title"),
        p("[ ] 画面方向、颜色和 480x320 显示正常", "body"),
        p("[ ] 触摸中心及四个角落都能响应", "body"),
        p("[ ] 触摸坐标与画面方向一致", "body"),
        p("[ ] 拔掉 HDMI，不连接其他 GPIO 设备", "body"),
    ]
    table = Table([[left, right]], colWidths=[2.58 * inch, 2.58 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_2),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def build_pdf(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=0.50 * inch,
        rightMargin=0.50 * inch,
        topMargin=0.89 * inch,
        bottomMargin=0.47 * inch,
        title="MazerPi MZP351HV00TR 中文工程测试指南",
        author="MazerPi",
        subject="MZP351HV00TR 安装、硬件、GPIO 及多系统测试指南",
        creator="MazerPi Easy Setup",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="letter", frames=[frame], onPage=header_footer)])

    online = method_card(
        "方法 1",
        "联网安装 - 主要方法",
        [p("适用于树莓派能访问 GitHub 的情况。打开终端或通过 SSH 连接，粘贴下面一行命令。完整下载成功后才会执行。", "body")],
        ONLINE_COMMAND,
        PALE_2,
    )
    offline = method_card(
        "方法 2",
        "离线 ZIP - 树莓派无需互联网",
        [
            p("1. 在有网络的电脑上下载离线 ZIP，解压后将完整文件夹拷贝到树莓派。", "body"),
            p("2. 进入该文件夹并运行下面命令。Desktop 也可双击 INSTALL 选择 Execute/Run。", "body"),
        ],
        OFFLINE_COMMAND,
        WHITE,
    )

    story = [
        Spacer(1, 4),
        p("3.51 英寸 LCD 快速安装", "title"),
        p("中文工程测试版：不替换客户的系统，不删除应用、网络设置或用户文件。", "subtitle"),
        callout("<b>重要：</b>本文档用于供应商和工程测试，不是最终客户版。美国客户发布前，必须完成本文档第 4 页的测试记录。"),
        Spacer(1, 7),
        p("安装前", "section"),
        preflight_grid(),
        Spacer(1, 8),
        online,
        Spacer(1, 7),
        offline,
        Spacer(1, 8),
        p("不同系统的当前测试方法", "section"),
        system_method_table(),
        Spacer(1, 5),
        p("供应商如果无法访问 raw.githubusercontent.com，请使用离线 ZIP；网络不可达不属于安装器故障。", "center_small"),
        PageBreak(),
        Spacer(1, 4),
        p("自动重启后的正常结果", "title"),
        p("等待 30-60 秒。只亮背光不算通过，必须有可读取的画面。", "subtitle"),
        expected_cards(),
        Spacer(1, 9),
        p("常见故障排查", "section"),
        troubleshooting_table(),
        Spacer(1, 9),
        p("兼容性与测试边界", "section"),
        callout("<b>当前正式目标：</b>Raspberry Pi Zero、Zero W/WH、Zero 2 W/2 WH，配合已测试的 Raspberry Pi OS。<br/><b>探索性测试：</b>Ubuntu、Kali、DietPi/Debian 和 RetroPie。<br/><b>尚未适配：</b>LibreELEC、Batocera、Android 及自定义内核。遇到停止信息时请记录，不要直接使用 --force。"),
        Spacer(1, 9),
        support_block(),
        Spacer(1, 8),
        p("四线电阻触摸需要轻压，可使用指尖、指甲或触控笔；不支持多点触摸手势。", "center_small"),
        PageBreak(),
        Spacer(1, 4),
        p("硬件连接与 GPIO 参考", "title"),
        p("必须在断电状态下连接屏幕。先通过四个固定孔确认方向，再插入 40-pin 接口。", "subtitle"),
        connection_reference(),
        Spacer(1, 8),
        p("GPIO 占用总览", "section"),
        p("屏幕占用 25 个 GPIO。中间两列为 Raspberry Pi 40-pin 接口的物理引脚编号。", "small"),
        Spacer(1, 3),
        gpio_legend(),
        Spacer(1, 4),
        gpio_pinout(),
        Spacer(1, 7),
        breakout_reference(),
        PageBreak(),
        Spacer(1, 4),
        p("多系统工程测试记录", "title"),
        p("每个系统尽量使用官方原始镜像和空白 microSD 卡。请填写完整镜像版本，不要只写系统名称。", "subtitle"),
        test_record_fields(),
        Spacer(1, 8),
        callout("<b>联网测试：</b>必须能访问 raw.githubusercontent.com。<br/><b>离线测试：</b>必须将解压后的完整文件夹复制到树莓派，不能只复制 install.sh。"),
        Spacer(1, 8),
        p("系统测试矩阵", "section"),
        test_matrix(),
        Spacer(1, 8),
        functional_checklist(),
        Spacer(1, 8),
        callout("<b>失败处理：</b>不要立即重装系统。请保存安装器的完整终端输出，运行诊断命令，并提供树莓派型号、OS 版本、内核版本、屏幕现象和连接照片。"),
    ]
    doc.build(story)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: create-quick-start-zh-pdf.py OUTPUT.pdf")
    build_pdf(Path(sys.argv[1]).expanduser().resolve())


if __name__ == "__main__":
    main()
