#!/usr/bin/env python3
"""Generate the customer-facing MazerPi MZP351 Quick Start PDF."""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
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
OFFLINE_URL = (
    "https://github.com/iUniker/P035260107-easy-setup/releases/download/"
    f"v{VERSION}/MazerPi-MZP351-Offline-Setup.zip"
)
REPO_URL = "https://github.com/iUniker/P035260107-easy-setup"


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=27,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=5,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=MUTED,
            spaceAfter=8,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=INK,
            spaceBefore=2,
            spaceAfter=6,
        ),
        "card_title": ParagraphStyle(
            "CardTitle",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=INK,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.7,
            leading=12.3,
            textColor=INK,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.7,
            leading=10.5,
            textColor=MUTED,
        ),
        "table": ParagraphStyle(
            "Table",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.7,
            leading=10.2,
            textColor=INK,
        ),
        "table_bold": ParagraphStyle(
            "TableBold",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.7,
            leading=10.2,
            textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "TableHead",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.6,
            leading=9.5,
            textColor=WHITE,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=6.15,
            leading=8,
            textColor=LIME,
            splitLongWords=False,
        ),
        "code_short": ParagraphStyle(
            "CodeShort",
            parent=base["Code"],
            fontName="Courier-Bold",
            fontSize=8.2,
            leading=10,
            textColor=LIME,
        ),
        "code_diag": ParagraphStyle(
            "CodeDiag",
            parent=base["Code"],
            fontName="Courier-Bold",
            fontSize=6.6,
            leading=8.5,
            textColor=LIME,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=11.3,
            textColor=AMBER_INK,
        ),
        "center_small": ParagraphStyle(
            "CenterSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            alignment=TA_CENTER,
            textColor=MUTED,
        ),
        "pin_left": ParagraphStyle(
            "PinLeft",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.1,
            leading=7.2,
            alignment=TA_RIGHT,
            textColor=INK,
        ),
        "pin_right": ParagraphStyle(
            "PinRight",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.1,
            leading=7.2,
            alignment=TA_LEFT,
            textColor=INK,
        ),
        "pin_number": ParagraphStyle(
            "PinNumber",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.2,
            leading=7.2,
            alignment=TA_CENTER,
            textColor=WHITE,
        ),
        "legend": ParagraphStyle(
            "Legend",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=6.2,
            leading=7.4,
            textColor=INK,
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
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#AFC3BD"))
    canvas.drawString(0.88 * inch, height - 0.53 * inch, "DISPLAY SETUP")
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    right_text = "MZP351HV00TR / P035260107"
    canvas.drawRightString(width - 0.50 * inch, height - 0.43 * inch, right_text)

    canvas.setStrokeColor(BORDER)
    canvas.line(0.50 * inch, 0.39 * inch, width - 0.50 * inch, 0.39 * inch)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.7)
    canvas.drawString(0.50 * inch, 0.22 * inch, f"Quick Start {VERSION} - Engineering preview")
    canvas.drawRightString(width - 0.50 * inch, 0.22 * inch, f"Page {doc.page}")
    canvas.restoreState()


def rounded_label(text: str, background=GREEN, foreground=WHITE, width=0.72 * inch):
    table = Table([[p(text, "table_head")]], colWidths=[width])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("TEXTCOLOR", (0, 0), (-1, -1), foreground),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("BOX", (0, 0), (-1, -1), 0.5, background),
            ]
        )
    )
    return table


def preflight_grid():
    items = [
        ("1", "Power off before attaching the LCD."),
        ("2", "Align the 40-pin header carefully."),
        ("3", "Remove other GPIO HATs for the first test."),
        ("4", "Disconnect HDMI and use a stable 5V supply."),
    ]
    cells = []
    for number, text in items:
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
        cell = Table([[badge, p(text, "small")]], colWidths=[0.31 * inch, 2.14 * inch])
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
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return grid


def decision_table():
    rows = [
        [p("System", "table_head"), p("Internet", "table_head"), p("Use", "table_head"), p("Fastest action", "table_head")],
        [p("Raspberry Pi OS Desktop", "table_bold"), p("Yes", "table"), p("Method 1", "table_bold"), p("Open Terminal or connect by SSH, then paste the online command.", "table")],
        [p("Raspberry Pi OS Desktop", "table_bold"), p("No", "table"), p("Method 2", "table_bold"), p("Transfer and extract the ZIP, then double-click <b>INSTALL</b>.", "table")],
        [p("Raspberry Pi OS Lite / headless", "table_bold"), p("Yes", "table"), p("Method 1", "table_bold"), p("Connect by SSH and paste the online command.", "table")],
        [p("Raspberry Pi OS Lite / headless", "table_bold"), p("No", "table"), p("Method 2", "table_bold"), p("Transfer and extract the ZIP, then run <b>bash INSTALL</b>.", "table")],
    ]
    table = Table(rows, colWidths=[1.22 * inch, 0.56 * inch, 0.76 * inch, 2.74 * inch], repeatRows=1)
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
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ALIGN", (1, 1), (2, -1), "CENTER"),
            ]
        )
    )
    return table


def code_box(command: str, short=False, diagnostic=False, width=5.14 * inch):
    style = "code_diag" if diagnostic else "code_short" if short else "code"
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


def method_one():
    header = Table(
        [[rounded_label("METHOD 1"), p("Online install - recommended", "card_title")]],
        colWidths=[0.84 * inch, 4.30 * inch],
    )
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    content = [
        header,
        p("Use when the Raspberry Pi can reach the Internet. Open Terminal on the Pi or connect by SSH, then run:", "body"),
        Spacer(1, 4),
        code_box(ONLINE_COMMAND),
        Spacer(1, 4),
        p("The complete script downloads before it runs. The installer then checks compatibility, backs up <b>config.txt</b>, installs the managed display settings, and reboots automatically.", "small"),
    ]
    outer = Table([[content]], colWidths=[5.28 * inch])
    outer.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE_2), ("BOX", (0, 0), (-1, -1), 0.7, BORDER), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    return outer


def method_two():
    header = Table(
        [[rounded_label("METHOD 2"), p("Offline ZIP - no Internet required on the Pi", "card_title")]],
        colWidths=[0.84 * inch, 4.30 * inch],
    )
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    steps = Table(
        [
            [p("1", "table_bold"), p(f'<link href="{OFFLINE_URL}" color="#1D6D5D"><b>Download the small offline ZIP</b></link> on any connected device.', "body")],
            [p("2", "table_bold"), p("Transfer it to the Raspberry Pi and extract the complete ZIP.", "body")],
            [p("3", "table_bold"), p("Desktop: double-click <b>INSTALL</b> and choose <b>Execute</b> or <b>Run</b> if prompted.", "body")],
        ],
        colWidths=[0.24 * inch, 4.90 * inch],
    )
    steps.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TEXTCOLOR", (0, 0), (0, -1), GREEN), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    content = [
        header,
        steps,
        Spacer(1, 4),
        p("Raspberry Pi OS Lite / headless fallback:", "small"),
        Spacer(1, 2),
        code_box("bash INSTALL", short=True),
    ]
    outer = Table([[content]], colWidths=[5.28 * inch])
    outer.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), WHITE), ("BOX", (0, 0), (-1, -1), 0.7, BORDER), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    return outer


def expected_cards():
    desktop = [p("Raspberry Pi OS Desktop", "card_title"), p("After 30-60 seconds, the LCD should show the desktop. Touch should act like a pointer and requires light pressure.", "body")]
    lite = [p("Raspberry Pi OS Lite", "card_title"), p("The LCD should show a text login console. A text screen is normal because Lite does not include a graphical desktop.", "body")]
    table = Table([[desktop, lite]], colWidths=[2.58 * inch, 2.58 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), PALE), ("BACKGROUND", (1, 0), (1, 0), PALE_2), ("BOX", (0, 0), (-1, -1), 0.6, BORDER), ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    return table


def troubleshooting_table():
    data = [
        [p("Symptom", "table_head"), p("Check first", "table_head")],
        [p("White screen / backlight only", "table_bold"), p("Confirm installation completed, disconnect HDMI, then check 40-pin alignment.", "table")],
        [p("Completely dark", "table_bold"), p("Check the 5V supply, USB cable, header alignment, and GPIO18 conflicts.", "table")],
        [p("Picture works, touch does not", "table_bold"), p("Remove other SPI devices; check GPIO27 and the touchscreen connector.", "table")],
        [p("Wrong touch direction", "table_bold"), p("Return the display to default orientation. Rotation also needs a touch transform.", "table")],
        [p("Flicker / incorrect colours", "table_bold"), p("Check power quality, header solder joints, connector seating, and panel batch.", "table")],
        [p("Window does not fit", "table_bold"), p("The native resolution is 480x320; some applications require a larger display.", "table")],
    ]
    table = Table(data, colWidths=[1.68 * inch, 3.60 * inch], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), DARK), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE_2]), ("BOX", (0, 0), (-1, -1), 0.6, BORDER), ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return table


def callout(text: str):
    table = Table([[p(text, "callout")]], colWidths=[5.28 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AMBER), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#E8C96B")), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return table


def support_block():
    left = [
        p("Need support?", "card_title"),
        p("From the extracted offline package, run:", "small"),
        Spacer(1, 3),
        code_box("sudo bash diagnose.sh | tee mzp351-diagnostic.txt", diagnostic=True, width=3.18 * inch),
        Spacer(1, 4),
        p("Send the report with the Pi model, OS version, screen symptom, and a clear photo of the 40-pin connection.", "small"),
    ]
    right = [
        p("Updates and downloads", "card_title"),
        p(f'<link href="{REPO_URL}" color="#1D6D5D"><b>github.com/iUniker/<br/>P035260107-easy-setup</b></link>', "body"),
        Spacer(1, 5),
        p("The diagnostic report does not collect passwords, Wi-Fi credentials, or user files.", "small"),
    ]
    table = Table([[left, right]], colWidths=[3.42 * inch, 1.74 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE_2), ("BOX", (0, 0), (-1, -1), 0.6, BORDER), ("INNERGRID", (0, 0), (-1, -1), 0.4, BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    return table


def numbered_hardware_steps():
    items = [
        ("1", "Disconnect power and all cables."),
        ("2", "Match all four mounting holes as shown."),
        ("3", "Align every contact on the 40-pin header."),
        ("4", "Press straight down and seat the header evenly."),
    ]
    rows = []
    for number, text in items:
        badge = Table([[p(number, "table_head")]], colWidths=[0.25 * inch], rowHeights=[0.25 * inch])
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
        rows.append([badge, p(text, "body")])
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
        p("Safe connection", "card_title"),
        numbered_hardware_steps(),
        Spacer(1, 4),
        p(
            "<b>Never power the Pi with the connector offset by one row or one column.</b> "
            "A misaligned connection can short the board.",
            "callout",
        ),
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
        legend_badge("Timing", PURPLE),
        legend_badge("Blue data", BLUE),
        legend_badge("Green data", CHANNEL_GREEN),
        legend_badge("Red data", RED),
        legend_badge("Touch", TOUCH),
        legend_badge("Backlight", BACKLIGHT),
        legend_badge("Not used", AVAILABLE),
        legend_badge("Power / GND", PIN_GRAY),
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
    1: ("3.3V - power", PIN_GRAY),
    2: ("5V - power", PIN_GRAY),
    3: ("GPIO2 - VSYNC", PURPLE),
    4: ("5V - power", PIN_GRAY),
    5: ("GPIO3 - HSYNC", PURPLE),
    6: ("GND", PIN_GRAY),
    7: ("GPIO4 - BLUE0", BLUE),
    8: ("GPIO14 - GREEN2", CHANNEL_GREEN),
    9: ("GND", PIN_GRAY),
    10: ("GPIO15 - GREEN3", CHANNEL_GREEN),
    11: ("GPIO17 - GREEN5", CHANNEL_GREEN),
    12: ("GPIO18 - BACKLIGHT", BACKLIGHT),
    13: ("GPIO27 - TOUCH IRQ", TOUCH),
    14: ("GND", PIN_GRAY),
    15: ("GPIO22 - RED2", RED),
    16: ("GPIO23 - RED3", RED),
    17: ("3.3V - power", PIN_GRAY),
    18: ("GPIO24 - RED4", RED),
    19: ("GPIO10 - TOUCH MOSI", TOUCH),
    20: ("GND", PIN_GRAY),
    21: ("GPIO9 - TOUCH MISO", TOUCH),
    22: ("GPIO25 - NOT USED", AVAILABLE),
    23: ("GPIO11 - TOUCH SCLK", TOUCH),
    24: ("GPIO8 - BLUE4", BLUE),
    25: ("GND", PIN_GRAY),
    26: ("GPIO7 - BLUE3", BLUE),
    27: ("GPIO0 - PCLK", PURPLE),
    28: ("GPIO1 - DATA ENABLE", PURPLE),
    29: ("GPIO5 - BLUE1", BLUE),
    30: ("GND", PIN_GRAY),
    31: ("GPIO6 - BLUE2", BLUE),
    32: ("GPIO12 - GREEN0", CHANNEL_GREEN),
    33: ("GPIO13 - GREEN1", CHANNEL_GREEN),
    34: ("GND", PIN_GRAY),
    35: ("GPIO19 - NOT USED", AVAILABLE),
    36: ("GPIO16 - GREEN4", CHANNEL_GREEN),
    37: ("GPIO26 - NOT USED", AVAILABLE),
    38: ("GPIO20 - RED0", RED),
    39: ("GND", PIN_GRAY),
    40: ("GPIO21 - RED1", RED),
}


def gpio_pinout():
    rows = []
    style_commands = [
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1.3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.3),
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
        p("On-board breakout", "card_title"),
        p(
            "The LCD PCB exposes <b>5V, GPIO26, GPIO19, GPIO25, and GND</b>. "
            "GPIO19, GPIO25, and GPIO26 are not used by this display configuration.",
            "body",
        ),
        Spacer(1, 4),
        p(
            "The display still occupies the full 40-pin connector. Remove other HATs and SPI0 devices for the first test.",
            "small",
        ),
        Spacer(1, 4),
        p("3.51-inch / 480x320 / RGB565 / 4-wire resistive touch / Raspberry Pi Zero family", "small"),
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


def build_pdf(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=0.50 * inch,
        rightMargin=0.50 * inch,
        topMargin=0.89 * inch,
        bottomMargin=0.47 * inch,
        title="MazerPi MZP351HV00TR Quick Start",
        author="MazerPi",
        subject="Setup, connection, and GPIO reference for the MZP351HV00TR Raspberry Pi display",
        creator="MazerPi Easy Setup",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="letter", frames=[frame], onPage=header_footer)])

    story = [
        Spacer(1, 4),
        p("3.51-inch LCD Quick Start", "title"),
        p("Keep your existing Raspberry Pi OS, applications, network settings, and user files. Choose the row that matches your system and Internet access.", "subtitle"),
        callout("<b>ENGINEERING PREVIEW:</b> Validate this package on test hardware before customer release. Supported target: Raspberry Pi Zero / Zero W / Zero 2 W with current Raspberry Pi OS overlays."),
        Spacer(1, 8),
        p("Before you start", "section"),
        preflight_grid(),
        Spacer(1, 9),
        p("Choose the fastest method", "section"),
        decision_table(),
        Spacer(1, 9),
        method_one(),
        Spacer(1, 7),
        method_two(),
        PageBreak(),
        Spacer(1, 4),
        p("After the automatic reboot", "title"),
        p("Allow 30-60 seconds for startup. Backlight alone is not a pass; the expected result is a readable picture.", "subtitle"),
        expected_cards(),
        Spacer(1, 10),
        p("Troubleshooting", "section"),
        troubleshooting_table(),
        Spacer(1, 10),
        p("Compatibility and conflicts", "section"),
        callout("<b>Supported:</b> Raspberry Pi Zero, Zero W/WH, and Zero 2 W/2 WH with tested Raspberry Pi OS releases.<br/><b>Not yet supported:</b> Ubuntu, RetroPie, Batocera, Kali, LibreELEC, Android, and custom kernels unless the exact release is listed as tested.<br/><b>GPIO conflicts:</b> Other DPI displays, SPI0 devices, GPIO HATs, GPIO18, and GPIO27 devices may prevent the LCD or touch from working."),
        Spacer(1, 10),
        support_block(),
        Spacer(1, 8),
        p("Resistive touch requires light pressure from a fingertip, fingernail, or stylus. Multi-touch gestures are not supported.", "center_small"),
        PageBreak(),
        Spacer(1, 4),
        p("Hardware & GPIO Reference", "title"),
        p("Connect the display only while power is disconnected. Use the mounting holes to confirm orientation before seating the 40-pin header.", "subtitle"),
        connection_reference(),
        Spacer(1, 8),
        p("GPIO use at a glance", "section"),
        p("The display uses 25 GPIOs. Physical pin numbers are shown in the two colored center columns.", "small"),
        Spacer(1, 3),
        gpio_legend(),
        Spacer(1, 4),
        gpio_pinout(),
        Spacer(1, 7),
        breakout_reference(),
    ]
    doc.build(story)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: create-quick-start-pdf.py OUTPUT.pdf")
    build_pdf(Path(sys.argv[1]).expanduser().resolve())


if __name__ == "__main__":
    main()
