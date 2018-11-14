# coding: utf-8

import os
import sys

sys.path.extend(['.', ])

try:
    from Tkinter import *
except:
    from tkinter import *


INSTANCES_PER_WIDTH = 3
INSTANCES_PER_HEIGHT = 3


def get_fab_tasks():
    c = os.popen('fab --shortlist')
    return [i.replace(u'\n', u'') for i in c.readlines()]


def get_instances():
    import fabfile
    return fabfile.env['roledefs'].keys()


def split_list_in_blocks(_list, _size):
    return [_list[i:i + _size] for i in xrange(0, len(_list), _size)]


class FabTaskFrame(Frame):
    def __init__(self, parent, task_options, host_name, **kwargs):
        if len(task_options) == 0:
            raise ValueError(u'Task list empty')

        kwargs.setdefault('highlightthickness', 2)

        self.task_options = task_options
        Frame.__init__(self, parent, **kwargs)

        self.top_frame = Frame(self)
        self.top_frame.grid(row=1, column=0, sticky='nsew')

        self.selected_task = StringVar(self.top_frame)
        self.selected_task.set(self.task_options[0])
        self.task_combobox = OptionMenu(self.top_frame,
                                        self.selected_task,
                                        *self.task_options)
        self.task_combobox['font'] = ('TkDefaultFont', 5)
        self.task_combobox.grid(row=0, column=0)

        self.run_button = Button(self.top_frame,
                                 text=u'RUN',
                                 font=('TkDefaultFont', 5))
        self.run_button.grid(row=0, column=1)

        self.label = Label(self,
                           text=host_name,
                           anchor='w',
                           font=('TkDefaultFont', 8, 'bold'))
        self.label.grid(row=0, column=0, sticky='nwes')

        self.stop_button = Button(self.top_frame,
                                  text=u'\u25CF',
                                  font=('TkDefaultFont', 5),
                                  state=u'disable')
        self.stop_button.grid(row=0, column=3)

        self.disable_button = Button(self.top_frame,
                                     text=u'ENABLE',
                                     font=('TkDefaultFont', 5))
        self.disable_button.grid(row=0, column=4)

        self.see_button = Button(self.top_frame,
                                 text=u'DETAILS',
                                 font=('TkDefaultFont', 5))
        self.see_button.grid(row=0, column=5)

        self.text = Text(self,
                         font=('TkDefaultFont', 8),
                         width=50,
                         height=12)
        self.text.grid(row=2, column=0, sticky='we')
        self.write('disable')

    def write(self, text):
        self.text['state'] = 'normal'
        self.text.insert('end', text)
        self.text['state'] = 'disable'

    def mark_warning(self):
        self.config(highlightbackground='#d35400')

    def mark_success(self):
        self.config(highlightbackground='#27ae60')

    def mark_error(self):
        self.config(highlightbackground='#c0392b')


class InstancesFrame(Frame):
    def __init__(self, parent, instances):
        Frame.__init__(self, parent)

        column_counter = 0
        line_counter = 0
        for role in instances:
            FabTaskFrame(
                self,
                get_fab_tasks(),
                role
            ).grid(
                row=line_counter,
                column=column_counter,
                sticky='nwes',
                pady=2, padx=2)
            column_counter += 1
            if column_counter >= INSTANCES_PER_WIDTH:
                column_counter = 0
                line_counter += 1


class MainWindow(Tk):
    def __init__(self, instances=[], param=u'-H'):
        Tk.__init__(self)
        self.fabric_tasks = get_fab_tasks()
        if not self.fabric_tasks:
            raise RuntimeError(u'Fabric configured?')

        self.title(u'ParallelFab')
        self.bind('<Escape>', lambda e: self.destroy(), '+')

        self.selected_task = StringVar(self)
        self.selected_task.set(self.fabric_tasks[0])

        self.left_arrow = Button(self, text=u'\u2770')
        self.left_arrow.grid(row=1, column=0, sticky='ns', pady=5, padx=5)
        self.left_arrow['command'] = self.__left_button_handler

        self.right_arrow = Button(self, text=u'\u2771')
        self.right_arrow.grid(row=1, column=2, sticky='ns', pady=5, padx=5)
        self.right_arrow['command'] = self.__right_button_handler

        self.top_frame = Frame(self, bd=2, relief='groove')
        self.top_frame.grid(row=0,
                            column=0,
                            columnspan=3,
                            sticky='nwes',
                            pady=5,
                            padx=10)

        self.status_label = Label(self,
                                  text=u'',
                                  anchor='w')
        self.status_label.grid(row=2, column=0, columnspan=3, sticky='nwes')

        self.task_combobox = OptionMenu(self.top_frame,
                                        self.selected_task,
                                        *self.fabric_tasks)
        self.task_combobox['font'] = ('TkDefaultFont', 5)
        self.task_combobox.pack(side='left')

        self.run_button = Button(self.top_frame,
                                 text=u'RUN',
                                 font=('TkDefaultFont', 5))
        self.run_button.pack(side='left')

        self.about_button = Button(self.top_frame,
                                   text=u'about',
                                   font=('TkDefaultFont', 5))
        self.about_button.pack(side=u'right')

        self.settings_button = Button(self.top_frame,
                                      text=u'SETTINGS',
                                      font=('TkDefaultFont', 5))
        self.settings_button.pack(side=u'right')

        self.middle_frame = Frame(self, bd=2, relief='groove')
        self.middle_frame.grid(row=1, column=1, pady=5, padx=10, sticky='nwes')

        self.pages = []
        self.current_page = 0

        blocks = split_list_in_blocks(
            get_instances(), INSTANCES_PER_WIDTH * INSTANCES_PER_HEIGHT)
        for instance_group in blocks:
            print(u'Generating', instance_group)
            frame = InstancesFrame(
                self.middle_frame, instance_group)
            self.pages.append(frame)
        self.pages[0].grid(sticky='nwes')
        self.resizable(0, 0)
        self.status_label['text'] = self.get_status_label()

    def get_status_label(self):
        return u'NUM PAGES: {}\tACTUAL PAGE: {}\tSUCCESS: {}\tERRORS: {}'.format(len(self.pages), self.current_page, 0, 0)

    def __left_button_handler(self):
        if len(self.pages) <= 1:
            return

        self.pages[self.current_page].grid_forget()

        self.current_page -= 1
        if self.current_page <= -1:
            self.current_page = len(self.pages) - 1

        self.pages[self.current_page].grid(sticky='nwes')
        self.status_label['text'] = self.get_status_label()

    def __right_button_handler(self):
        if len(self.pages) <= 1:
            return

        self.pages[self.current_page].grid_forget()

        self.current_page += 1
        if self.current_page >= len(self.pages):
            self.current_page = 0

        self.pages[self.current_page].grid(sticky='nwes')
        self.status_label['text'] = self.get_status_label()

if __name__ == u'__main__':
    top = MainWindow()
    top.mainloop()
