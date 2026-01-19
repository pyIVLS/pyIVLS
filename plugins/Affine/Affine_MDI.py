from typing import Optional
from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from PyQt6 import QtGui
from plugin_components import MANIPULATOR_COLORS

class GraphicsView(QGraphicsView):
    # signal for added points
    point_clicked = pyqtSignal(QPointF)
    drawn_points: list[QGraphicsItem] = []

    def __init__(self, scene: QGraphicsScene, parent: Optional[QWidget] = None) -> None:
        super().__init__(scene, parent)
        self._mode: str = "none"  # one of: 'none' | 'pan' | 'points'
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        factor = 1.20 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def reset_zoom(self) -> None:
        self.setTransform(QtGui.QTransform())  # identity transform to reset

    def zoom_to_rect(self, rect: QRectF) -> None:
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def pan(self, delta: QPointF) -> None:
        self.translate(delta.x(), delta.y())

    # Interaction mode helpers
    def set_mode(self, mode: str) -> None:
        self._mode = mode

    def mousePressEvent(self, event: QtGui.QMouseEvent | None) -> None:
        if event is None:
            return

        if self._mode == "points" and event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            self.point_clicked.emit(scene_pos)
            event.accept()
            return
        else:
            # default behaviour when mode is not "points"
            super().mousePressEvent(event)

    def draw_point_list(self, points: list[list[QPointF]], colors=MANIPULATOR_COLORS, size=6) -> None:
        # Takes in a list of point lists and draws them all
        skene = self.scene()
        if skene:
            # Clear previous points
            for item in self.drawn_points:
                skene.removeItem(item)
            self.drawn_points.clear()

            # Draw new points
            for point_list in points:
                for i, point in enumerate(point_list):
                    color = colors[i % len(colors)] # just in case someone modifies this to use more than 4 manipulators
                    ellipse = QGraphicsEllipseItem(
                        point.x() - size / 2,
                        point.y() - size / 2,
                        size,
                        size,
                    )
                    ellipse.setBrush(color)
                    ellipse.setPen(QtGui.QPen(Qt.GlobalColor.black))
                    skene.addItem(ellipse)
                    self.drawn_points.append(ellipse)

class DualGraphicsWidget(QWidget):
    """Two QGraphicsViews with a shared toolbar of common tools."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Dual Graphics Views!!!!!!! WITH BUTTONS!!!!!")

        # Scenes and views
        self._scene_left = QGraphicsScene(self)
        self._scene_right = QGraphicsScene(self)

        self._view_left = GraphicsView(self._scene_left)
        self._view_right = GraphicsView(self._scene_right)

        # Toolbar and actions
        self._toolbar = QToolBar("Tools", self)
        self._toolbar.setIconSize(self._toolbar.iconSize())

        self._act_reset = QAction("Reset", self)
        self._act_pan = QAction("Pan", self)
        self._act_points = QAction("Points", self)
        self._act_pan.setCheckable(True)
        self._act_points.setCheckable(True)
        self._act_pan.setChecked(True)
        self._on_pan_toggled(True)
        self._show_left = QAction("Show Left", self)
        self._show_left.setCheckable(True)
        self._show_left.setChecked(True)
        self._show_right = QAction("Show Right", self)
        self._show_right.setCheckable(True)
        self._show_right.setChecked(True)

        # Group selection/pan mutually exclusive
        self._act_points.toggled.connect(self._on_points_toggled)
        self._act_pan.toggled.connect(self._on_pan_toggled)
        self._show_left.toggled.connect(
            lambda checked: self._view_left.setVisible(checked)
        )
        self._show_right.toggled.connect(
            lambda checked: self._view_right.setVisible(checked)
        )

        # Wire actions
        self._act_reset.triggered.connect(lambda: self._apply(lambda v: v.reset_zoom()))

        self._toolbar.addAction(self._act_reset)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._act_pan)
        self._toolbar.addAction(self._act_points)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._show_left)
        self._toolbar.addAction(self._show_right)

        # Layout
        views = QWidget(self)
        h = QHBoxLayout(views)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(self._view_left)
        h.addWidget(self._view_right)

        root = QVBoxLayout(self)
        root.addWidget(self._toolbar)
        root.addWidget(views, 1)
        self.setLayout(root)




    def _apply(self, fn):
        fn(self._view_left)
        fn(self._view_right)

    def _on_points_toggled(self, checked: bool) -> None:
        if checked:
            # Turn off pan
            if self._act_pan.isChecked():
                self._act_pan.setChecked(False)
            self._apply(lambda v: v.setDragMode(QGraphicsView.DragMode.NoDrag))
            self._apply(lambda v: v.set_mode("points"))
        else:
            self._apply(lambda v: v.set_mode("none"))

    def _on_pan_toggled(self, checked: bool) -> None:
        if checked:
            if self._act_points.isChecked():
                self._act_points.setChecked(False)
            self._apply(lambda v: v.set_mode("pan"))
            self._apply(lambda v: v.setDragMode(QGraphicsView.DragMode.ScrollHandDrag))
        else:
            self._apply(lambda v: v.set_mode("none"))
            self._apply(lambda v: v.setDragMode(QGraphicsView.DragMode.NoDrag))

    def set_scene(self, side, scene: QGraphicsScene) -> None:
        if side == "left":
            self._view_left.setScene(scene)
        elif side == "right":
            self._view_right.setScene(scene)
        else:
            raise ValueError(f"Invalid side: {side}, must be 'left' or 'right'")
        
    @pyqtSlot()
    def draw_points_on_left(self, points: list[list[QPointF]]) -> None:
        self._view_left.draw_point_list(points)

    @pyqtSlot()
    def draw_points_on_right(self, points: list[list[QPointF]]) -> None:
        self._view_right.draw_point_list(points)
