
import logging
import os

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import mc.gui.safe_delete_dialog
# import mc.gui.toggle_switch_widget
from mc import model, mc_global


class RestActionsComposite(QtWidgets.QWidget):
    update_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.updating_gui_bool = False

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # Rest actions
        self.list_widget = QtWidgets.QListWidget()
        vbox.addWidget(self.list_widget)

        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        self.rest_add_action_qle = QtWidgets.QLineEdit()
        hbox.addWidget(self.rest_add_action_qle)
        self.rest_add_action_qpb = QtWidgets.QPushButton("Add")
        hbox.addWidget(self.rest_add_action_qpb)
        self.rest_add_action_qpb.clicked.connect(self.add_rest_action_clicked)

        # Details

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)

        self.edit_texts_qpb = QtWidgets.QPushButton()
        hbox.addWidget(self.edit_texts_qpb)
        self.edit_texts_qpb.setIcon(QtGui.QIcon(mc_global.get_icon_path("pencil-2x.png")))
        self.edit_texts_qpb.clicked.connect(self.on_edit_texts_clicked)

        self.move_to_top_qpb = QtWidgets.QPushButton()
        hbox.addWidget(self.move_to_top_qpb)
        self.move_to_top_qpb.setIcon(QtGui.QIcon(mc_global.get_icon_path("data-transfer-upload-2x.png")))
        self.move_to_top_qpb.clicked.connect(self.on_move_to_top_clicked)
        self.move_up_qpb = QtWidgets.QPushButton()
        hbox.addWidget(self.move_up_qpb)
        self.move_up_qpb.setIcon(QtGui.QIcon(mc_global.get_icon_path("arrow-top-2x.png")))
        self.move_up_qpb.clicked.connect(self.on_move_up_clicked)
        self.move_down_qpb = QtWidgets.QPushButton()
        hbox.addWidget(self.move_down_qpb)
        self.move_down_qpb.setIcon(QtGui.QIcon(mc_global.get_icon_path("arrow-bottom-2x.png")))
        self.move_down_qpb.clicked.connect(self.on_move_down_clicked)
        hbox.addStretch(1)
        self.delete_qpb = QtWidgets.QPushButton()
        hbox.addWidget(self.delete_qpb)
        self.delete_qpb.setIcon(QtGui.QIcon(mc_global.get_icon_path("trash-2x.png")))
        self.delete_qpb.clicked.connect(self.on_delete_clicked)

        self.update_gui()

    def on_edit_texts_clicked(self):
        edit_dialog_result_tuple = EditDialog.get_edit_dialog()
        if edit_dialog_result_tuple[0]:
            assert mc_global.active_rest_action_id_it != mc_global.NO_REST_ACTION_SELECTED_INT
            model.RestActionsM.update_title(
                mc_global.active_rest_action_id_it,
                self.breath_title_qle.text()
            )
            model.RestActionsM.update(
                mc_global.active_rest_action_id_it,
                self.in_breath_phrase_qle.text()
            )
            # TODO: self.phrases_updated_signal.emit(self.details_qgb.isEnabled())
        else:
            pass
        """
        text_str = QtWidgets.QInputDialog.getText(
            self,
            "title",
            "label"
        )
        """

    def on_move_up_clicked(self):
        self.move_up_down(model.MoveDirectionEnum.up)

    def on_move_down_clicked(self):
        self.move_up_down(model.MoveDirectionEnum.down)

    def move_up_down(self, i_up_down: model.MoveDirectionEnum):
        id_int = mc_global.active_rest_action_id_it
        model.RestActionsM.update_sort_order_move_up_down(id_int, i_up_down)
        self.update_gui()
        self.update_selected()

    def on_move_to_top_clicked(self):
        id_int = mc_global.active_rest_action_id_it
        while True:
            result_bool = model.RestActionsM.update_sort_order_move_up_down(
                id_int,
                model.MoveDirectionEnum.up
            )
            if not result_bool:
                break
        self.update_gui()
        self.update_selected()

    def update_selected(self):
        for i in range(0, self.list_widget.count()):
            item = self.list_widget.item(i)
            rest_qll = self.list_widget.itemWidget(item)
            logging.debug("custom_qll.question_entry_id = " + str(rest_qll.question_entry_id))
            if rest_qll.question_entry_id == mc_global.active_rest_action_id_it:
                item.setSelected(True)
                return

    def add_rest_action_clicked(self):
        if not(self.rest_add_action_qle.text().strip()):
            return
        model.RestActionsM.add(
            self.rest_add_action_qle.text().strip(),
            ""
        )
        self.update_gui()
        self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def on_delete_clicked(self):
        # active_phrase = model.PhrasesM.get(mc_global.active_phrase_id_it)
        conf_result_bool = mc.gui.safe_delete_dialog.SafeDeleteDialog.get_safe_confirmation_dialog(
            "Are you sure that you want to remove this entry?"
        )
        if conf_result_bool:
            self.list_widget.clearSelection()
            model.RestActionsM.remove(mc_global.active_rest_action_id_it)
            mc_global.active_rest_action_id_it = mc_global.NO_REST_ACTION_SELECTED_INT
            self.update_gui()
        else:
            pass

    def on_selection_changed(self):
        if self.updating_gui_bool:
            return
        selected_modelindexlist = self.list_widget.selectedIndexes()
        # current_row_int = self.rest_actions_qlw.currentRow()
        if len(selected_modelindexlist) >= 1:
            selected_row_int = selected_modelindexlist[0].row()
            # self.details_qgb.setDisabled(False)
            current_rest_action_qli = self.list_widget.item(selected_row_int)
            customqlabel_widget = self.list_widget.itemWidget(current_rest_action_qli)
            mc_global.active_rest_action_id_it = customqlabel_widget.question_entry_id
        else:
            self.details_qgb.setDisabled(True)
            #### mc_global.act= mc_global.NO_PHRASE_SELECTED_INT

        # self.update_gui_details()
        #### self.row_changed_signal.emit()

        self.update_signal.emit()

    def update_gui(self):
        self.updating_gui_bool = True

        self.list_widget.clear()
        for rest_action in model.RestActionsM.get_all():
            rest_action_title_cll = RestQLabel(rest_action.title_str, rest_action.id_int)
            list_item = QtWidgets.QListWidgetItem()
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, rest_action_title_cll)

        # self.update_gui_details()

        self.updating_gui_bool = False


class RestQLabel(QtWidgets.QLabel):
    question_entry_id = mc_global.NO_PHRASE_SELECTED_INT  # -"static"
    #mouse_pressed_signal = QtCore.pyqtSignal(QtGui.QMouseEvent, int)

    def __init__(self, i_text: str, i_diary_entry_id: int=mc_global.NO_PHRASE_SELECTED_INT):
        super().__init__(i_text)
        self.question_entry_id = i_diary_entry_id


class EditDialog(QtWidgets.QDialog):
    """
    Inspiration: Answer by lou here:
    https://stackoverflow.com/questions/18196799/how-can-i-show-a-pyqt-modal-dialog-and-get-data-out-of-its-controls-once-its-clo
    """
    def __init__(self, i_parent = None):
        super(EditDialog, self).__init__(i_parent)

        assert mc_global.active_rest_action_id_it != mc_global.NO_REST_ACTION_SELECTED_INT
        active_rest_action = model.RestActionsM.get(mc_global.active_rest_action_id_it)

        vbox = QtWidgets.QVBoxLayout(self)

        self.rest_action_title_qle = QtWidgets.QLineEdit(active_rest_action.title_str)
        vbox.addWidget(QtWidgets.QLabel("Title"))
        vbox.addWidget(self.rest_action_title_qle)

        image_hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(image_hbox)
        self.select_image_qpb = QtWidgets.QPushButton()  # "Select image"
        image_hbox.addWidget(self.select_image_qpb)
        self.select_image_qpb.setIcon(QtGui.QIcon(mc_global.get_icon_path("image-2x.png")))
        self.select_image_qpb.clicked.connect(self.on_select_image_clicked)
        self.details_image_path_qll = QtWidgets.QLabel()
        image_hbox.addWidget(self.details_image_path_qll)
        self.details_image_path_qll.setWordWrap(True)
        image_hbox.addStretch(1)

        self.update_gui_details()

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            self
        )
        vbox.addWidget(self.button_box)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        # -accept and reject are "slots" built into Qt

    def update_gui_details(self):
        if mc_global.active_rest_action_id_it != mc_global.NO_REST_ACTION_SELECTED_INT:
            rest_action = model.RestActionsM.get(mc_global.active_rest_action_id_it)
            # self.details_name_qle.setText(rest_action.title_str)
            if rest_action.image_path_str:
                if os.path.isfile(rest_action.image_path_str):
                    self.details_image_path_qll.setText(os.path.basename(rest_action.image_path_str))
                else:
                    self.details_image_path_qll.setText("image does not exist")
            else:
                self.details_image_path_qll.setText("(no image set)")

    @staticmethod
    def get_edit_dialog():
        dialog = EditDialog()
        dialog_result = dialog.exec_()

        confirmation_result_bool = False
        if dialog_result == QtWidgets.QDialog.Accepted:
            confirmation_result_bool = True
        edit_tuple = (
            dialog.breath_title_qle.text(),
            dialog.in_breath_phrase_qle.text(),
            dialog.out_breath_phrase_qle.text()
        )

        ret_tuple = (confirmation_result_bool, edit_tuple)
        return ret_tuple

    def on_select_image_clicked(self):
        image_file_result_tuple = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Please choose an image",
            mc_global.get_user_images_path(),
            "Image files (*.png *.jpg *.bmp)"
        )
        image_file_path_str = image_file_result_tuple[0]
        logging.debug("image_file_path_str = " + image_file_path_str)
        if image_file_path_str:
            model.RestActionsM.update_rest_action_image_path(
                mc_global.active_rest_action_id_it,
                image_file_path_str
            )
            self.update_gui_details()
        else:
            pass


