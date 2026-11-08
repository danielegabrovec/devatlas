"""Native Qt components for the library, sharing semantic design tokens."""
from __future__ import annotations
from functools import lru_cache
import html
import math

from PySide6.QtCore import Qt, QPointF, QRectF, QSize, Signal
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QIcon, QPainter, QPainterPath, QPen, QPixmap, QTextLayout, QTextOption
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel, QLayout, QPushButton,
    QScrollArea, QSizePolicy, QStyle, QStyledItemDelegate, QVBoxLayout, QWidget)

from devatlas.models import STATUSES
from devatlas.theme import THEMES, COMPONENTS, technology_tone, status_tone


def current_theme():
    return THEMES.get(QApplication.instance().property("devatlasTheme"), THEMES["light"])


@lru_cache(maxsize=256)
def _paint_icon(name, color, size, scale):
    pixmap = QPixmap(round(size * scale), round(size * scale))
    pixmap.setDevicePixelRatio(scale)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(size / 24, size / 24)
    painter.setPen(QPen(QColor(color), 1.7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    path = QPainterPath()
    if name in ("library", "project"):
        painter.drawRoundedRect(QRectF(4, 3, 16, 18), 2, 2)
        painter.drawLine(8, 3, 8, 21)
        painter.drawLine(11, 8, 17, 8)
        painter.drawLine(11, 12, 16, 12)
    elif name == "code":
        path.moveTo(8, 6); path.lineTo(3, 12); path.lineTo(8, 18)
        path.moveTo(16, 6); path.lineTo(21, 12); path.lineTo(16, 18)
        path.moveTo(14, 4); path.lineTo(10, 20)
        painter.drawPath(path)
    elif name == "desktop":
        painter.drawRoundedRect(QRectF(3, 4, 18, 13), 2, 2)
        painter.drawLine(8, 21, 16, 21); painter.drawLine(12, 17, 12, 21)
    elif name == "web":
        painter.drawEllipse(QRectF(3, 3, 18, 18))
        painter.drawEllipse(QRectF(8, 3, 8, 18))
        painter.drawLine(3, 12, 21, 12)
    elif name == "database":
        painter.drawEllipse(QRectF(4, 3, 16, 6))
        path.moveTo(4, 6); path.lineTo(4, 18); path.cubicTo(4, 22, 20, 22, 20, 18); path.lineTo(20, 6)
        path.moveTo(4, 12); path.cubicTo(4, 16, 20, 16, 20, 12)
        painter.drawPath(path)
    elif name in ("tools", "terminal"):
        painter.drawRoundedRect(QRectF(3, 4, 18, 16), 2, 2)
        path.moveTo(6, 8); path.lineTo(10, 12); path.lineTo(6, 16)
        path.moveTo(13, 16); path.lineTo(18, 16)
        painter.drawPath(path)
    elif name == "star":
        for index in range(10):
            angle = -math.pi / 2 + index * math.pi / 5
            radius = 9 if index % 2 == 0 else 4
            point = QPointF(12 + radius * math.cos(angle), 12 + radius * math.sin(angle))
            path.moveTo(point) if index == 0 else path.lineTo(point)
        path.closeSubpath(); painter.drawPath(path)
    elif name in ("clock", "recent"):
        painter.drawEllipse(QRectF(3, 3, 18, 18))
        path.moveTo(12, 7); path.lineTo(12, 12); path.lineTo(16, 14); painter.drawPath(path)
    elif name == "person":
        painter.drawEllipse(QRectF(8, 3, 8, 8))
        path.moveTo(4, 21); path.cubicTo(4, 11, 20, 11, 20, 21); painter.drawPath(path)
    elif name == "bookmark":
        path.moveTo(6, 3); path.lineTo(18, 3); path.lineTo(18, 21); path.lineTo(12, 17); path.lineTo(6, 21); path.closeSubpath(); painter.drawPath(path)
    elif name == "folder":
        path.moveTo(3, 7); path.lineTo(3, 20); path.lineTo(21, 20); path.lineTo(21, 6); path.lineTo(11, 6); path.lineTo(9, 3); path.lineTo(3, 3); path.closeSubpath(); painter.drawPath(path)
    elif name == "route":
        painter.drawEllipse(QRectF(3, 3, 5, 5)); painter.drawEllipse(QRectF(16, 16, 5, 5))
        path.moveTo(8, 5); path.lineTo(17, 5); path.cubicTo(23, 5, 23, 13, 17, 13); path.lineTo(7, 13); path.cubicTo(1, 13, 1, 19, 7, 19); path.lineTo(16, 19); painter.drawPath(path)
    elif name == "filter":
        for x, y in ((5, 8), (12, 16), (19, 10)):
            painter.drawLine(x, 3, x, 21); painter.drawEllipse(QRectF(x - 2.5, y - 2.5, 5, 5))
    elif name == "search":
        painter.drawEllipse(QRectF(3, 3, 13, 13)); painter.drawLine(14, 14, 21, 21)
    elif name == "focus":
        for x, y, dx, dy in ((3, 3, 1, 1), (21, 3, -1, 1), (3, 21, 1, -1), (21, 21, -1, -1)):
            path.moveTo(x + dx * 5, y); path.lineTo(x, y); path.lineTo(x, y + dy * 5)
        painter.drawPath(path)
    elif name == "external":
        path.moveTo(13, 3); path.lineTo(21, 3); path.lineTo(21, 11)
        path.moveTo(21, 3); path.lineTo(10, 14)
        path.moveTo(9, 4); path.lineTo(3, 4); path.lineTo(3, 21); path.lineTo(20, 21); path.lineTo(20, 15); painter.drawPath(path)
    elif name == "alert":
        path.moveTo(12, 3); path.lineTo(22, 21); path.lineTo(2, 21); path.closeSubpath(); painter.drawPath(path)
        painter.drawLine(12, 9, 12, 14); painter.drawPoint(12, 18)
    else:
        painter.drawRoundedRect(QRectF(4, 4, 6, 6), 1, 1); painter.drawRoundedRect(QRectF(14, 4, 6, 6), 1, 1)
        painter.drawRoundedRect(QRectF(4, 14, 6, 6), 1, 1); painter.drawRoundedRect(QRectF(14, 14, 6, 6), 1, 1)
    painter.end()
    return QIcon(pixmap)


def local_icon(name, color=None, size=20):
    app = QApplication.instance()
    return _paint_icon(name, color or current_theme()["muted"], size, float(app.devicePixelRatio()))


def wrapped_lines(text, font, width, limit):
    text = str(text).replace("\n", " ")[:2000]
    layout = QTextLayout(text, font)
    option = QTextOption()
    option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
    layout.setTextOption(option)
    raw = text.encode("utf-16-le")
    result = []
    layout.beginLayout()
    for number in range(limit):
        line = layout.createLine()
        if not line.isValid():
            break
        line.setLineWidth(max(1, width))
        start, length = line.textStart(), line.textLength()
        value = raw[start * 2:(start + length) * 2].decode("utf-16-le").rstrip()
        if number + 1 == limit and (start + length) * 2 < len(raw):
            rest = raw[start * 2:].decode("utf-16-le")
            value = QFontMetricsF(font).elidedText(rest, Qt.TextElideMode.ElideRight, max(1, width))
        result.append(value)
    layout.endLayout()
    return result


class CardDelegate(QStyledItemDelegate):
    def __init__(self, stacks, parent=None):
        super().__init__(parent)
        self.stacks = stacks

    def fonts(self):
        base = QApplication.font()
        point = max(8, base.pointSizeF())
        title, body, small = QFont(base), QFont(base), QFont(base)
        title.setPointSizeF(point + 1); title.setWeight(QFont.Weight.DemiBold)
        small.setPointSizeF(max(8, point - 1))
        return title, body, small

    def sizeHint(self, option, index):
        title, body, small = self.fonts()
        compact = QApplication.instance().property("devatlasDensity") == "compact"
        height = 64 + QFontMetricsF(small).height() * 2 + QFontMetricsF(title).lineSpacing() * 2 + QFontMetricsF(body).lineSpacing() * (1 if compact else 2)
        return QSize(280, math.ceil(height))

    def paint(self, painter, option, index):
        recipe = index.data(Qt.ItemDataRole.UserRole)
        if recipe is None:
            return
        theme = current_theme()
        title_font, body_font, small_font = self.fonts()
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hover = bool(option.state & QStyle.StateFlag.State_MouseOver)
        focused = bool(option.state & QStyle.StateFlag.State_HasFocus)
        card = QRectF(option.rect).adjusted(1, 4, -1, -4)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipRect(option.rect)
        painter.setBrush(QColor(theme["selection"] if selected else theme["card_hover"] if hover else theme["surface"]))
        painter.setPen(QPen(QColor(theme["accent"] if selected or focused else theme["border"]), 2 if selected or focused else 1))
        painter.drawRoundedRect(card, COMPONENTS["card_radius"], COMPONENTS["card_radius"])
        rect = card.adjusted(14, 12, -14, -12)
        painter.setFont(small_font)
        fm = QFontMetricsF(small_font)
        technology = self.stacks.get(recipe.stack, {}).get("label", recipe.stack)
        group = self.stacks.get(recipe.stack, {}).get("group", recipe.group)
        fg, bg = technology_tone(group, QApplication.instance().property("devatlasTheme"))
        tech_text = fm.elidedText(technology, Qt.TextElideMode.ElideRight, max(50, rect.width() * .58))
        badge = QRectF(rect.left(), rect.top(), fm.horizontalAdvance(tech_text) + 14, fm.height() + 7)
        painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(QColor(bg)); painter.drawRoundedRect(badge, 5, 5)
        painter.setPen(QColor(fg)); painter.drawText(badge, Qt.AlignmentFlag.AlignCenter, tech_text)
        section = "PROGETTO" if recipe.project else "PERSONALE" if recipe.personal else recipe.section
        painter.setPen(QColor(theme["muted"]))
        section_rect = QRectF(badge.right() + 8, rect.top(), max(0, rect.right() - badge.right() - 8), badge.height())
        painter.drawText(section_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, fm.elidedText(section, Qt.TextElideMode.ElideRight, section_rect.width()))
        y = badge.bottom() + 8
        painter.setFont(title_font); painter.setPen(QColor(theme["text"]))
        tfm = QFontMetricsF(title_font)
        for line in wrapped_lines(recipe.title, title_font, rect.width(), 2):
            painter.drawText(QPointF(rect.left(), y + tfm.ascent()), line)
            y += tfm.lineSpacing()
        y = badge.bottom() + 8 + tfm.lineSpacing() * 2 + 5
        painter.setFont(body_font); painter.setPen(QColor(theme["muted"]))
        bfm = QFontMetricsF(body_font)
        compact = QApplication.instance().property("devatlasDensity") == "compact"
        for line in wrapped_lines(recipe.summary, body_font, rect.width(), 1 if compact else 2):
            painter.drawText(QPointF(rect.left(), y + bfm.ascent()), line)
            y += bfm.lineSpacing()
        painter.setFont(small_font)
        status = recipe.verification.get("status", "documentato")
        status_label = STATUSES.get(status, "Revisionato")
        status_color = status_tone(status, QApplication.instance().property("devatlasTheme"))
        foot_y = rect.bottom() - fm.height()
        painter.setBrush(QColor(status_color)); painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(rect.left(), foot_y + fm.height() / 2 - 3, 6, 6))
        painter.setPen(QColor(theme["muted"]))
        status_width = max(35, rect.width() - fm.horizontalAdvance(recipe.difficulty) - 30)
        painter.drawText(QPointF(rect.left() + 12, foot_y + fm.ascent()), fm.elidedText(status_label, Qt.TextElideMode.ElideRight, status_width))
        painter.drawText(QRectF(rect.left(), foot_y, rect.width(), fm.height()), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, recipe.difficulty)
        painter.restore()


class FlowLayout(QLayout):
    def __init__(self, parent=None, spacing=6):
        super().__init__(parent)
        self.items = []
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(spacing)

    def addItem(self, item): self.items.append(item)
    def count(self): return len(self.items)
    def itemAt(self, index): return self.items[index] if 0 <= index < len(self.items) else None
    def takeAt(self, index): return self.items.pop(index) if 0 <= index < len(self.items) else None
    def expandingDirections(self): return Qt.Orientation(0)
    def hasHeightForWidth(self): return True
    def heightForWidth(self, width): return self.arrange(QRectF(0, 0, width, 0), True)
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.arrange(QRectF(rect), False)
    def sizeHint(self): return self.minimumSize()
    def minimumSize(self):
        size = QSize()
        for item in self.items: size = size.expandedTo(item.minimumSize())
        return size
    def arrange(self, rect, measure):
        from PySide6.QtCore import QRect
        x, y, row_height = rect.left(), rect.top(), 0
        for item in self.items:
            hint = item.sizeHint()
            width = min(hint.width(), max(1, rect.width()))
            if x > rect.left() and x + width > rect.right():
                x = rect.left(); y += row_height + self.spacing(); row_height = 0
            if not measure: item.setGeometry(QRect(round(x), round(y), round(width), hint.height()))
            x += width + self.spacing(); row_height = max(row_height, hint.height())
        return round(y + row_height - rect.top())


class FilterChip(QPushButton):
    def __init__(self, caption, parent=None):
        super().__init__(parent)
        self.caption = caption
        self.setText(caption.replace("&", "&&") + "  ×")
        self.setObjectName("filterChip")
        self.setAccessibleName("Rimuovi filtro " + caption)
        self.setToolTip("<p>" + html.escape(caption) + "</p>")
        self.setMaximumWidth(240)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

    def sizeHint(self):
        size = super().sizeHint()
        size.setWidth(min(240, self.fontMetrics().horizontalAdvance(self.caption) + 38))
        return size

    def resizeEvent(self, event):
        super().resizeEvent(event)
        text = self.fontMetrics().elidedText(self.caption, Qt.TextElideMode.ElideRight, max(20, self.width() - 35))
        self.setText(text.replace("&", "&&") + "  ×")


class GridScrollPanel(QScrollArea):
    visibilityChanged = Signal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.content = QWidget()
        self.grid = QGridLayout(self.content)
        self.setWidget(self.content)
    def layout(self): return self.grid
    def showEvent(self, event):
        super().showEvent(event); self.visibilityChanged.emit(True)
    def hideEvent(self, event):
        super().hideEvent(event); self.visibilityChanged.emit(False)


class ResponsivePanel(QWidget):
    resized = Signal()
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()


class StatePanel(QFrame):
    actionRequested = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statePanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.addStretch()
        self.title = QLabel()
        self.title.setObjectName("stateTitle"); self.title.setWordWrap(True)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        self.description = QLabel()
        self.description.setObjectName("muted"); self.description.setWordWrap(True)
        self.description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.description)
        self.button = QPushButton()
        self.button.setObjectName("secondary")
        self.button.clicked.connect(self.actionRequested)
        layout.addWidget(self.button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
    def set_state(self, title, description, action=""):
        self.title.setText(title); self.description.setText(description)
        self.title.setTextFormat(Qt.TextFormat.PlainText); self.description.setTextFormat(Qt.TextFormat.PlainText)
        self.description.show(); self.button.setText(action); self.button.setVisible(bool(action))


class LibraryLink(QPushButton):
    def __init__(self, title, caption, icon_name, parent=None):
        super().__init__(title, parent)
        self.caption, self.icon_name = caption, icon_name
        self.setAccessibleName(title + ". " + caption)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    def sizeHint(self): return QSize(260, max(88, round(QApplication.font().pointSizeF() * 5 + 42)))
    def paintEvent(self, event):
        theme = current_theme()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(theme["selection"] if self.underMouse() or self.isDown() else theme["surface"]))
        painter.setPen(QPen(QColor(theme["accent"] if self.hasFocus() else theme["border"]), 2 if self.hasFocus() else 1))
        card = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(card, 10, 10)
        local_icon(self.icon_name, theme["accent"], 22).paint(painter, 14, round(card.center().y()) - 11, 22, 22)
        font = QFont(QApplication.font()); font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font); painter.setPen(QColor(theme["text"]))
        metrics = QFontMetricsF(font)
        x, y = 49, 14
        for line in wrapped_lines(self.text(), font, self.width() - 68, 2):
            painter.drawText(QPointF(x, y + metrics.ascent()), line); y += metrics.lineSpacing()
        font.setWeight(QFont.Weight.Normal); font.setPointSizeF(max(8, font.pointSizeF() - 1))
        painter.setFont(font); painter.setPen(QColor(theme["muted"]))
        painter.drawText(QPointF(x, self.height() - 15), QFontMetricsF(font).elidedText(self.caption, Qt.TextElideMode.ElideRight, self.width() - 68))
        painter.end()
