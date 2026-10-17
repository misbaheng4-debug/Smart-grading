import json
import os
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle


BG = (0.95, 0.96, 1.0, 1)
INK = (0.13, 0.17, 0.29, 1)
PURPLE = (0.39, 0.29, 0.91, 1)
BLUE = (0.16, 0.48, 0.91, 1)
GREEN = (0.08, 0.58, 0.34, 1)
ORANGE = (0.88, 0.43, 0.08, 1)
RED = (0.82, 0.16, 0.22, 1)
MUTED = (0.40, 0.44, 0.54, 1)
WHITE = (1, 1, 1, 1)


def grade_for(marks):
    if marks >= 80:
        return "A+  Excellent! 🌟", GREEN
    if marks >= 70:
        return "A  Very Good", BLUE
    if marks >= 60:
        return "B  Good", ORANGE
    if marks >= 40:
        return "D  Pass", INK
    return "FAIL", RED


class RoundedPanel(BoxLayout):
    def __init__(self, color=WHITE, radius=22, **kwargs):
        super().__init__(**kwargs)
        self.panel_color = color
        self.radius = radius
        with self.canvas.before:
            self._color_instruction = Color(*self.panel_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(self.radius)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def set_panel_color(self, color):
        self.panel_color = color
        self._color_instruction.rgba = color

    def _update_rect(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


class SmartGradingApp(App):
    def build(self):
        self.title = "Smart Grading"
        self.records_path = os.path.join(self.user_data_dir, "saved_results.json")
        self.records = self.load_records()

        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        root.bind(size=lambda *_: setattr(root, "padding", [dp(18), dp(18), dp(18), dp(12)]))
        with root.canvas.before:
            Color(*BG)
            self.bg_rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[0])
        root.bind(pos=self._update_bg, size=self._update_bg)

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(82), spacing=dp(3))
        header.add_widget(Label(text="[b]SMART GRADING[/b]", markup=True,
                                font_size="25sp", color=PURPLE, halign="left",
                                valign="middle", size_hint_y=0.62))
        header.add_widget(Label(text="Student marks • Simple and colorful",
                                font_size="14sp", color=MUTED, halign="left",
                                valign="top", size_hint_y=0.38))
        root.add_widget(header)

        form = RoundedPanel(orientation="vertical", padding=dp(16),
                            spacing=dp(10), size_hint_y=None, height=dp(280))
        form.add_widget(self.make_label("STUDENT NAME", 12, MUTED, height=dp(22)))
        self.name_input = TextInput(hint_text="Enter student name", multiline=False,
                                    size_hint_y=None, height=dp(46), font_size="16sp",
                                    padding=[dp(12), dp(12), dp(12), dp(8)],
                                    background_normal="", background_active="",
                                    background_color=(0.95, 0.96, 1, 1),
                                    foreground_color=INK, hint_text_color=MUTED)
        form.add_widget(self.name_input)

        form.add_widget(self.make_label("MARKS (0–100)", 12, MUTED, height=dp(22)))
        self.marks_input = TextInput(hint_text="e.g. 85", multiline=False,
                                     input_filter="int", size_hint_y=None, height=dp(46),
                                     font_size="18sp", halign="center",
                                     padding=[dp(12), dp(12), dp(12), dp(8)],
                                     background_normal="", background_active="",
                                     background_color=(0.95, 0.96, 1, 1),
                                     foreground_color=INK, hint_text_color=MUTED)
        form.add_widget(self.marks_input)

        self.check_button = Button(text="CHECK GRADE", size_hint_y=None, height=dp(48),
                                   background_normal="", background_down="",
                                   background_color=PURPLE, color=WHITE,
                                   font_size="16sp", bold=True)
        self.check_button.bind(on_release=self.check_grade)
        form.add_widget(self.check_button)
        root.add_widget(form)

        self.result_panel = RoundedPanel(orientation="vertical", padding=dp(14),
                                          spacing=dp(4), size_hint_y=None, height=dp(105),
                                          color=(0.91, 0.89, 1, 1))
        self.result_label = Label(text="Your grade will appear here",
                                  font_size="20sp", bold=True, color=PURPLE)
        self.result_detail = Label(text="Enter a name and marks to begin",
                                   font_size="13sp", color=MUTED)
        self.result_panel.add_widget(self.result_label)
        self.result_panel.add_widget(self.result_detail)
        root.add_widget(self.result_panel)

        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        self.save_button = Button(text="SAVE RESULT", background_normal="",
                                  background_down="", background_color=GREEN,
                                  color=WHITE, bold=True, disabled=True)
        self.save_button.bind(on_release=self.save_result)
        actions.add_widget(self.save_button)
        clear_button = Button(text="CLEAR", background_normal="", background_down="",
                              background_color=(0.88, 0.90, 0.95, 1), color=INK,
                              bold=True, size_hint_x=0.55)
        clear_button.bind(on_release=self.clear_form)
        actions.add_widget(clear_button)
        root.add_widget(actions)

        root.add_widget(self.make_label("SAVED RESULTS", 15, INK, height=dp(25)))
        scroll = ScrollView(do_scroll_x=False)
        self.history = BoxLayout(orientation="vertical", spacing=dp(7),
                                 size_hint_y=None, padding=[0, dp(2), 0, dp(8)])
        self.history.bind(minimum_height=self.history.setter("height"))
        scroll.add_widget(self.history)
        root.add_widget(scroll)

        self.current_record = None
        self.refresh_history()
        return root

    def _update_bg(self, widget, *_):
        self.bg_rect.pos = widget.pos
        self.bg_rect.size = widget.size

    def make_label(self, text, size, color, height=None):
        return Label(text=text, font_size=f"{size}sp", color=color,
                     bold=True, size_hint_y=None, height=height or dp(25),
                     halign="left", valign="middle")

    def load_records(self):
        try:
            with open(self.records_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (OSError, ValueError):
            return []

    def write_records(self):
        os.makedirs(self.user_data_dir, exist_ok=True)
        with open(self.records_path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)

    def check_grade(self, *_):
        name = self.name_input.text.strip()
        marks_text = self.marks_input.text.strip()

        if not name:
            self.show_message("Enter the student's name", RED)
            return
        if not marks_text:
            self.show_message("Enter marks from 0 to 100", RED)
            return

        try:
            marks = int(marks_text)
        except ValueError:
            self.show_message("Marks must be a whole number", RED)
            return

        if not 0 <= marks <= 100:
            self.show_message("Marks must be between 0 and 100", RED)
            return

        grade, color = grade_for(marks)
        self.current_record = {
            "name": name,
            "marks": marks,
            "grade": grade,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.result_label.text = grade
        self.result_label.color = color
        self.result_detail.text = f"{name}  •  {marks}/100"
        self.result_panel.set_panel_color((0.91, 0.89, 1, 1) if color == PURPLE else (
            0.90, 0.97, 0.92, 1) if color == GREEN else (
            0.89, 0.94, 1, 1) if color == BLUE else (
            1, 0.94, 0.85, 1) if color == ORANGE else (
            1, 0.90, 0.90, 1) if color == RED else (0.94, 0.95, 0.98, 1))
        self.save_button.disabled = False

    def show_message(self, message, color):
        self.result_label.text = message
        self.result_label.color = color
        self.result_detail.text = "Please check the information and try again"
        self.save_button.disabled = True

    def save_result(self, *_):
        if not self.current_record:
            return
        self.records.insert(0, dict(self.current_record))
        self.records = self.records[:1000]
        try:
            self.write_records()
        except OSError:
            self.show_message("Could not save result", RED)
            return
        self.refresh_history()
        self.result_detail.text = "Result saved on this device"
        self.save_button.disabled = True

    def refresh_history(self):
        self.history.clear_widgets()
        if not self.records:
            self.history.add_widget(Label(
                text="No saved results yet", color=MUTED, font_size="14sp",
                size_hint_y=None, height=dp(42)))
            return
        for record in self.records[:50]:
            row = RoundedPanel(orientation="horizontal", padding=[dp(12), dp(8)],
                               spacing=dp(8), size_hint_y=None, height=dp(58),
                               color=WHITE, radius=14)
            details = BoxLayout(orientation="vertical", spacing=dp(1))
            details.add_widget(Label(text=f"[b]{record.get('name', 'Student')}[/b]",
                                     markup=True, color=INK, font_size="14sp",
                                     halign="left", valign="middle"))
            details.add_widget(Label(text=f"{record.get('marks', '?')}/100  •  {record.get('date', '')}",
                                     color=MUTED, font_size="11sp",
                                     halign="left", valign="middle"))
            row.add_widget(details)
            row.add_widget(Label(text=record.get("grade", ""), color=PURPLE,
                                 font_size="12sp", bold=True, size_hint_x=0.42))
            self.history.add_widget(row)

    def clear_form(self, *_):
        self.name_input.text = ""
        self.marks_input.text = ""
        self.current_record = None
        self.result_label.text = "Your grade will appear here"
        self.result_label.color = PURPLE
        self.result_detail.text = "Enter a name and marks to begin"
        self.result_panel.set_panel_color((0.91, 0.89, 1, 1))
        self.save_button.disabled = True


if __name__ == "__main__":
    SmartGradingApp().run()
