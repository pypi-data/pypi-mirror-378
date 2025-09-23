from PySideJZ.JZContainer import JZContainer
from PySideJZ.JZAbvs import JZAbvs
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QSlider, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStyle


class JZSliderH(JZContainer):

    valueChanged = Signal(int)  # noqa: N815
    setValueSilent = Signal(int)  # noqa: N815

    def __init__(
        self,
        parent: QWidget,
        min_value: int = 0,
        max_value: int = 1000,
        step: int = 1,
        minimum_text: str = "",
        maximum_text: str = "",
    ) -> None:

        super().__init__(parent=parent, layout=QVBoxLayout(), spacing=0, margin=0, name="NoBorder")

        self._step = step
        self._min = min_value
        self._max = max_value

        self._top = JZContainer(self, layout=QHBoxLayout(), spacing=3, margin=0, name="NoBorder")
        self._bot = JZContainer(self, layout=QHBoxLayout(), spacing=0, margin=0, name="NoBorder")
        self.addMultiple([self._top, self._bot])

        self._min_label = QLabel(minimum_text)
        self._max_label = QLabel(maximum_text)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(min_value)
        self.slider.setMaximum(max_value)
        self.slider.setSingleStep(step)
        self._label_value = QLabel("0")
        self._label_value.setAlignment(JZAbvs.Align.C)

        self._top.addMultiple([self._min_label, self.slider, self._max_label])
        self._bot.addWidget(self._label_value)

        self.slider.valueChanged.connect(self._on_slider_value_changed)
        self.valueChanged.connect(self._on_value_changed)
        self.slider.mousePressEvent = self._slider_mouse_press_event
        self.setValueSilent.connect(self._on_set_value_silent)

    def _on_slider_value_changed(self, value: int) -> None:
        snapped = ((value - self._min) // self._step) * self._step + self._min
        snapped = max(self._min, min(snapped, self._max))
        if value != snapped:
            self.slider.blockSignals(True)
            self.slider.setValue(snapped)
            self.slider.blockSignals(False)
        self.valueChanged.emit(snapped)

    def _on_value_changed(self, value: int) -> None:
        self._label_value.setText(str(value))

    def _slider_mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            from PySide6.QtWidgets import QStyleOptionSlider
            opt = QStyleOptionSlider()
            self.slider.initStyleOption(opt)
            handle_rect = self.slider.style().subControlRect(
                QStyle.CC_Slider,
                opt,
                QStyle.SC_SliderHandle,
                self.slider
            )
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            if not handle_rect.contains(pos):
                slider_width = self.slider.width()
                slider_min = self._min
                slider_max = self._max
                slider_range = slider_max - slider_min

                ratio = pos.x() / slider_width
                value = slider_min + round(ratio * slider_range)

                # Snap to step
                snapped = ((value - self._min) // self._step) * self._step + self._min
                snapped = max(self._min, min(snapped, self._max))
                self.slider.setValue(snapped)
                event.accept()
                return
        QSlider.mousePressEvent(self.slider, event)

    @Slot(int)
    def _on_set_value_silent(self, value: int) -> None:
        """Set the slider and label value without emitting valueChanged."""
        snapped = ((value - self._min) // self._step) * self._step + self._min
        snapped = max(self._min, min(snapped, self._max))
        self.slider.blockSignals(True)
        self.slider.setValue(snapped)
        self.slider.blockSignals(False)
        self._label_value.setText(str(snapped))