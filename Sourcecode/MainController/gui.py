from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Line
from kivy.vector import Vector
from kivy.clock import Clock
from hexifier import hexify


from settings import Voltages, Roles, Side, COLOR_DICT
from smart_grid_table import SmartGridTable, TableSection, ModuleFlowSegment, DefaultModule, ConnectionModule
from smart_grid_messaging import MessageTypes, SmartMessage
from grids import *
from hexifier import hexify



class Gui(App):
    def __init__(self, smart_grid_table, add_message_func):
        super(Gui, self).__init__()
        self.smart_grid_table = smart_grid_table
        self.add_message_func = add_message_func
        self.screen_manager = None

    def run(self):
        from kivy.core.window import Window

        Builder.load_file('kv/gui.kv')
        self.screen_manager = ScreenManager()
        Window.size = (800, 480)
        super(Gui, self).run()

    def build(self):
        self.screen_manager.add_widget(TableSectionOverviewScreen(name='TableSectionOverviewScreen', gui=self))
        self.screen_manager.add_widget(ModuleOverviewScreen(name='ModuleOverviewScreen', gui=self))
        self.screen_manager.add_widget(ModuleConfigurationScreen(name='ModuleConfigurationScreen', gui=self))
        self.screen_manager.add_widget(ConfigurationScreen(name='ConfigurationScreen', gui=self))
        self.screen_manager.add_widget(ColorChangeScreen(name='ColorChangeScreen', gui=self))
        return self.screen_manager

    """Callbacks"""
    def on_slider_change(self, obj, value):
        """If there is a slider change, update the smart grid table"""
        self.screen_manager.get_screen('ModuleConfigurationScreen').set_slider_value(str(int(value)), obj.get_slider_id())
        module_id = self.screen_manager.get_screen('ModuleConfigurationScreen').get_module_id()
        config_id = obj.get_config_id()
        s_message = SmartMessage(MessageTypes.CONFIG_CHANGED, (module_id, config_id, value))
        self.add_message_func(s_message)

    def set_module_overview(self, obj):
        self.screen_manager.transition.direction = 'left'
        self.screen_manager.get_screen('ModuleOverviewScreen').set_table_section_id(obj.get_table_section_id())
        self.screen_manager.current = 'ModuleOverviewScreen'

    def set_module_overview_from_transformer(self, obj):
        module = self.smart_grid_table.get_module(obj.get_module_id())
        if module is None:
            return

        linked_table = module.get_linked_module().get_table_section()
        if linked_table is None:
            return

        self.screen_manager.transition.direction = obj.get_transition_side()
        self.screen_manager.get_screen('ModuleOverviewScreen').set_table_section_id(linked_table.get_id())
        self.screen_manager.current = 'ModuleOverviewScreen'

        self.refresh()

    def set_module_configuration_screen(self, obj):
        self.screen_manager.transition.direction = 'left'
        self.screen_manager.get_screen('ModuleConfigurationScreen').set_module_id(obj.get_module_id())
        self.screen_manager.current = 'ModuleConfigurationScreen'

    def refresh(self):
        Clock.schedule_once(self.refresh_screen, 0)

    def refresh_screen(self, dt):
        if self.screen_manager.current not in [None, 'ModuleConfigurationScreen', 'ConfigurationScreen', 'ColorChangeScreen']:
            children = [child for child in self.screen_manager.get_screen(self.screen_manager.current).ids.grid.children
                        if not isinstance(child, FlowSegmentWidget)]
            self.screen_manager.get_screen(self.screen_manager.current).ids.grid.clear_widgets(children)
            self.screen_manager.get_screen(self.screen_manager.current).on_pre_enter()

    def reboot_tables(self):
        s_message = SmartMessage(MessageTypes.RESET_TABLES)
        self.add_message_func(s_message)

    def disable_buzzer(self):
        s_message = SmartMessage(MessageTypes.BUZZER_ENABLE, (False,))
        self.add_message_func(s_message)

    def enable_buzzer(self):
        s_message = SmartMessage(MessageTypes.BUZZER_ENABLE, (True,))
        self.add_message_func(s_message)

    def shutdown_app(self):
        s_message = SmartMessage(MessageTypes.SHUTDOWN_APP, ())
        self.add_message_func(s_message)

    def show_color_change_screen(self, obj):
        self.screen_manager.transition.direction = 'left'
        self.screen_manager.get_screen('ColorChangeScreen').set_color_id(obj.color_id)
        self.screen_manager.current = 'ColorChangeScreen'


class ColoredButton(Button):
    def __init__(self, **kwargs):
        super(ColoredButton, self).__init__(**kwargs)
        self.background_color = kwargs.pop('bg_color')


class TableSectionButton(ColoredButton):
    def __init__(self, **kwargs):
        super(TableSectionButton, self).__init__(**kwargs)
        self.table_section_id = kwargs.pop('table_section_id')

    def get_table_section_id(self):
        return self.table_section_id


class ModuleButton(ColoredButton):
    def __init__(self, **kwargs):
        super(ModuleButton, self).__init__(**kwargs)
        self.module_id = kwargs.pop('module_id')

    def get_module_id(self):
        return self.module_id


class ConnectionModuleButton(ModuleButton):
    def __init__(self, **kwargs):
        super(ConnectionModuleButton, self).__init__(**kwargs)
        self.transition_side = kwargs.pop('transition_side')

    def get_transition_side(self):
        return self.transition_side

class RebootButton(Button):
    def __init__(self, **kwargs):
        super(RebootButton, self).__init__(**kwargs)


class ColorChangeButton(Button):
    def __init__(self, **kwargs):
        super(ColorChangeButton, self).__init__(**kwargs)


class FlowSegmentWidget(Widget):
    def __init__(self, **kwargs):
        super(FlowSegmentWidget, self).__init__(**kwargs)
        self.color = Color(0.5, 0.5, 0.5)
        self.points = kwargs.pop('points')
        self.width = kwargs.pop('width')
        self.flow_id = kwargs.pop('flow_id')
        self.table_section_id = -1

        """Line buffer for detecting touch on the lines. Higher is less accurate."""
        self.line_buffer = 10

        """A flow is enabled by default"""
        self.disabled = False

        self.line = Line(points=self.points, width=self.width)
        self.update_canvas()

    def set_color(self, color):
        self.color = color
        self.update_canvas()

    def set_table_section_id(self, id):
        self.table_section_id = id

    def update_canvas(self):
        self.canvas.clear()
        if self.disabled:
            self.canvas.add(Color(0.5, 0.5, 0.5))
        else:
            self.canvas.add(self.color)
        self.canvas.add(self.line)

    def on_touch_down(self, touch):
        """Ignore the touch if the user didn't touch this widget"""
        if not self.collide_point(*touch.pos):
            return False

        """Calculate the distance between the touch and the first point of the line"""
        distance_1 = Vector((touch.x, touch.y)).distance((self.points[0], self.points[1]))

        """Calculate the distance between the touch and the second point of the line"""
        distance_2 = Vector((touch.x, touch.y)).distance((self.points[2], self.points[3]))

        distance_total = distance_1 + distance_2
        self.size = (distance_1, distance_2)
        line_length = Vector((self.points[0], self.points[1])).distance((self.points[2], self.points[3]))

        """If the sum of the distance between the touch and each line point is greater than the length of the line,
            the user touched the line"""
        if line_length - self.line_buffer <= distance_total <= line_length + self.line_buffer:
            self.disabled = not self.disabled
            self.update_canvas()
            if self.table_section_id != -1 and self.parent is not None:
                s_message = SmartMessage(MessageTypes.FLOW_DISABLED, (self.table_section_id, self.flow_id, self.disabled))
                """Parent is FloatLayout -> parent is BoxLayout -> parent is ModuleOverviewScreen"""
                self.parent.parent.parent.gui.add_message_func(s_message)
            return True
        return False


class CustomScreen(Screen):
    """This screen clears all widgets of the current grid when exiting"""
    def __init__(self, **kwargs):
        super(CustomScreen, self).__init__(**kwargs)
        self.gui = kwargs.pop('gui')

    def on_leave(self, *args):
        self.ids.grid.clear_widgets()


class TableSectionOverviewScreen(CustomScreen):
    """This screen draws a button for each Table Section"""
    def on_pre_enter(self):
        """
        
        """
        table_sections = self.gui.smart_grid_table.get_table_sections()

        if len(table_sections) is 0:
            # No Table Sections
            return

        single_tables = []
        tables_with_neighbors = []

        # Create list of singles and non-singles
        for table_section in table_sections:
            neighbors = table_section.get_neighbors()
            is_single = True
            for side, neighbor in neighbors.iteritems():
                if neighbor is not None:
                    is_single = False
            if is_single:
                single_tables.append(table_section)
            else:
                tables_with_neighbors.append(table_section)

        # Create array for the table clusters
        table_clusters = []
        for table_section in tables_with_neighbors:
            # Continue if Table Section already present in a cluster
            if any(any(table_section in row for row in cluster) for cluster in table_clusters):
                continue

            table_cluster = create_table_cluster(table_section, cropped=True)
            table_clusters.append(table_cluster)

        has_clusters = len(table_clusters) > 0

        max_table_sections = 6

        max_width = max_table_sections + ((max_table_sections / 2) - 1)
        max_height = max_table_sections + 1

        full_grid = [[0 for x in range(max_width)] for y in range(max_height)]

        next_x = 0

        for c in table_clusters:
            fill_grid_with_cluster(full_grid, c, next_x, 0)
            next_x = next_x + len(c[0]) + 1

        next_x = 0
        next_y = max(len(c) for c in table_clusters) + 1 if has_clusters else 0

        for st in single_tables:
            full_grid[next_y][next_x] = st
            if has_clusters:
                next_x += 2
            else:
                next_x = (next_x + 2) % 6
                if next_x is 0:
                    next_y += 1
                    next_x += 1

        # Crop full grid
        full_grid = crop_array(np.array(full_grid), min_x=2, min_y=2)

        # Calculate button width and height
        grid_height = 400.0
        grid_width = 800.0
        button_width = grid_width / len(full_grid[0])
        button_height = grid_height / len(full_grid)
        size_hint=(button_width / grid_width, button_height / grid_height)

        # For each table section in grid, create button
        for (x,y), table_section in np.ndenumerate(full_grid):
            if isinstance(table_section, TableSection):
                table_section_id = table_section.get_id()
                pos = (y * button_width, (len(full_grid) - 1 - x) * button_height)
                button = TableSectionButton(text='Table Section {0}'.format(table_section_id), table_section_id=table_section_id,
                                        bg_color=Voltages.enum_to_color(table_section.get_voltage()), pos=pos,
                                        size_hint=size_hint)
                button.bind(on_press=self.gui.set_module_overview)
                self.ids.grid.add_widget(button)


class ModuleOverviewScreen(CustomScreen):
    """This screen draws a button for each placed module including transformers. If there are places with no
    placed module, this screen draws a disabled button."""
    def __init__(self, **kwargs):
        super(ModuleOverviewScreen, self).__init__(**kwargs)
        self.modules = []
        self.table_section_id = -1
        self.btn_size_hint = 0.2
        self.button_margin = 30
        self.height_offset = 10
        self.grid_width = 800
        self.grid_height = 480

        """ Calculate the positions of the buttons """
        self.module_positions = [(self.button_margin, self.ids.grid.height * 0.35),

                                 (self.grid_width * self.btn_size_hint + (2 * self.button_margin),
                                  self.grid_height * 0.65),

                                 (self.grid_width - (2 * (self.grid_width * self.btn_size_hint)) - (
                                 2 * self.button_margin), self.grid_height * 0.65),

                                 (self.grid_width - (
                                 self.grid_width * self.btn_size_hint) - self.button_margin,
                                  self.grid_height * 0.35),

                                 (self.grid_width - (2 * (self.grid_width * self.btn_size_hint)) - (
                                     2 * self.button_margin), self.grid_height * 0.05),

                                 (self.grid_width * self.btn_size_hint + (2 * self.button_margin),
                                  self.grid_height * 0.05)

                                 ]

        self.draw_flow_structure()

    def update_flow_structure_color(self, voltage):
        for child in self.ids.grid.children:
            if isinstance(child, FlowSegmentWidget):
                color = Voltages.enum_to_flow_color(voltage)
                child.set_color(Color(*color))

    def update_flow_structure_table_section_id(self, id):
        for child in self.ids.grid.children:
            if isinstance(child, FlowSegmentWidget):
                child.set_table_section_id(id)

    def draw_flow_structure(self):
        """This function draws each line of the flow structure"""
        self.ids.grid.add_widget(FlowSegmentWidget(
            points=[self.module_positions[0][0] + self.grid_width * self.btn_size_hint + self.button_margin,
                    self.module_positions[0][1] + ((self.grid_height * self.btn_size_hint) / 2) - self.height_offset,
                    self.module_positions[0][0] + ((self.grid_width * self.btn_size_hint) / 2) + (
                        (self.grid_width * self.btn_size_hint) + self.button_margin),
                    self.module_positions[1][1] - self.button_margin], width=3, flow_id=0))

        self.ids.grid.add_widget(
            FlowSegmentWidget(points=[self.module_positions[0][0] + ((self.grid_width * self.btn_size_hint) / 2) + (
                (self.grid_width * self.btn_size_hint) + self.button_margin),
                         self.module_positions[1][1] - self.button_margin,
                         self.module_positions[2][0] + ((self.grid_width * self.btn_size_hint) / 2),
                         self.module_positions[2][1] - self.button_margin], width=3, flow_id=1))

        self.ids.grid.add_widget(
            FlowSegmentWidget(points=[self.module_positions[2][0] + ((self.grid_width * self.btn_size_hint) / 2),
                         self.module_positions[2][1] - self.button_margin,
                         self.module_positions[3][0] - self.button_margin,
                         self.module_positions[3][1] + (
                         (self.grid_height * self.btn_size_hint) / 2) - self.height_offset], width=3, flow_id=2))

        self.ids.grid.add_widget(FlowSegmentWidget(points=[self.module_positions[3][0] - self.button_margin,
                                              self.module_positions[3][1] + (
                                              (self.grid_height * self.btn_size_hint) / 2 - self.height_offset),
                                              self.module_positions[4][0] + (
                                              (self.grid_width * self.btn_size_hint) / 2),
                                              self.module_positions[4][1] + (self.grid_height * self.btn_size_hint) + (
                                                  self.button_margin / 2)], width=3, flow_id=3))

        self.ids.grid.add_widget(
            FlowSegmentWidget(points=[self.module_positions[5][0] + ((self.grid_width * self.btn_size_hint) / 2),
                         self.module_positions[5][1] + (self.grid_height * self.btn_size_hint) + (
                             self.button_margin / 2),
                         self.module_positions[4][0] + ((self.grid_width * self.btn_size_hint) / 2),
                         self.module_positions[4][1] + (self.grid_height * self.btn_size_hint) + (
                             self.button_margin / 2)], width=3, flow_id=4))

        self.ids.grid.add_widget(
            FlowSegmentWidget(points=[self.module_positions[5][0] + ((self.grid_width * self.btn_size_hint) / 2),
                         self.module_positions[5][1] + (self.grid_height * self.btn_size_hint) + (
                             self.button_margin / 2),
                         self.module_positions[0][0] + (self.grid_width * self.btn_size_hint) + self.button_margin,
                         self.module_positions[0][1] + (
                             (self.grid_height * self.btn_size_hint) / 2) - self.height_offset], width=3, flow_id=5))

    def on_leave(self):
        """Clear all widgets except the flows"""
        children = [child for child in self.ids.grid.children if not isinstance(child, FlowSegmentWidget)]
        self.ids.grid.clear_widgets(children)

    def on_pre_enter(self):
        """Draw the module buttons"""
        i = 0
        table_section = self.gui.smart_grid_table.get_table_section(self.table_section_id)
        if table_section:
            self.update_flow_structure_color(table_section.voltage)
            for flow in table_section.get_flows(ModuleFlowSegment):
                self.ids.grid.add_widget(self.get_module_widget(flow.get_module(False), self.module_positions[i], i))
                i += 1

    def get_module_widget(self, module, position, index):
        """If the module is a DefaultModule, return a button. If the module is a Transformer, return a button with smaller
        text due to the long names of the transformers. If there is no module placed, return a disabled button"""
        if isinstance(module, DefaultModule):
            button = ModuleButton(text=module.get_name(), module_id=module.get_id(),
                                  bg_color=Voltages.enum_to_color(module.get_voltage()), pos=position,
                                  size_hint=(self.btn_size_hint, self.btn_size_hint), font_size='13sp')
            button.bind(on_press=self.gui.set_module_configuration_screen)
            return button
        elif isinstance(module, ConnectionModule):
            transition_side = 'left' if index > 0 else 'right'
            btn = ConnectionModuleButton(text='{0}\n{1}'.format(module.get_name(), abs(module.get_power())), pos=position, pos_hint_x=None, pos_hint_y=None, module_id=module.get_id(),
                                size_hint=(self.btn_size_hint, self.btn_size_hint), font_size='10sp', transition_side=transition_side, bg_color=
                                Voltages.enum_to_color(
                                self.gui.smart_grid_table.get_table_section(self.table_section_id).get_voltage()))
            btn.bind(on_press=self.gui.set_module_overview_from_transformer)
            return btn
        else:
            btn = Button(text='No module placed', pos=position, size_hint=(self.btn_size_hint, self.btn_size_hint))
            btn.disabled = True
            return btn

    def set_table_section_id(self, id):
        self.ids.table_section_label.text = 'Table Section {0}'.format(id)
        self.modules = self.gui.smart_grid_table.get_table_section(id).get_placed_modules()
        self.table_section_id = id
        table_section = self.gui.smart_grid_table.get_table_section(id)
        voltage = table_section.get_voltage()
        self.update_flow_structure_color(voltage)
        self.update_flow_structure_table_section_id(id)


class ConfigSlider(Slider):
    def __init__(self, **kwargs):
        super(ConfigSlider, self).__init__(**kwargs)
        self.slider_id = kwargs.pop('slider_id')
        self.config_id = kwargs.pop('config_id')

    def get_slider_id(self):
        return self.slider_id

    def get_config_id(self):
        return self.config_id


class ModuleConfigurationScreen(CustomScreen):
    def __init__(self, **kwargs):
        super(ModuleConfigurationScreen, self).__init__(**kwargs)
        self.module_id = -1
        self.slider_values = []

    def get_module_id(self):
        return self.module_id

    def on_pre_enter(self, *args):
        """Clear slider values and add a slider for each configuration"""
        i = 0
        self.slider_values = []
        for config in self.gui.smart_grid_table.get_module(self.module_id).get_configurations():
            self.add_slider(config.config_type.name, config.config_type.min_value, config.config_type.max_value,
                            config.get_value(), config.config_type.id, i, config.config_type.role)
            i += 1
        self.ids.voltage_label.text = 'Voltage: {0}'.format(
            Voltages.enum_to_str(self.gui.smart_grid_table.get_module(self.module_id).get_voltage()))

    def role_to_grid(self, role):
        """Get the consumption/production grid name which is defined in the .kv file"""
        if role is Roles.CONSUMPTION:
            return self.ids.consumption_grid
        elif role is Roles.PRODUCTION:
            return self.ids.production_grid
        raise Exception('Cannot convert this to grid')

    def add_slider(self, label_str, min, max, current, config_id, slider_id, role):
        grid = self.role_to_grid(role)
        slider = ConfigSlider(min=min, max=max, value=current, step=10, config_id=config_id, slider_id=slider_id,
                              size_hint_x=3)
        slider.bind(value=self.gui.on_slider_change)
        self.slider_values.append(Label(text=str(int(slider.value))))
        grid.add_widget(Label(text=label_str))
        grid.add_widget(Label(text=str(int(slider.min))))
        grid.add_widget(slider)
        grid.add_widget(Label(text=str(int(slider.max))))
        grid.add_widget(self.slider_values[slider_id])

    def set_slider_value(self, value, slider_id):
        self.slider_values[slider_id].text = value

    def set_module_id(self, id):
        self.module_id = id
        self.ids.module_label.text = 'Module {0}: {1}'.format(id,
            self.gui.smart_grid_table.get_module(self.module_id).get_name())

    def on_leave(self, *args):
        self.ids.production_grid.clear_widgets()
        self.ids.consumption_grid.clear_widgets()


class ConfigurationScreen(CustomScreen):
    def on_pre_enter(self):
        pass

    def on_leave(self):
        pass


class ColorChangeScreen(CustomScreen):
    def on_pre_enter(self):
        r, g, b = COLOR_DICT[self.color_id]["color"][0], COLOR_DICT[self.color_id]["color"][1], COLOR_DICT[self.color_id]["color"][2]
        # Set slider values
        self.ids.R.value = r
        self.ids.G.value = g
        self.ids.B.value = b
        # Set screen title name
        self.ids.screen_title.text = 'Change {0} color'.format(COLOR_DICT[self.color_id]["name"])

    def on_leave(self):
        pass

    def set_color_id(self, id):
        self.color_id = id

    def confirm_color(self):
        COLOR_DICT[self.color_id]["color"] = (self.ids.R.value, self.ids.G.value, self.ids.B.value, 1.0)
        r, g, b = (int(self.ids.R.value * 255)), (int(self.ids.G.value * 255)), (int(self.ids.B.value * 255))
        rgb = hexify(r) + hexify(g) + hexify(b)
        self.gui.add_message_func(SmartMessage(MessageTypes.COLOR_CHANGED, (COLOR_DICT[self.color_id]["id"], rgb)))



if __name__ == '__main__':
    """Add a test population and run the gui"""
    def a(b):
        print b
    smart_grid_table = SmartGridTable()
    for i in range(1,4):
        smart_grid_table.table_connected(i, 1, 1)
    smart_grid_table.table_neighbor_changed(2, 0, 2090825840)
    smart_grid_table.table_neighbor_changed(1, 0, 1945993616)
    smart_grid_table.module_placed(1, 1, 439560267)
    smart_grid_table.module_placed(1, 2, 441033275)
    smart_grid_table.module_placed(3, 1, 448705851)
    smart_grid_table.module_placed(3, 0, 1945699104)
    smart_grid_table.module_placed(2, 0, 1947440355)
    smart_grid_table.get_flow_configurations()
    gui = Gui(smart_grid_table, a)
    gui.run()
