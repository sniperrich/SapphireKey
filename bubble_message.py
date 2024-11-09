# from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, pyqtSignal, Qt, QThread
from PyQt5.QtGui import QPainter, QFont, QColor, QPixmap, QPolygon, QFontMetrics
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QVBoxLayout, QSpacerItem, \
    QScrollArea, QScrollBar, QLineEdit, QPushButton
from enum import Enum



class MessageType(Enum):
    Text = 1
    Image = 2


class TextMessage(QLabel):
    heightSingal = pyqtSignal(int)

    def __init__(self, text, is_send=False, parent=None):
        super(TextMessage, self).__init__(text, parent)
        font = QFont('微软雅黑', 12)
        self.setFont(font)
        self.setWordWrap(True)
        self.setMaximumWidth(800)
        self.setMinimumWidth(200)
        self.setMinimumHeight(45)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        if is_send:
            self.setAlignment(Qt.AlignCenter | Qt.AlignRight)
            self.setStyleSheet(
                '''
                background-color:#b2e281;
                border-radius:10px;
                padding:10px;
                '''
            )
        else:
            self.setStyleSheet(
                '''
                background-color:white;
                border-radius:10px;
                padding:10px;
                '''
            )
        font_metrics = QFontMetrics(font)
        rect = font_metrics.boundingRect(text)
        self.setMaximumWidth(rect.width()+30)


    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(TextMessage, self).paintEvent(a0)


class Triangle(QLabel):
    def __init__(self, Type, is_send=False, parent=None):
        super().__init__(parent)
        self.Type = Type
        self.is_send = is_send
        self.setFixedSize(6, 45)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(Triangle, self).paintEvent(a0)
        if self.Type == MessageType.Text:
            painter = QPainter(self)
            triangle = QPolygon()
            if self.is_send:
                painter.setPen(QColor('#b2e281'))
                painter.setBrush(QColor('#b2e281'))
                triangle.setPoints(0, 20, 0, 34, 6, 27)
            else:
                painter.setPen(QColor('white'))
                painter.setBrush(QColor('white'))
                triangle.setPoints(0, 27, 6, 20, 6, 34)
            painter.drawPolygon(triangle)


class Notice(QLabel):
    def __init__(self, text, type_=3, parent=None):
        super().__init__(text, parent)
        self.type_ = type_
        self.setFont(QFont('微软雅黑', 12))
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setAlignment(Qt.AlignCenter)


class Avatar(QLabel):
    def __init__(self, avatar, parent=None):
        super().__init__(parent)
        if isinstance(avatar, str):
            self.setPixmap(QPixmap(avatar).scaled(45, 45))
            self.image_path = avatar
        elif isinstance(avatar, QPixmap):
            self.setPixmap(avatar.scaled(45, 45))
        self.setFixedSize(QSize(45, 45))


class OpenImageThread(QThread):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self) -> None:
        image = Image.open(self.image_path)
        image.show()


class ImageMessage(QLabel):
    def __init__(self, avatar, parent=None):
        super().__init__(parent)
        self.image = QLabel(self)
        if isinstance(avatar, str):
            self.setPixmap(QPixmap(avatar))
            self.image_path = avatar
        elif isinstance(avatar, QPixmap):
            self.setPixmap(avatar)
        self.setMaximumWidth(480)
        self.setMaximumHeight(720)
        self.setScaledContents(True)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:  # 左键按下
            self.open_image_thread = OpenImageThread(self.image_path)
            self.open_image_thread.start()


class BubbleMessage(QWidget):
    def __init__(self, content, avatar_path, message_type=MessageType.Text, is_send=True, timestamp=None):
        super().__init__()
        self.content = content
        self.avatar_path = avatar_path
        self.message_type = message_type
        self.is_send = is_send
        self.timestamp = timestamp
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 头像
        avatar_label = QLabel()
        pixmap = QPixmap(self.avatar_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        avatar_label.setPixmap(pixmap)
        avatar_label.setFixedSize(40, 40)
        
        # 消息内容
        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("""
            QLabel {
                background-color: #95EC69;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                max-width: 400px;
            }
        """)
        
        if self.is_send:
            layout.addStretch()
            layout.addWidget(content_label)
            layout.addWidget(avatar_label)
        else:
            layout.addWidget(avatar_label)
            layout.addWidget(content_label)
            layout.addStretch()
            
        self.setLayout(layout)


class ScrollAreaContent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.adjustSize()


class ScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(
            '''
            border:none;
            '''
        )


class ScrollBar(QScrollBar):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            '''
          QScrollBar:vertical {
              border-width: 0px;
              border: none;
              background:rgba(64, 65, 79, 0);
              width:5px;
              margin: 0px 0px 0px 0px;
          }
          QScrollBar::handle:vertical {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
              stop: 0 #DDDDDD, stop: 0.5 #DDDDDD, stop:1 #aaaaff);
              min-height: 20px;
              max-height: 20px;
              margin: 0 0px 0 0px;
              border-radius: 2px;
          }
          QScrollBar::add-line:vertical {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
              stop: 0 rgba(64, 65, 79, 0), stop: 0.5 rgba(64, 65, 79, 0),  stop:1 rgba(64, 65, 79, 0));
              height: 0px;
              border: none;
              subcontrol-position: bottom;
              subcontrol-origin: margin;
          }
          QScrollBar::sub-line:vertical {
              background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
              stop: 0  rgba(64, 65, 79, 0), stop: 0.5 rgba(64, 65, 79, 0),  stop:1 rgba(64, 65, 79, 0));
              height: 0 px;
              border: none;
              subcontrol-position: top;
              subcontrol-origin: margin;
          }
          QScrollBar::sub-page:vertical {
              background: rgba(64, 65, 79, 0);
          }

          QScrollBar::add-page:vertical {
              background: rgba(64, 65, 79, 0);
          }
            '''
        )


class ChatWidget(QWidget):
    # 添加消息发送信号
    message_sent = pyqtSignal(str)  # 发送消息内容
    
    def __init__(self):
        super().__init__()
        self.resize(500, 200)

        # 创建主布
        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.adjustSize()

        # 创建消息显示区域
        self.scrollArea = ScrollArea(self)
        scrollBar = ScrollBar()
        self.scrollArea.setVerticalScrollBar(scrollBar)
        self.scrollAreaWidgetContents = ScrollAreaContent(self.scrollArea)
        self.scrollAreaWidgetContents.setMinimumSize(50, 100)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
        # 消息列表布局
        self.layout0 = QVBoxLayout()
        self.layout0.setSpacing(0)
        self.scrollAreaWidgetContents.setLayout(self.layout0)
        
        # 添加消息显示区域到主布局
        layout.addWidget(self.scrollArea)
        
        # 创建输入区域
        input_widget = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 5, 10, 5)
        
        # 创建消息输入框
        self.message_input = QLineEdit()
        self.message_input.setStyleSheet('''
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
                min-height: 30px;
            }
        ''')
        self.message_input.returnPressed.connect(self.send_message)
        
        # 创建发送按钮
        self.send_button = QPushButton('发送')
        self.send_button.setStyleSheet('''
            QPushButton {
                background-color: #1aad19;
                border: none;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-size: 14px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #129611;
            }
            QPushButton:pressed {
                background-color: #108010;
            }
        ''')
        self.send_button.clicked.connect(self.send_message)
        
        # 添加组件到输入区域布局
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_widget.setLayout(input_layout)
        
        # 添加输入区域到主布局
        layout.addWidget(input_widget)
        
        self.setLayout(layout)

    def send_message(self):
        """发送消息"""
        content = self.message_input.text().strip()
        if content:
            # 发送消息信号
            self.message_sent.emit(content)
            
            # 创建并添加消息气泡
            bubble = BubbleMessage(
                content, 
                'bubble_message/data/head1.jpg',  # 这里需要替换为实际的头像路径
                MessageType.Text, 
                True
            )
            self.add_message_item(bubble)
            
            # 清空输入框
            self.message_input.clear()
            
            # 滚动到底部
            self.set_scroll_bar_last()

    def add_message_item(self, bubble_message, index=1):
        if index:
            self.layout0.addWidget(bubble_message)
        else:
            self.layout0.insertWidget(0, bubble_message)
        # self.set_scroll_bar_last()

    def set_scroll_bar_last(self):
        """滚动到最后一条消息"""
        try:
            scrollbar = self.scrollArea.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            print(f"滚动到底部失败: {e}")

    def set_scroll_bar_value(self, val):
        self.verticalScrollBar().setValue(val)

    def verticalScrollBar(self):
        return self.scrollArea.verticalScrollBar()

    def update(self) -> None:
        super().update()
        self.scrollAreaWidgetContents.adjustSize()
        self.scrollArea.update()
        # self.scrollArea.repaint()
        # self.verticalScrollBar().setMaximum(self.scrollAreaWidgetContents.height())


    def clear_messages(self):
        """清空所有消息"""
        try:
            # 清空布局中的所有消息
            while self.layout0.count():
                item = self.layout0.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        except Exception as e:
            print(f"清空消息失败: {e}")

    def load_chat_history(self, friend_nickname, messages, send_avatar, receive_avatar):
        """加载聊天记录"""
        try:
            self.clear_messages()
            
            current_date = None
            for message in messages:
                # 添加日期分割线
                message_date = message["timestamp"].split()[0]
                if current_date != message_date:
                    current_date = message_date
                    time_notice = Notice(message["timestamp"])
                    self.add_message_item(time_notice)
                
                # 添加消息气泡
                avatar = send_avatar if message["is_send"] else receive_avatar
                msg_type = MessageType.Text if message["type"] == "text" else MessageType.Image
                bubble = BubbleMessage(message["content"], avatar, msg_type, message["is_send"])
                self.add_message_item(bubble)
                
            # 滚动到底部
            self.set_scroll_bar_last()
        except Exception as e:
            print(f"加载聊天记录失败: {e}")
            raise

    def add_message(self, content, is_send, avatar_path, message_type='text', timestamp=None):
        """添加一条消息"""
        try:
            # 如果有时间戳且与上一条消息不是同一天，添加日期分割线
            if timestamp:
                message_date = timestamp.split()[0]
                if not hasattr(self, 'last_message_date') or self.last_message_date != message_date:
                    self.last_message_date = message_date
                    time_notice = Notice(timestamp)
                    self.add_message_item(time_notice)
            
            # 添加消息气泡
            bubble = BubbleMessage(
                content,
                avatar_path,
                MessageType.Text if message_type == 'text' else MessageType.Image,
                is_send,
                timestamp
            )
            self.add_message_item(bubble)
            
            # 滚动到底部
            self.set_scroll_bar_last()
        except Exception as e:
            print(f"添加消息失败: {e}")
