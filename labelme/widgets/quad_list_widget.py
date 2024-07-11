from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy.QtCore import Qt


class QuadListWidgetItem(QtGui.QStandardItem):
    def __init__(self, text=None, quad=None):
        super(QuadListWidgetItem, self).__init__()
        self.setText(text or "")
        self.setQuad(quad)

        self.setEditable(False)
        self.setTextAlignment(Qt.AlignBottom)

    def clone(self):
        return QuadListWidgetItem(self.text(), self.quad())

    def setQuad(self, quad):
        self.setData(quad, Qt.UserRole)

    def quad(self):
        return self.data(Qt.UserRole)
    
    def __hash__(self):
        return id(self)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.text())


class StandardItemModel(QtGui.QStandardItemModel):
    itemDropped = QtCore.Signal()

    def removeRows(self, *args, **kwargs):
        ret = super().removeRows(*args, **kwargs)
        self.itemDropped.emit()
        return ret


class QuadListWidget(QtWidgets.QListView):
    itemDoubleClicked = QtCore.Signal(QuadListWidgetItem)
    itemSelectionChanged = QtCore.Signal(list, list)

    def __init__(self):
        super(QuadListWidget, self).__init__()
        self._selectedItems = []

        self.setWindowFlags(Qt.Window)
        self.setModel(StandardItemModel())
        self.model().setItemPrototype(QuadListWidgetItem())
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)

        self.doubleClicked.connect(self.itemDoubleClickedEvent)
        self.selectionModel().selectionChanged.connect(self.itemSelectionChangedEvent)

    def __len__(self):
        return self.model().rowCount()

    def __getitem__(self, i):
        return self.model().item(i)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    @property
    def itemDropped(self):
        return self.model().itemDropped

    @property
    def itemChanged(self):
        return self.model().itemChanged

    def itemSelectionChangedEvent(self, selected, deselected):
        selected = [self.model().itemFromIndex(i) for i in selected.indexes()]
        deselected = [self.model().itemFromIndex(i) for i in deselected.indexes()]
        self.itemSelectionChanged.emit(selected, deselected)

    def itemDoubleClickedEvent(self, index):
        self.itemDoubleClicked.emit(self.model().itemFromIndex(index))

    def selectedItems(self):
        return [self.model().itemFromIndex(i) for i in self.selectedIndexes()]

    def scrollToItem(self, item):
        self.scrollTo(self.model().indexFromItem(item))

    def addItem(self, item):
        if not isinstance(item, QuadListWidgetItem):
            raise TypeError("item must be QuadListWidgetItem")
        self.model().setItem(self.model().rowCount(), 0, item)
        item.setSizeHint(self.itemDelegate().sizeHint(None, None))

    def removeItem(self, item):
        index = self.model().indexFromItem(item)
        self.model().removeRows(index.row(), 1)

    def selectItem(self, item):
        index = self.model().indexFromItem(item)
        self.selectionModel().select(index, QtCore.QItemSelectionModel.Select)

    def findItemByShape(self, quad):
        for row in range(self.model().rowCount()):
            item = self.model().item(row, 0)
            if item.quad() == quad:
                return item
        raise ValueError("cannot find quad: {}".format(quad))

    def clear(self):
        self.model().clear()
