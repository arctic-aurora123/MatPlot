import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QSpinBox, QCheckBox, QLineEdit, QColorDialog, QSlider, QGroupBox, QFormLayout, QTextEdit)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Plotter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MatPlot")
        self.setGeometry(100, 100, 1400, 800)

        # 主窗口分为两大部分：左侧的绘图区域和右侧的控制面板
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # 创建绘图区域
        self.plot_widget = QWidget()
        self.plot_layout = QVBoxLayout(self.plot_widget)
        self.canvas = FigureCanvas(Figure(figsize=(8, 6)))
        self.plot_layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()
        self.main_layout.addWidget(self.plot_widget, 3)  # 占据主窗口3/4的宽度

        # 创建控制面板区域
        self.control_widget = QWidget()
        self.control_layout = QVBoxLayout(self.control_widget)
        self.main_layout.addWidget(self.control_widget, 1)  # 占据主窗口1/4的宽度

        # 文件选择与保存区域
        self.file_groupbox = QGroupBox("File")
        self.file_layout = QVBoxLayout()
        self.upload_button = QPushButton("Upload CSV", self)
        self.upload_button.clicked.connect(self.load_csv)
        self.save_button = QPushButton("Save Plot", self)
        self.save_button.clicked.connect(self.save_plot)  # 添加保存绘图功能
        self.file_layout.addWidget(self.upload_button)
        self.file_layout.addWidget(self.save_button)
        # self.file_preview = QTextEdit()  # 用于显示CSV文件的预览
        # self.file_preview.setReadOnly(True)
        # self.file_layout.addWidget(QLabel("File Preview:"))
        # self.file_layout.addWidget(self.file_preview)
        self.file_preview = QTableWidget()  # 使用QTableWidget来展示CSV预览
        self.file_preview.setColumnCount(0)
        self.file_preview.setRowCount(0)
        self.file_layout.addWidget(QLabel("File Preview:"))
        self.file_layout.addWidget(self.file_preview)
        self.file_groupbox.setLayout(self.file_layout)
        self.control_layout.addWidget(self.file_groupbox)

        # 子图行列设置区域
        self.subplot_groupbox = QGroupBox("Subplot Settings")
        self.subplot_layout = QFormLayout()
        self.row_spin = QSpinBox(self)
        self.row_spin.setRange(1, 4)
        self.row_spin.setValue(1)
        self.row_spin.valueChanged.connect(self.update_subplot_selector)
        self.subplot_layout.addRow(QLabel("Rows:"), self.row_spin)
        self.col_spin = QSpinBox(self)
        self.col_spin.setRange(1, 4)
        self.col_spin.setValue(1)
        self.col_spin.valueChanged.connect(self.update_subplot_selector)
        self.subplot_layout.addRow(QLabel("Columns:"), self.col_spin)
        self.subplot_selector = QComboBox(self)
        self.subplot_layout.addRow(QLabel("Subplot (row, col):"), self.subplot_selector)
        self.subplot_groupbox.setLayout(self.subplot_layout)
        self.control_layout.addWidget(self.subplot_groupbox)

        # 图形大小调整区域
        self.figsize_groupbox = QGroupBox("Figure Size")
        self.figsize_layout = QFormLayout()
        self.fig_width_spin = QSpinBox(self)
        self.fig_width_spin.setRange(4, 20)
        self.fig_width_spin.setValue(8)
        self.figsize_layout.addRow(QLabel("Width:"), self.fig_width_spin)
        self.fig_height_spin = QSpinBox(self)
        self.fig_height_spin.setRange(4, 20)
        self.fig_height_spin.setValue(6)
        self.figsize_layout.addRow(QLabel("Height:"), self.fig_height_spin)
        self.figsize_groupbox.setLayout(self.figsize_layout)
        self.control_layout.addWidget(self.figsize_groupbox)

        # 模式选择区域
        self.mode_groupbox = QGroupBox("Mode & Variables")
        self.mode_layout = QFormLayout()
        self.plot_type_combo = QComboBox(self)
        self.plot_type_combo.addItems(["Line", "Scatter", "Bar", "Stem", "Pie"])
        self.plot_type_combo.currentIndexChanged.connect(self.update_parameter_panel)
        self.x_combo = QComboBox(self)
        self.y_combo = QComboBox(self)
        self.mode_layout.addRow(QLabel("Plot Type:"), self.plot_type_combo)
        self.mode_layout.addRow(QLabel("X Variable:"), self.x_combo)
        self.mode_layout.addRow(QLabel("Y Variable:"), self.y_combo)
        self.mode_groupbox.setLayout(self.mode_layout)
        self.control_layout.addWidget(self.mode_groupbox)

        # 参数调整区域
        self.param_groupbox = QGroupBox("Parameters")
        self.param_layout = QVBoxLayout()
        self.color_label = QLabel("Color:")
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        self.linewidth_label = QLabel("Line Width:")
        self.linewidth_spin = QSpinBox()
        self.linewidth_spin.setRange(1, 10)
        self.linewidth_spin.setValue(2)
        self.markersize_label = QLabel("Marker Size:")
        self.markersize_spin = QSpinBox()
        self.markersize_spin.setRange(1, 20)
        self.markersize_spin.setValue(6)

        # 散点图支持 marker 样式选择
        self.marker_label = QLabel("Marker:")
        self.marker_combo = QComboBox()
        self.marker_combo.addItems(['o', 'x', 's', '^', 'D', 'v'])  # 添加常见标记

        self.alpha_label = QLabel("Alpha (Transparency):")
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_slider.setValue(100)
        self.alpha_slider.setTickInterval(10)
        self.alpha_slider.setSingleStep(5)
        self.param_layout.addWidget(self.color_label)
        self.param_layout.addWidget(self.color_button)
        self.param_layout.addWidget(self.linewidth_label)
        self.param_layout.addWidget(self.linewidth_spin)
        self.param_layout.addWidget(self.markersize_label)
        self.param_layout.addWidget(self.markersize_spin)
        self.param_layout.addWidget(self.marker_label)
        self.param_layout.addWidget(self.marker_combo)
        self.param_layout.addWidget(self.alpha_label)
        self.param_layout.addWidget(self.alpha_slider)
        self.param_groupbox.setLayout(self.param_layout)
        self.control_layout.addWidget(self.param_groupbox)

        # 茎叶图支持 basefmt, linefmt, markerfmt
        self.stem_linefmt_label = QLabel("Line Format (linefmt):")
        self.stem_linefmt_edit = QLineEdit('r-')
        self.stem_markerfmt_label = QLabel("Marker Format (markerfmt):")
        self.stem_markerfmt_edit = QLineEdit('ro')
        self.stem_basefmt_label = QLabel("Base Format (basefmt):")
        self.stem_basefmt_edit = QLineEdit('k-')

        self.param_layout.addWidget(self.stem_linefmt_label)
        self.param_layout.addWidget(self.stem_linefmt_edit)
        self.param_layout.addWidget(self.stem_markerfmt_label)
        self.param_layout.addWidget(self.stem_markerfmt_edit)
        self.param_layout.addWidget(self.stem_basefmt_label)
        self.param_layout.addWidget(self.stem_basefmt_edit)

        # 图例、标题、标签等区域
        self.label_groupbox = QGroupBox("Labels & Grid")
        self.label_layout = QFormLayout()
        self.title_edit = QLineEdit()
        self.title_size_spin = QSpinBox()  # 标题大小
        self.title_size_spin.setRange(8, 30)
        self.title_size_spin.setValue(12)
        self.x_label_edit = QLineEdit()
        self.x_label_size_spin = QSpinBox()  # x轴标签大小
        self.x_label_size_spin.setRange(8, 30)
        self.x_label_size_spin.setValue(10)
        self.y_label_edit = QLineEdit()
        self.y_label_size_spin = QSpinBox()  # y轴标签大小
        self.y_label_size_spin.setRange(8, 30)
        self.y_label_size_spin.setValue(10)
        self.legend_edit = QLineEdit()  # 新增图例输入框
        self.legend_check = QCheckBox("Show Legend")
        self.grid_check = QCheckBox("Show Grid")
        self.latex_check = QCheckBox("Use LaTeX for Text Rendering")
        self.label_layout.addRow(QLabel("Title:"), self.title_edit)
        self.label_layout.addRow(QLabel("Title Size:"), self.title_size_spin)  # 标题大小
        self.label_layout.addRow(QLabel("X Label:"), self.x_label_edit)
        self.label_layout.addRow(QLabel("X Label Size:"), self.x_label_size_spin)  # x轴标签大小
        self.label_layout.addRow(QLabel("Y Label:"), self.y_label_edit)
        self.label_layout.addRow(QLabel("Y Label Size:"), self.y_label_size_spin)  # y轴标签大小
        self.label_layout.addRow(QLabel("Legend Text:"), self.legend_edit)  # 图例输入框添加到布局
        self.label_layout.addRow(self.legend_check)
        self.label_layout.addRow(self.grid_check)
        self.label_layout.addRow(self.latex_check)
        self.label_groupbox.setLayout(self.label_layout)
        self.control_layout.addWidget(self.label_groupbox)

        # 保存每个子图的设置
        self.subplot_settings = {}

        # 隐藏参数控件并更新面板
        self.hide_all_parameter_widgets()
        self.update_subplot_selector()

        # 绘图按钮
        self.plot_button = QPushButton("Plot", self)
        self.plot_button.clicked.connect(self.plot_data)
        self.control_layout.addWidget(self.plot_button)

    def hide_all_parameter_widgets(self):
        self.color_label.hide()
        self.color_button.hide()
        self.linewidth_label.hide()
        self.linewidth_spin.hide()
        self.markersize_label.hide()
        self.markersize_spin.hide()
        self.marker_label.hide()
        self.marker_combo.hide()
        self.alpha_label.hide()
        self.alpha_slider.hide()
        self.stem_linefmt_label.hide()
        self.stem_linefmt_edit.hide()
        self.stem_markerfmt_label.hide()
        self.stem_markerfmt_edit.hide()
        self.stem_basefmt_label.hide()
        self.stem_basefmt_edit.hide()

    def update_parameter_panel(self):
        plot_type = self.plot_type_combo.currentText()
        self.hide_all_parameter_widgets()

        if plot_type == "Line":
            self.color_label.show()
            self.color_button.show()
            self.linewidth_label.show()
            self.linewidth_spin.show()

        elif plot_type == "Scatter":
            self.color_label.show()
            self.color_button.show()
            self.markersize_label.show()
            self.markersize_spin.show()
            self.marker_label.show()
            self.marker_combo.show()
            self.alpha_label.show()
            self.alpha_slider.show()

        elif plot_type == "Bar":
            self.color_label.show()
            self.color_button.show()

        elif plot_type == "Stem":
            self.color_label.show()
            self.color_button.show()
            self.stem_linefmt_label.show()
            self.stem_linefmt_edit.show()
            self.stem_markerfmt_label.show()
            self.stem_markerfmt_edit.show()
            self.stem_basefmt_label.show()
            self.stem_basefmt_edit.show()

        elif plot_type == "Pie":
            self.color_label.show()
            self.color_button.show()

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}")

    def update_table_preview(self, df):
        """更新表格中的CSV预览"""
        self.file_preview.setRowCount(df.shape[0])  # 设置表格行数
        self.file_preview.setColumnCount(df.shape[1])  # 设置表格列数
        self.file_preview.setHorizontalHeaderLabels(df.columns)  # 设置表头

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.file_preview.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))  # 填充表格数据

        self.file_preview.resizeColumnsToContents()  # 调整列宽度以适应内容
    
    def load_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)
        if file_name:
            self.df = pd.read_csv(file_name)
            self.x_combo.clear()
            self.y_combo.clear()
            self.x_combo.addItems(self.df.columns)
            self.y_combo.addItems(self.df.columns)
            self.update_subplot_selector()

            # 预览CSV文件中的数据
            self.update_table_preview(self.df)

    def update_subplot_selector(self):
        self.subplot_selector.clear()
        rows = self.row_spin.value()
        cols = self.col_spin.value()

        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                self.subplot_selector.addItem(f"({r}, {c})")

    def save_subplot_settings(self, subplot_key):
        """保存当前子图的设置"""
        self.subplot_settings[subplot_key] = {
            'x_var': self.x_combo.currentText(),
            'y_var': self.y_combo.currentText(),
            'plot_type': self.plot_type_combo.currentText(),
            'color': getattr(self, 'selected_color', 'blue'),
            'linewidth': self.linewidth_spin.value(),
            'markersize': self.markersize_spin.value(),
            'marker': self.marker_combo.currentText(),
            'alpha': self.alpha_slider.value() / 100,
            'stem_linefmt': self.stem_linefmt_edit.text(),
            'stem_markerfmt': self.stem_markerfmt_edit.text(),
            'stem_basefmt': self.stem_basefmt_edit.text(),
            'title': self.title_edit.text(),
            'title_size': self.title_size_spin.value(),  # 标题字体大小
            'x_label': self.x_label_edit.text(),
            'x_label_size': self.x_label_size_spin.value(),  # x轴标签字体大小
            'y_label': self.y_label_edit.text(),
            'y_label_size': self.y_label_size_spin.value(),  # y轴标签字体大小
            'legend': self.legend_edit.text(),
            'show_legend': self.legend_check.isChecked(),
            'show_grid': self.grid_check.isChecked(),
            'use_latex': self.latex_check.isChecked()
        }

    def load_subplot_settings(self, subplot_key):
        """加载并应用存储的子图设置"""
        settings = self.subplot_settings.get(subplot_key, None)
        if settings:
            self.x_combo.setCurrentText(settings['x_var'])
            self.y_combo.setCurrentText(settings['y_var'])
            self.plot_type_combo.setCurrentText(settings['plot_type'])
            self.selected_color = settings['color']
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}")
            self.linewidth_spin.setValue(settings['linewidth'])
            self.markersize_spin.setValue(settings['markersize'])
            self.marker_combo.setCurrentText(settings['marker'])
            self.alpha_slider.setValue(int(settings['alpha'] * 100))
            self.stem_linefmt_edit.setText(settings['stem_linefmt'])
            self.stem_markerfmt_edit.setText(settings['stem_markerfmt'])
            self.stem_basefmt_edit.setText(settings['stem_basefmt'])
            self.title_edit.setText(settings['title'])
            self.title_size_spin.setValue(settings['title_size'])  # 标题字体大小
            self.x_label_edit.setText(settings['x_label'])
            self.x_label_size_spin.setValue(settings['x_label_size'])  # x轴标签字体大小
            self.y_label_edit.setText(settings['y_label'])
            self.y_label_size_spin.setValue(settings['y_label_size'])  # y轴标签字体大小
            self.legend_edit.setText(settings['legend'])
            self.legend_check.setChecked(settings['show_legend'])
            self.grid_check.setChecked(settings['show_grid'])
            self.latex_check.setChecked(settings['use_latex'])

    def apply_latex_settings(self):
        """应用LaTeX设置"""
        if self.latex_check.isChecked():
            plt.rc('text', usetex=True)
            plt.rc('font', family='serif', serif=['Times'])
        else:
            plt.rc('text', usetex=False)

    def plot_data(self):
        x_var = self.x_combo.currentText()
        y_var = self.y_combo.currentText()
        plot_type = self.plot_type_combo.currentText()
        rows = self.row_spin.value()
        cols = self.col_spin.value()
        fig_width = self.fig_width_spin.value()
        fig_height = self.fig_height_spin.value()

        subplot_key = self.subplot_selector.currentText()
        self.save_subplot_settings(subplot_key)

        # 应用LaTeX设置
        self.apply_latex_settings()

        if self.df is not None:
            self.canvas.figure.clf()  # 清除当前的图形
            self.canvas.figure.set_size_inches(fig_width, fig_height)
            axes = self.canvas.figure.subplots(rows, cols)

            if rows == 1 and cols == 1:
                axes = [axes]  # 处理单一子图的情况
            elif rows == 1 or cols == 1:
                axes = axes.flatten()  # 处理单行或单列多子图
            else:
                axes = axes.ravel()  # 将多行多列的子图转成一维列表

            for i, ax in enumerate(axes):
                subplot_key = f"({(i // cols) + 1}, {(i % cols) + 1})"
                if subplot_key in self.subplot_settings:
                    settings = self.subplot_settings[subplot_key]
                    color = settings['color']
                    alpha = settings['alpha']

                    x_data = self.df[settings['x_var']]
                    y_data = self.df[settings['y_var']]

                    if settings['plot_type'] == "Line":
                        ax.plot(x_data, y_data, color=color, linewidth=settings['linewidth'], marker='o', markersize=settings['markersize'])
                    elif settings['plot_type'] == "Scatter":
                        ax.scatter(x_data, y_data, color=color, s=settings['markersize'] * 10, alpha=alpha, marker=settings['marker'])
                    elif settings['plot_type'] == "Bar":
                        ax.bar(x_data, y_data, color=color)
                    elif settings['plot_type'] == "Stem":
                        ax.stem(x_data, y_data, linefmt=settings['stem_linefmt'], markerfmt=settings['stem_markerfmt'], basefmt=settings['stem_basefmt'])
                    elif settings['plot_type'] == "Pie":
                        ax.pie(y_data, labels=x_data, colors=[color])

                    # 设置子图的标题、x轴和y轴标签，支持大小调整
                    ax.set_title(settings['title'], fontsize=settings['title_size'], usetex=settings['use_latex'])
                    ax.set_xlabel(settings['x_label'], fontsize=settings['x_label_size'], usetex=settings['use_latex'])
                    ax.set_ylabel(settings['y_label'], fontsize=settings['y_label_size'], usetex=settings['use_latex'])

                    # 显示图例和网格
                    if settings['show_legend']:
                        ax.legend([settings['legend']])
                    if settings['show_grid']:
                        ax.grid(True)

            self.canvas.figure.tight_layout()  # 使用 tight_layout 调整布局
            self.canvas.draw()

    def save_plot(self):
        """保存当前绘图为图像文件"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf)", options=options)
        if file_name:
            self.canvas.figure.savefig(file_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    plotter = Plotter()
    plotter.show()
    sys.exit(app.exec_())
