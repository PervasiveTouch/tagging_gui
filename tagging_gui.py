import sys
import datetime
import pandas as pd
import json

from PyQt6.QtCore import QSize, Qt, QSize, QMargins
from PyQt6.QtGui import QImage, QPalette, QPixmap,QStandardItem, QStandardItemModel, QFont
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QScrollArea, QLabel, QLineEdit, QListWidget, QListWidgetItem, QAbstractItemView, QProgressBar, QPlainTextEdit, QTabWidget, QListView, QStyle

start_index = 0
annotator = 'N.N.'

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
WINDOW_TITLE = 'Tagger 3000 🚀🚀'

FONT_SIZE = 12

WIDTH_IMAGE_VIEW = WINDOW_WIDTH // 4
WIDTH_COLUMN_TEXT = WINDOW_WIDTH // 4
WIDTH_COLUMN_TAGS = WINDOW_WIDTH // 2
HEIGHT_LIST_TAGS = int(WINDOW_HEIGHT * 0.7)

TEXT_LABEL_POSITIVE = 'Positiv'
TEXT_LABEL_NEGATIVE = 'Negativ'
TEXT_LABEL_OTHER = 'Anderes Feedback'
TEXT_BUTTON_SUBMIT = 'Speichern'
TEXT_DEVICE_TYPE = 'Gerätetyp'
TEXT_ADDITIONAL_REMARKS = 'Zusätzliche Anmerkungen'
TEXT_SHOW_IMAGE = 'Bild anzeigen'
TEXT_HIDE_IMAGE = 'Bild ausblenden'
TEXT_SEARCH_BAR_HINT = 'Tags filtern...'
TEXT_ACQUISITION = 'Anschaffung'
TEXT_FUNCTIONALITY = 'Funktionalität und Design'
TEXT_USABILITY = 'Bedienbarkeit und UX'
TEXT_ASSIGNED = 'Zugewiesen'
TEXT_CLEAR_SEARCH_BAR = 'Zurücksetzen'
TEXT_DESCRIPTION = 'Tag-Beschreibung'
TEXT_REMOVE = 'Entfernen'

# icon list: https://www.pythonguis.com/faq/built-in-qicons-pyqt/
# ICON_REMOVE = 'SP_TitleBarCloseButton'
# ICON_REMOVE = 'SP_MessageBoxCritical'
ICON_REMOVE = 'SP_DialogCancelButton'
#ICON_REMOVE = 'SP_DialogCloseButton'
#ICON_REMOVE = 'SP_DialogDiscardButton'

STYLE_BOLD = 'font-weight: bold'

ASSIGNED_LIST_MARGINS = QMargins(0, 0, 0, 0)

#PATH_TAG_DICT = 'mapping_2025-05-28.json'
PATH_TAG_DICT = 'tag_descriptions.json'
PATH_DEVICE_DATA = 'full_devices_data.csv'
PATH_IMAGE_BASE = '../all_images'

def read_tags():
    tag_dict = {}
    with open(PATH_TAG_DICT, 'r', encoding='utf-8') as f:
        file_text = f.read()
        #file_text = f.read().replace('"', '\\"').replace('\'', '"')
        #print(file_text)
        tag_dict = json.loads(file_text)
    return tag_dict

class DataModel():
    def __init__(self):
        self.index = 0
        self.total_device_count = 0

    def read_data(self, path):
        self.df = pd.read_csv(path)
        self.total_device_count = len(self.df.index)

    # for future researchers: change this to make it work with other data formats
    def get_device_by_index(self, index):
        row = self.df.iloc[index]
        result = {'img_path' : row.img_path, 'positive_text' : row.positive_arg, 'negative_text' : row.negative_arg, 'other_text' : row.other_arg, 'device_type' : row.device_type}
        return result

    def get_next_device(self):
        result = self.get_device_by_index(self.index)
        self.index += 1
        return result

    def set_index(self, index : int):
        self.index = index

class QListWidgetItemRemovable(QWidget):
    all_tags = []

    def __init__ (self, parent=None, text='', deselect=None):
        super(QListWidgetItemRemovable, self).__init__()
        self.parent = parent
        self.tag = text
        self.layout = QHBoxLayout()
        self.label = QLabel(text)
        self.button = QPushButton() #TEXT_REMOVE

        icon_pixmap = getattr(QStyle.StandardPixmap, ICON_REMOVE)
        icon = self.style().standardIcon(icon_pixmap)
        self.button.setIcon(icon)
        self.button.setFlat(True)

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)
        self.layout.addStretch()
        self.layout.setContentsMargins(ASSIGNED_LIST_MARGINS)
        self.setLayout(self.layout)
        self.button.clicked.connect(self.on_remove_clicked)
        self.deselect = deselect
        QListWidgetItemRemovable.all_tags.append(self.tag)

    def setText(self, text):
        self.label.setText(text)

    def on_remove_clicked(self):
        self.remove()

    def remove(self):
        self.deselect(self.tag)
        QListWidgetItemRemovable.all_tags.remove(self.tag)
        self.parent.removeWidget(self)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(WINDOW_TITLE)

        #self.setFixedSize(QSize(WINDOW_WIDTH, WINDOW_HEIGHT))

        self.img_path = ''

        self.layout_global = QVBoxLayout()
        self.layout_gui = QHBoxLayout()
        self.layout_buttons = QHBoxLayout()
        self.layout_image = QVBoxLayout()
        self.layout_text = QVBoxLayout()
        self.layout_text_positive = QVBoxLayout()
        self.layout_text_negative = QVBoxLayout()
        self.layout_text_other = QVBoxLayout()
        self.layout_tag_tabs = QTabWidget()
        self.layout_tag_lists = QHBoxLayout()
        self.layout_tag_bottom = QHBoxLayout()
        self.layout_additional_remarks = QVBoxLayout()
        self.layout_search_bar = QHBoxLayout()
        self.layout_text_description = QVBoxLayout()
        self.groupbox_text_description = QGroupBox(TEXT_DESCRIPTION)
        self.label_text_description = QLabel()
        self.groupbox_text_positive = QGroupBox(TEXT_LABEL_POSITIVE)
        self.groupbox_text_negative = QGroupBox(TEXT_LABEL_NEGATIVE)
        self.groupbox_text_other = QGroupBox(TEXT_LABEL_OTHER)
        self.layout_tag_menu = QVBoxLayout()
        self.button_submit = QPushButton(TEXT_BUTTON_SUBMIT)
        self.label_annotator = QLabel()
        self.label_device_count = QLabel()
        self.progress_bar_device_count = QProgressBar()
        self.button_toggle_image = QPushButton(TEXT_SHOW_IMAGE)
        self.label_list_acquisition = QLabel(TEXT_ACQUISITION)
        self.label_list_functionality = QLabel(TEXT_FUNCTIONALITY)
        self.label_list_usability = QLabel(TEXT_USABILITY)
        self.label_list_assigned = QLabel(TEXT_ASSIGNED)
        self.button_clear_search_bar = QPushButton(TEXT_CLEAR_SEARCH_BAR)

        self.button_toggle_image.setMinimumWidth(WIDTH_IMAGE_VIEW)
        self.button_toggle_image.setMaximumWidth(WIDTH_IMAGE_VIEW)

        self.groupbox_text_positive.setMinimumWidth(WIDTH_COLUMN_TEXT)
        self.groupbox_text_negative.setMinimumWidth(WIDTH_COLUMN_TEXT)
        self.groupbox_text_other.setMinimumWidth(WIDTH_COLUMN_TEXT)

        self.groupbox_text_positive.setMaximumWidth(WIDTH_COLUMN_TEXT)
        self.groupbox_text_negative.setMaximumWidth(WIDTH_COLUMN_TEXT)
        self.groupbox_text_other.setMaximumWidth(WIDTH_COLUMN_TEXT)

        self.scroll_assigned_tags = QScrollArea()
        self.scroll_assigned_tags.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_assigned_tags.setWidgetResizable(True)

        self.groupbox_list_assigned = QGroupBox(TEXT_ASSIGNED)

        self.model_list_assigned = QStandardItemModel()

        #self.container_tag_list_acquisition = QWidget()
        #self.container_tag_list_functionality = QWidget()
        #self.container_tag_list_usability = QWidget()

        self.layout_tag_list_acquisition = QVBoxLayout()
        self.layout_tag_list_functionality = QVBoxLayout()
        self.layout_tag_list_usability = QVBoxLayout()
        self.layout_tag_list_assigned = QVBoxLayout()


        self.image_visible = False

        self.label_device_type = QLabel()
        self.label_device_type.setStyleSheet(STYLE_BOLD)

        self.label_additional_remarks = QLabel(TEXT_ADDITIONAL_REMARKS)
        self.textedit_additional_remarks = QPlainTextEdit()

        self.area_image = QScrollArea()
        self.image = QImage()
        self.label_image = QLabel()
        self.label_image.setVisible(False)

        self.label_text_positive = QLabel()
        self.label_text_negative = QLabel()
        self.label_text_other = QLabel()

        self.label_text_positive.setWordWrap(True)
        self.label_text_negative.setWordWrap(True)
        self.label_text_other.setWordWrap(True)

        self.textedit_filter_tags = QLineEdit()
        self.textedit_filter_tags.setPlaceholderText(TEXT_SEARCH_BAR_HINT)
        self.list_tags = QListWidget()

        self.list_tags_acquisition = QListWidget()
        self.list_tags_functonality = QListWidget()
        self.list_tags_usability = QListWidget()
        self.tag_lists = [self.list_tags_acquisition, self.list_tags_functonality, self.list_tags_usability]
        self.map_category_list = {'acquisition' : self.list_tags_acquisition,
                                  'reason' : self.list_tags_acquisition,
                                  'functionality' : self.list_tags_functonality,
                                  'design' : self.list_tags_functonality,
                                  'usability' : self.list_tags_usability,
                                  'UX' : self.list_tags_usability}

        self.list_tags_usability.setMinimumHeight(HEIGHT_LIST_TAGS)

        #self.list_tags_assigned = QListWidget()
        self.list_tags_assigned = QVBoxLayout()
        self.list_tags_assigned.setAlignment(Qt.AlignmentFlag.AlignTop)
        #self.list_tags_assigned.setModel(self.model_list_assigned)

        # image widget
        self.layout_image.addWidget(self.label_device_type)
        self.layout_image.addWidget(self.button_toggle_image)
        #self.area_image.setBackgroundRole(QPalette.dark())
        #self.label_image.setScaledContents(True)
        self.layout_image.addWidget(self.label_image)
        self.layout_image.addStretch()

        ## old: use scroll area
        #self.area_image.setWidget(self.label_image)
        #self.layout_image.addWidget(self.area_image)

        # text widgets
        ## text labels
        #self.groupbox_text_positive.addWidget(QLabel(TEXT_LABEL_POSITIVE).setStyleSheet(STYLE_HEADER_TEXT))
        #self.groupbox_text_negative.addWidget(QLabel(TEXT_LABEL_NEGATIVE).setStyleSheet(STYLE_HEADER_TEXT))
        #self.groupbox_text_other.addWidget(QLabel(TEXT_LABEL_OTHER).setStyleSheet(STYLE_HEADER_TEXT))
        self.layout_text_positive.addWidget(self.label_text_positive)
        self.layout_text_negative.addWidget(self.label_text_negative)
        self.layout_text_other.addWidget(self.label_text_other)

        self.layout_text.addWidget(self.groupbox_text_positive)
        self.layout_text.addWidget(self.groupbox_text_negative)
        self.layout_text.addWidget(self.groupbox_text_other)

        self.groupbox_text_positive.setLayout(self.layout_text_positive)
        self.groupbox_text_negative.setLayout(self.layout_text_negative)
        self.groupbox_text_other.setLayout(self.layout_text_other)

        # tag menu
        ## ExtendedSelection allows for Crtl + Click
        #self.list_tags.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_tags.setSortingEnabled(True)

        #self.list_tags_acquisition.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_tags_acquisition.setSortingEnabled(True)
        #self.list_tags_functonality.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_tags_functonality.setSortingEnabled(True)
        #self.list_tags_usability.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_tags_usability.setSortingEnabled(True)

        #self.layout_tag_menu.addWidget(self.layout_tag_tabs)

        #self.layout_tag_tabs.addTab(self.textedit_filter_tags)
        #self.layout_tag_tabs.addTab(self.list_tags)

        self.layout_tag_lists.addLayout(self.layout_tag_list_usability)
        self.layout_tag_lists.addLayout(self.layout_tag_list_functionality)
        self.layout_tag_lists.addLayout(self.layout_tag_list_acquisition)

        self.layout_tag_list_acquisition.addWidget(self.label_list_acquisition)
        self.layout_tag_list_functionality.addWidget(self.label_list_functionality)
        self.layout_tag_list_usability.addWidget(self.label_list_usability)

        self.layout_tag_list_acquisition.addWidget(self.list_tags_acquisition)
        self.layout_tag_list_functionality.addWidget(self.list_tags_functonality)
        self.layout_tag_list_usability.addWidget(self.list_tags_usability)

        self.layout_tag_menu.addLayout(self.layout_search_bar)
        self.layout_search_bar.addWidget(self.textedit_filter_tags)
        self.layout_search_bar.addWidget(self.button_clear_search_bar)


        self.layout_tag_menu.addLayout(self.layout_tag_lists)
        #self.layout_tag_menu.addWidget(self.list_tags)


        self.layout_tag_menu.addLayout(self.layout_tag_bottom)

        self.layout_tag_bottom.addLayout(self.layout_tag_list_assigned)
        self.layout_tag_bottom.addLayout(self.layout_additional_remarks)

        self.layout_tag_list_assigned.addWidget(self.scroll_assigned_tags)
        self.scroll_assigned_tags.setWidget(self.groupbox_list_assigned)

        self.groupbox_list_assigned.setLayout(self.list_tags_assigned)
        #self.layout_tag_list_assigned.addWidget(self.label_list_assigned)
        #self.layout_tag_list_assigned.addWidget(self.list_tags_assigned)
        #self.layout_tag_list_assigned.addLayout(self.list_tags_assigned)

        self.label_text_description.setWordWrap(True)
        self.layout_additional_remarks.addWidget(self.groupbox_text_description)
        self.groupbox_text_description.setLayout(self.layout_text_description)
        self.layout_text_description.addWidget(self.label_text_description)
        self.layout_additional_remarks.addWidget(self.label_additional_remarks)
        self.layout_additional_remarks.addWidget(self.textedit_additional_remarks)

        # buttons
        self.layout_buttons.addWidget(self.label_annotator)
        #self.layout_buttons.addWidget(self.label_device_count)
        self.layout_buttons.addWidget(self.progress_bar_device_count)
        self.layout_buttons.addWidget(self.button_submit)

        # build layout
        self.layout_gui.addLayout(self.layout_image)
        self.layout_gui.addLayout(self.layout_text)
        self.layout_gui.addLayout(self.layout_tag_menu)

        self.layout_global.addLayout(self.layout_gui)
        self.layout_global.addLayout(self.layout_buttons)

        self.button_clear_search_bar.clicked.connect(self.on_clear_search_bar_button_pressed)

        self.textedit_filter_tags.textChanged.connect(self.on_filter_text_changed)

        self.button_submit.clicked.connect(self.on_submit_button_pressed)

        self.button_toggle_image.clicked.connect(self.on_toggle_image_button_pressed)

        self.list_tags_acquisition.currentItemChanged.connect(self.on_list_item_selected)
        self.list_tags_functonality.currentItemChanged.connect(self.on_list_item_selected)
        self.list_tags_usability.currentItemChanged.connect(self.on_list_item_selected)

        self.list_tags_acquisition.itemDoubleClicked.connect(self.on_list_item_assigned)
        self.list_tags_functonality.itemDoubleClicked.connect(self.on_list_item_assigned)
        self.list_tags_usability.itemDoubleClicked.connect(self.on_list_item_assigned)

        widget = QWidget()
        widget.setLayout(self.layout_global)

        self.setCentralWidget(widget)

    def load_image(self):
        pass

    def load_tags(self, tags : dict):
        #self.list_tags.addItems(tags)
        for item in tags.items():
            list_item = QListWidgetItem(item[0])
            list_item.setToolTip(item[1])
            list_item.setStatusTip(item[1])
            category, code = item[0].split(':')
            for key, tag_list in self.map_category_list.items():
                if key == category:
                    tag_list.addItem(list_item)

    def update_tag_list(self, search_string : str):
        #for item in self.list_tags.items(): ## does not work because MIME type is required
        for tag_list in self.tag_lists:
            for i in range(tag_list.count()):
                item = tag_list.item(i)
                if search_string.lower() in str(item.text()).lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def get_selected_tags(self):
        items = [item.text for item in self.list_tags.selectedItems()]
        return items
    
    def load_image(self, path : str):
        return QPixmap(path)

    def update_image(self, path : str):
        #print(path)
        image = self.load_image(path)
        image = image.scaledToWidth(WIDTH_IMAGE_VIEW)
        #print(image.size())
        self.label_image.setPixmap(image)

    def on_filter_text_changed(self):
        text = self.textedit_filter_tags.text()
        self.update_tag_list(text)

    def set_model(self, model : DataModel):
        self.model = model
        self.load_next_device()

    # for future researchers: change this also for working with other stuff
    def load_next_device(self):
        self.start_time = datetime.datetime.now()
        data = self.model.get_next_device()
        self.label_text_positive.setText(str(data['positive_text']))
        self.label_text_negative.setText(str(data['negative_text']))
        self.label_text_other.setText(str(data['other_text']))
        self.img_path = data['img_path']
        self.update_image(f'{PATH_IMAGE_BASE}/{self.img_path}')
        #print(data)
        self.update_device_count()
        self.update_device_type(data['device_type'])

    def deselect_tag(self, tag):
        #print(tag)
        for tag_list in self.tag_lists:
            for i in range(tag_list.count()):
                item = tag_list.item(i)
                if item.text() == tag:
                    item.setSelected(False)

    def deselect_tags(self):
        for tag_list in self.tag_lists:
            for i in range(tag_list.count()):
                item = tag_list.item(i)
                item.setSelected(False)

    def on_clear_search_bar_button_pressed(self):
        self.clear_search()

    def clear_search(self):
        self.textedit_filter_tags.clear()

    def save_tags(self):
        self.end_time = datetime.datetime.now()
        with open(self.output_file_path, 'a') as f:
            #print('annotator,img_path,type,content')
            for tag in QListWidgetItemRemovable.all_tags:
                f.write(f'{self.annotator},{self.img_path},tag,{tag},{self.start_time},{self.end_time}\n')
            additional_remarks = self.textedit_additional_remarks.toPlainText().replace('"', '\"')
            additional_remarks = f'"{additional_remarks}"'
            if len(additional_remarks) > 2:
                f.write(f'{self.annotator},{self.img_path},additional_remarks,{additional_remarks},{self.start_time},{self.end_time}\n')
                #print(self.annotator, self.img_path, 'additional_remarks', additional_remarks)
            #print(self.img_path)
            #print(additional_remarks)
            #print(QListWidgetItemRemovable.all_tags)

    def on_submit_button_pressed(self):
        self.save_tags()
        self.clear_search()
        self.deselect_tags()
        self.clear_assigned_list()
        self.clear_additional_remarks()
        self.load_next_device()

    def set_annotator(self, annotator : str):
        self.annotator = annotator
        self.label_annotator.setText(f'Annotator: {annotator}')

    def update_device_count(self):
        self.progress_bar_device_count.setMinimum(0)
        self.progress_bar_device_count.setMaximum(self.model.total_device_count)
        self.progress_bar_device_count.setValue(self.model.index)
        self.progress_bar_device_count.setFormat(f'Device {self.model.index}/{self.model.total_device_count}')
        #self.label_device_count.setText(f'Device {self.model.index}/{self.model.total_device_count}')

    def update_device_type(self, device_type : str):
        self.label_device_type.setText(f'{TEXT_DEVICE_TYPE}: {device_type}')

    def on_toggle_image_button_pressed(self):
        if self.image_visible:
            self.button_toggle_image.setText(TEXT_SHOW_IMAGE)
            self.image_visible = False
            self.label_image.setVisible(False)
        else:
            self.button_toggle_image.setText(TEXT_HIDE_IMAGE)
            self.image_visible = True
            self.label_image.setVisible(True)

    def on_list_item_selected(self, item : QListWidgetItem, previous : QListWidgetItem):
        tag = item.text()
        category, code = tag.split(':')
        description = item.statusTip()
        description_text = f'{tag}\n{description}'
        self.label_text_description.setText(description_text)


    def on_list_item_assigned(self, item : QListWidgetItem):
        tag = item.text()
        category, code = tag.split(':')
        #self.list_tags_assigned.addItem(item)
        #self.list_tags_assigned.addItem(QListWidgetItem(tag))
        #self.list_tags_assigned.addItem(QLabel("test"))
        #self.list_tags_assigned.addItem(QListWidgetItemRemovable(parent=self.list_tags_assigned, text='test'))

        if tag not in QListWidgetItemRemovable.all_tags:
            self.list_tags_assigned.addWidget(QListWidgetItemRemovable(parent=self.list_tags_assigned, text=tag, deselect=self.deselect_tag))
        #print(item, tag)

        #list_item = QListWidgetItem(item[0])
        #list_item.setToolTip(item[1])
        #list_item.setStatusTip(item[1])

        #for key, tag_list in map_category_list.items():
        #    if tag == key:

    def set_output_file_path(self, output_file_path : str):
        self.output_file_path = output_file_path

    def clear_assigned_list(self):
        to_remove = []

        for i in range(self.list_tags_assigned.count()):
            to_remove.append(self.list_tags_assigned.itemAt(i).widget())

        for item in to_remove:
            item.remove()

        QListWidgetItemRemovable.all_tags = []

    def clear_additional_remarks(self):
        self.textedit_additional_remarks.clear()

if __name__ == '__main__':
    output_file_path = f'output_{datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.csv'
    if len(sys.argv) > 1:
        start_index = int(sys.argv[1])
    if len(sys.argv) > 2:
        annotator = sys.argv[2]
    if len(sys.argv) > 3:
        output_file_path = sys.argv[3]
    else:
        print(f'Warning: output file path not set. Using placeholder: {output_file_path}')


    model = DataModel()
    model.read_data(PATH_DEVICE_DATA)
    model.set_index(start_index)

    tags = read_tags()

    app = QApplication(sys.argv)
    global_font = app.font()
    global_font.setPointSize(FONT_SIZE);
    app.setFont(global_font, 'QWidget')

    window = MainWindow()

    window.set_annotator(annotator)
    window.set_output_file_path(output_file_path)
    window.load_tags(tags)
    window.set_model(model)

    window.show()

    app.exec()
