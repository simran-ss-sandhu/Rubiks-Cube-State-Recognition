import tkinter as tk
import logging
from PIL import Image, ImageTk
import cv2 as cv
import threading
from rubiks_cube_state_recognition.cube_state.CubeState import CubeFace
from rubiks_cube_state_recognition.cube_capture.CubeStateFinder import CubeStateFinder
from rubiks_cube_state_recognition.solution_finder.ThistlethwaiteSolver import ThistlethwaiteSolver

logging.basicConfig(level=logging.INFO, format="|%(asctime)s|%(name)s|%(levelname)s| %(message)s")

# colours that will be used in the program
COLOURS = {'light_grey': '#c3c3c3',
           'dark_grey': '#1d1d1d',
           'grey1': '#1e1e1e',  # darkest grey
           'grey2': '#252526',
           'grey3': '#333333',
           'grey4': '#3c3c3c',  # lightest grey
           None: '#c3c3c3',  # default cube tile colour
           'w': 'white',
           'g': 'green',
           'r': 'red',
           'b': 'blue',
           'o': 'orange',
           'y': 'yellow'}

# the pages background colour
PAGES_BACKGROUND = COLOURS['light_grey']
CONTAINERS_BACKGROUND = COLOURS['grey3']
cube_state_finder = CubeStateFinder()
thistlethwaite_solver = ThistlethwaiteSolver()
solution = []


class GuiBase(tk.Tk):
    def __init__(self):
        super().__init__()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.title("Rubik's Cube Solver")  # the title of the window
        self.geometry('1280x720')  # sets the windows size

        navigation_menu_container = tk.Frame(master=self, background=COLOURS['grey1'])
        navigation_menu_container.grid(column=0, row=0, sticky='ns')
        navigation_menu_container.grid_columnconfigure(0, weight=1)
        for row_index in range(0, 12):
            navigation_menu_container.grid_rowconfigure(row_index, weight=1)

        pages_container = tk.Frame(master=self, background=PAGES_BACKGROUND)
        pages_container.grid(column=1, row=0, sticky='nsew')
        pages_container.grid_columnconfigure(0, weight=1)
        pages_container.grid_rowconfigure(0, weight=1)

        self.capture_page_button = tk.Button(
            master=navigation_menu_container,
            text='Capture',
            command=lambda: self.show_frame(CapturePage, self.capture_page_button))
        self.capture_page_button.grid(column=0, row=0, sticky='nsew')

        self.solution_page_button = tk.Button(
            master=navigation_menu_container,
            text='Solution',
            command=lambda: self.show_frame(SolutionPage, self.solution_page_button))
        self.solution_page_button.grid(column=0, row=1, sticky='nsew')

        self.settings_page_button = tk.Button(
            master=navigation_menu_container,
            text='Settings',
            command=lambda: self.show_frame(SettingsPage, self.settings_page_button))
        self.settings_page_button.grid(column=0, row=10, sticky='nsew')

        self.tutorial_page_button = tk.Button(
            master=navigation_menu_container,
            text='Tutorial',
            command=lambda: self.show_frame(TutorialPage, self.tutorial_page_button))
        self.tutorial_page_button.grid(column=0, row=11, sticky='nsew')

        for page_button in [self.capture_page_button, self.solution_page_button, self.settings_page_button,
                            self.tutorial_page_button]:
            page_button.configure(
                relief='flat',
                background=COLOURS['grey2'],
                foreground='black',
                activebackground='black',
                activeforeground='white')

        self.frames = {}
        for Page in (CapturePage, SolutionPage, SettingsPage, TutorialPage):
            frame = Page(parent=pages_container, controller=self)
            frame.grid(row=0, column=0, sticky='nsew')
            self.frames[Page] = frame

        self.show_frame(CapturePage, self.capture_page_button)  # sets the capture page as the default page

    def show_frame(self, page, page_button):
        for button in [self.capture_page_button, self.solution_page_button, self.settings_page_button,
                       self.tutorial_page_button]:
            button.configure(relief='flat')
        page_button.configure(relief='solid')
        frame = self.frames[page]
        frame.tkraise()


class CapturePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, master=parent, background=PAGES_BACKGROUND)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.colour_grid_chosen_colour = COLOURS['grey4']

        self.camera_feed = tk.Label(master=self)
        self.camera_feed.grid(column=0, row=0)

        # Bind a resize event to handle dynamic resizing
        self.frame_width = 640  # initial value
        self.frame_height = 360  # initial value
        self.bind("<Configure>", self.on_resize)

        right_container = tk.Frame(master=self, background=PAGES_BACKGROUND)
        right_container.grid(column=1, row=0)
        right_container.grid_columnconfigure(0, weight=1)
        right_container.grid_columnconfigure(1, weight=1)

        cube_state_diagram_container = tk.Frame(master=right_container, background=PAGES_BACKGROUND)
        cube_state_diagram_container.grid(column=0, columnspan=2, row=0, pady=10)
        for column_index in range(12):
            cube_state_diagram_container.grid_columnconfigure(column_index, weight=1)
        for row_index in range(9):
            cube_state_diagram_container.grid_rowconfigure(row_index, weight=1)

        colour_grid_container = tk.Frame(master=right_container)
        colour_grid_container.grid(column=0, row=1, pady=10)

        self.solve_button = tk.Label(
            master=right_container,
            font=('Calibri', 30),
            width=10,
            relief='solid',
            foreground='white')
        self.solve_button.bind('<Button-1>', lambda event: threading.Thread(target=self.find_solution, daemon=True).start())
        self.solve_button.grid(column=1, row=1, padx=(10, 0))

        w_tl = tk.Label(master=cube_state_diagram_container)
        w_tl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(w_tl, 'w_face', 'tl'))
        w_tl.grid(column=3, row=0, sticky='nsew')
        w_tm = tk.Label(master=cube_state_diagram_container)
        w_tm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(w_tm, 'w_face', 'tm'))
        w_tm.grid(column=4, row=0, sticky='nsew')
        w_tr = tk.Label(master=cube_state_diagram_container)
        w_tr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(w_tr, 'w_face', 'tr'))
        w_tr.grid(column=5, row=0, sticky='nsew')
        w_ml = tk.Label(master=cube_state_diagram_container)
        w_ml.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(w_ml, 'w_face', 'ml'))
        w_ml.grid(column=3, row=1, sticky='nsew')
        w_c = tk.Label(master=cube_state_diagram_container, text='W', width=3, height=2, relief='solid', background='white')
        w_c.grid(column=4, row=1, sticky='nsew')
        w_mr = tk.Label(master=cube_state_diagram_container)
        w_mr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(w_mr, 'w_face', 'mr'))
        w_mr.grid(column=5, row=1, sticky='nsew')
        w_bl = tk.Label(master=cube_state_diagram_container)
        w_bl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(w_bl, 'w_face', 'bl'))
        w_bl.grid(column=3, row=2, sticky='nsew')
        w_bm = tk.Label(master=cube_state_diagram_container)
        w_bm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(w_bm, 'w_face', 'bm'))
        w_bm.grid(column=4, row=2, sticky='nsew')
        w_br = tk.Label(master=cube_state_diagram_container)
        w_br.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(w_br, 'w_face', 'br'))
        w_br.grid(column=5, row=2, sticky='nsew')

        g_tl = tk.Label(master=cube_state_diagram_container)
        g_tl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(g_tl, 'g_face', 'tl'))
        g_tl.grid(column=0, row=3, sticky='nsew')
        g_tm = tk.Label(master=cube_state_diagram_container)
        g_tm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(g_tm, 'g_face', 'tm'))
        g_tm.grid(column=1, row=3, sticky='nsew')
        g_tr = tk.Label(master=cube_state_diagram_container)
        g_tr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(g_tr, 'g_face', 'tr'))
        g_tr.grid(column=2, row=3, sticky='nsew')
        g_ml = tk.Label(master=cube_state_diagram_container)
        g_ml.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(g_ml, 'g_face', 'ml'))
        g_ml.grid(column=0, row=4, sticky='nsew')
        g_c = tk.Label(master=cube_state_diagram_container, text='G', width=3, height=2, relief='solid', background='green')
        g_c.grid(column=1, row=4, sticky='nsew')
        g_mr = tk.Label(master=cube_state_diagram_container)
        g_mr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(g_mr, 'g_face', 'mr'))
        g_mr.grid(column=2, row=4, sticky='nsew')
        g_bl = tk.Label(master=cube_state_diagram_container)
        g_bl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(g_bl, 'g_face', 'bl'))
        g_bl.grid(column=0, row=5, sticky='nsew')
        g_bm = tk.Label(master=cube_state_diagram_container)
        g_bm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(g_bm, 'g_face', 'bm'))
        g_bm.grid(column=1, row=5, sticky='nsew')
        g_br = tk.Label(master=cube_state_diagram_container)
        g_br.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(g_br, 'g_face', 'br'))
        g_br.grid(column=2, row=5, sticky='nsew')

        r_tl = tk.Label(master=cube_state_diagram_container)
        r_tl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(r_tl, 'r_face', 'tl'))
        r_tl.grid(column=3, row=3, sticky='nsew')
        r_tm = tk.Label(master=cube_state_diagram_container)
        r_tm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(r_tm, 'r_face', 'tm'))
        r_tm.grid(column=4, row=3, sticky='nsew')
        r_tr = tk.Label(master=cube_state_diagram_container)
        r_tr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(r_tr, 'r_face', 'tr'))
        r_tr.grid(column=5, row=3, sticky='nsew')
        r_ml = tk.Label(master=cube_state_diagram_container)
        r_ml.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(r_ml, 'r_face', 'ml'))
        r_ml.grid(column=3, row=4, sticky='nsew')
        r_c = tk.Label(master=cube_state_diagram_container, text='R', width=3, height=2, relief='solid', background='red')
        r_c.grid(column=4, row=4, sticky='nsew')
        r_mr = tk.Label(master=cube_state_diagram_container)
        r_mr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(r_mr, 'r_face', 'mr'))
        r_mr.grid(column=5, row=4, sticky='nsew')
        r_bl = tk.Label(master=cube_state_diagram_container)
        r_bl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(r_bl, 'r_face', 'bl'))
        r_bl.grid(column=3, row=5, sticky='nsew')
        r_bm = tk.Label(master=cube_state_diagram_container)
        r_bm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(r_bm, 'r_face', 'bm'))
        r_bm.grid(column=4, row=5, sticky='nsew')
        r_br = tk.Label(master=cube_state_diagram_container)
        r_br.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(r_br, 'r_face', 'br'))
        r_br.grid(column=5, row=5, sticky='nsew')

        b_tl = tk.Label(master=cube_state_diagram_container)
        b_tl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(b_tl, 'b_face', 'tl'))
        b_tl.grid(column=6, row=3, sticky='nsew')
        b_tm = tk.Label(master=cube_state_diagram_container)
        b_tm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(b_tm, 'b_face', 'tm'))
        b_tm.grid(column=7, row=3, sticky='nsew')
        b_tr = tk.Label(master=cube_state_diagram_container)
        b_tr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(b_tr, 'b_face', 'tr'))
        b_tr.grid(column=8, row=3, sticky='nsew')
        b_ml = tk.Label(master=cube_state_diagram_container)
        b_ml.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(b_ml, 'b_face', 'ml'))
        b_ml.grid(column=6, row=4, sticky='nsew')
        b_c = tk.Label(master=cube_state_diagram_container, text='B', width=3, height=2, relief='solid', background='blue')
        b_c.grid(column=7, row=4, sticky='nsew')
        b_mr = tk.Label(master=cube_state_diagram_container)
        b_mr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(b_mr, 'b_face', 'mr'))
        b_mr.grid(column=8, row=4, sticky='nsew')
        b_bl = tk.Label(master=cube_state_diagram_container)
        b_bl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(b_bl, 'b_face', 'bl'))
        b_bl.grid(column=6, row=5, sticky='nsew')
        b_bm = tk.Label(master=cube_state_diagram_container)
        b_bm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(b_bm, 'b_face', 'bm'))
        b_bm.grid(column=7, row=5, sticky='nsew')
        b_br = tk.Label(master=cube_state_diagram_container)
        b_br.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(b_br, 'b_face', 'br'))
        b_br.grid(column=8, row=5, sticky='nsew')

        o_tl = tk.Label(master=cube_state_diagram_container)
        o_tl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(o_tl, 'o_face', 'tl'))
        o_tl.grid(column=9, row=3, sticky='nsew')
        o_tm = tk.Label(master=cube_state_diagram_container)
        o_tm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(o_tm, 'o_face', 'tm'))
        o_tm.grid(column=10, row=3, sticky='nsew')
        o_tr = tk.Label(master=cube_state_diagram_container)
        o_tr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(o_tr, 'o_face', 'tr'))
        o_tr.grid(column=11, row=3, sticky='nsew')
        o_ml = tk.Label(master=cube_state_diagram_container)
        o_ml.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(o_ml, 'o_face', 'ml'))
        o_ml.grid(column=9, row=4, sticky='nsew')
        o_c = tk.Label(master=cube_state_diagram_container, text='O', width=3, height=2, relief='solid', background='orange')
        o_c.grid(column=10, row=4, sticky='nsew')
        o_mr = tk.Label(master=cube_state_diagram_container)
        o_mr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(o_mr, 'o_face', 'mr'))
        o_mr.grid(column=11, row=4, sticky='nsew')
        o_bl = tk.Label(master=cube_state_diagram_container)
        o_bl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(o_bl, 'o_face', 'bl'))
        o_bl.grid(column=9, row=5, sticky='nsew')
        o_bm = tk.Label(master=cube_state_diagram_container)
        o_bm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(o_bm, 'o_face', 'bm'))
        o_bm.grid(column=10, row=5, sticky='nsew')
        o_br = tk.Label(master=cube_state_diagram_container)
        o_br.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(o_br, 'o_face', 'br'))
        o_br.grid(column=11, row=5, sticky='nsew')

        y_tl = tk.Label(master=cube_state_diagram_container)
        y_tl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(y_tl, 'y_face', 'tl'))
        y_tl.grid(column=3, row=6, sticky='nsew')
        y_tm = tk.Label(master=cube_state_diagram_container)
        y_tm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(y_tm, 'y_face', 'tm'))
        y_tm.grid(column=4, row=6, sticky='nsew')
        y_tr = tk.Label(master=cube_state_diagram_container)
        y_tr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(y_tr, 'y_face', 'tr'))
        y_tr.grid(column=5, row=6, sticky='nsew')
        y_ml = tk.Label(master=cube_state_diagram_container)
        y_ml.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(y_ml, 'y_face', 'ml'))
        y_ml.grid(column=3, row=7, sticky='nsew')
        y_c = tk.Label(master=cube_state_diagram_container, text='Y', width=3, height=2, relief='solid', background='yellow')
        y_c.grid(column=4, row=7, sticky='nsew')
        y_mr = tk.Label(master=cube_state_diagram_container)
        y_mr.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(y_mr, 'y_face', 'mr'))
        y_mr.grid(column=5, row=7, sticky='nsew')
        y_bl = tk.Label(master=cube_state_diagram_container)
        y_bl.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(y_bl, 'y_face', 'bl'))
        y_bl.grid(column=3, row=8, sticky='nsew')
        y_bm = tk.Label(master=cube_state_diagram_container)
        y_bm.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(y_bm, 'y_face', 'bm'))
        y_bm.grid(column=4, row=8, sticky='nsew')
        y_br = tk.Label(master=cube_state_diagram_container)
        y_br.bind("<Button-1>", lambda event: self.set_cube_tile_state_colour(y_br, 'y_face', 'br'))
        y_br.grid(column=5, row=8, sticky='nsew')

        self.cube_state_diagram_buttons = [w_tl, w_tm, w_tr, w_ml, w_mr, w_bl, w_bm, w_br,
                                           g_tl, g_tm, g_tr, g_ml, g_mr, g_bl, g_bm, g_br,
                                           r_tl, r_tm, r_tr, r_ml, r_mr, r_bl, r_bm, r_br,
                                           b_tl, b_tm, b_tr, b_ml, b_mr, b_bl, b_bm, b_br,
                                           o_tl, o_tm, o_tr, o_ml, o_mr, o_bl, o_bm, o_br,
                                           y_tl, y_tm, y_tr, y_ml, y_mr, y_bl, y_bm, y_br]

        for cube_state_diagram_button in self.cube_state_diagram_buttons:
            cube_state_diagram_button.configure(
                width=3,
                height=2,
                relief='solid',
                background=COLOURS['light_grey'])

        self.red_button = tk.Label(
            master=colour_grid_container,
            text='R',
            foreground='pink',
            background='red')
        self.red_button.bind("<Button-1>", lambda event: self.set_colour_grid_chosen_colour('red', self.red_button))
        self.red_button.grid(column=0, row=0)

        self.blue_button = tk.Label(
            master=colour_grid_container,
            text='B',
            foreground='light blue',
            background='blue')
        self.blue_button.bind("<Button-1>", lambda event: self.set_colour_grid_chosen_colour('blue', self.blue_button))
        self.blue_button.grid(column=1, row=0)

        self.yellow_button = tk.Label(
            master=colour_grid_container,
            text='Y',
            foreground='black',
            background='yellow')
        self.yellow_button.bind("<Button-1>", lambda event: self.set_colour_grid_chosen_colour('yellow', self.yellow_button))
        self.yellow_button.grid(column=2, row=0)

        self.orange_button = tk.Label(
            master=colour_grid_container,
            text='O',
            foreground='yellow',
            background='orange')
        self.orange_button.bind("<Button-1>", lambda event: self.set_colour_grid_chosen_colour('orange', self.orange_button))
        self.orange_button.grid(column=0, row=1)

        self.green_button = tk.Label(
            master=colour_grid_container,
            text='G',
            foreground='light green',
            background='green')
        self.green_button.bind("<Button-1>", lambda event: self.set_colour_grid_chosen_colour('green', self.green_button))
        self.green_button.grid(column=1, row=1)

        self.white_button = tk.Label(
            master=colour_grid_container,
            text='W',
            foreground='black',
            background='white')
        self.white_button.bind("<Button-1>", lambda event: self.set_colour_grid_chosen_colour('white', self.white_button))
        self.white_button.grid(column=2, row=1)

        for colour_grid_button in [self.red_button, self.blue_button, self.yellow_button, self.orange_button,
                                   self.green_button, self.white_button]:
            colour_grid_button.configure(
                font=("Calibri", 25),
                width=3,
                height=1,
                borderwidth=5,
                relief='flat')

        self.capture_loop()

    def update_cube_state(self):
        cube_state_finder.update_cube_state()
        index = 0
        for face_name in ['w_face', 'g_face', 'r_face', 'b_face', 'o_face', 'y_face']:
            cube_face_state = cube_state_finder.cube_state.__getattribute__(face_name)
            if cube_face_state is not None:
                for tile_name in ['tl', 'tm', 'tr', 'ml', 'mr', 'bl', 'bm', 'br']:
                    tile_colour = COLOURS[cube_face_state.__getattribute__(tile_name)]
                    self.cube_state_diagram_buttons[index].configure(background=tile_colour)
                    index += 1
            else:
                index += 8

    def on_resize(self, event):
        self.frame_width = event.width
        self.frame_height = event.height

    def capture_loop(self):
        self.update_cube_state()
        if cube_state_finder.cube_state.is_valid():
            if not cube_state_finder.cube_state.is_solved() and self.solve_button['background'] == 'red':
                self.solve_button.configure(
                    text='SOLVE',
                    background='green')
        else:
            self.solve_button.configure(
                text='SOLVE',
                background='red')
        # makes frame tkinter compatible
        frame = cube_state_finder.video_feed.frame
        while frame is None:
            cube_state_finder.video_feed.update_frame()
            frame = cube_state_finder.video_feed.frame
        frame = cv.resize(frame, (int(self.frame_width * 1 / 2), int(self.frame_height * 1 / 2)))
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        frame = Image.fromarray(frame)
        tk_frame = ImageTk.PhotoImage(image=frame)

        # updates camera feed with the current frame
        self.camera_feed.imgtk = tk_frame
        self.camera_feed.configure(image=tk_frame)
        self.camera_feed.after(ms=1, func=self.capture_loop)

    def set_colour_grid_chosen_colour(self, colour, chosen_button):
        logging.info(f"setting colour grid to {colour}")
        self.colour_grid_chosen_colour = colour
        for colour_grid_button in [self.red_button, self.blue_button, self.yellow_button, self.orange_button,
                                   self.green_button, self.white_button]:
            colour_grid_button.configure(relief='flat')
        chosen_button.configure(
            relief='solid',
            borderwidth=5)

    def set_cube_tile_state_colour(self, cube_tile_button, face_name, tile_name):
        logging.info(f"setting {tile_name} on {face_name} to {self.colour_grid_chosen_colour}")
        cube_tile_button.configure(background=self.colour_grid_chosen_colour)
        cube_face_state = cube_state_finder.cube_state.__getattribute__(face_name)
        if cube_face_state is None:
            cube_face_state = CubeFace()
            cube_face_state.c = face_name[0]
            cube_state_finder.cube_state.__setattr__(face_name, cube_face_state)
        if self.colour_grid_chosen_colour[0] != '#':
            cube_face_state.__setattr__(tile_name, self.colour_grid_chosen_colour[0])

    def find_solution(self):
        if self.solve_button['background'] != COLOURS['grey3']:
            logging.info("finding solution")
            global solution
            self.solve_button.configure(text='Finding\nSolution', background=COLOURS['grey3'])
            self.solve_button.update_idletasks()
            solution = thistlethwaite_solver.solve(cube_state_finder.cube_state)
            self.solve_button.configure(text='Solution\nFound', background=COLOURS['grey3'])
            self.solve_button.update_idletasks()
            self.solve_button.after(thistlethwaite_solver.min_group_search_time*100, lambda: self.controller.show_frame(SolutionPage, self.solve_button))


class SolutionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, master=parent, background=PAGES_BACKGROUND)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)

        top_container = tk.Frame(master=self, background=CONTAINERS_BACKGROUND)
        top_container.grid(column=0, row=0, pady=15, padx=15, sticky='nsew')
        top_container.grid_columnconfigure(0, weight=1)
        top_container.grid_columnconfigure(1, weight=2)
        top_container.grid_columnconfigure(2, weight=1)
        top_container.grid_rowconfigure(0, weight=1)

        bottom_container = tk.Frame(master=self, background=CONTAINERS_BACKGROUND)
        bottom_container.grid(column=0, row=1, pady=15, padx=15, sticky='nsew')
        for column_index in range(10):
            bottom_container.grid_columnconfigure(column_index, weight=1)
        for row_index in range(2):
            bottom_container.grid_rowconfigure(row_index, weight=1)

        self.current_move_index = 0

        self.previous_move = tk.Button(master=top_container, text='LAST', font=('Arial', 40), foreground='black',
                                       background=CONTAINERS_BACKGROUND, relief='flat', command=self.rewind)
        self.previous_move.grid(column=0, row=0)
        self.current_move = tk.Label(master=top_container, text='CURR', font=('Arial', 100), foreground='white',
                                     background=CONTAINERS_BACKGROUND)
        self.current_move.grid(column=1, row=0)
        self.next_move = tk.Button(master=top_container, text='NEXT', font=('Arial', 40), foreground='black',
                                   background=CONTAINERS_BACKGROUND, relief='flat', command=self.forward)
        self.next_move.grid(column=2, row=0)

        self.turns_names_labels = [
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container),
            tk.Label(master=bottom_container)]

        self.solution_loop()

    def solution_loop(self):
        if solution:
            if solution[0] != 'START' and solution[-1] != 'END':
                solution.insert(0, 'START')
                solution.append('END')
                self.turns_names_labels[0].configure(foreground='white')
                self.previous_move.configure(text='START')
                self.current_move.configure(text=solution[1])
                self.next_move.configure(text=solution[2])

                for column_index, turn_name_label in enumerate(self.turns_names_labels[:10]):
                    turn_name_label.grid(row=0, column=column_index)
                    turn_name_label.configure(text='', background=CONTAINERS_BACKGROUND)
                for column_index, turn_name_label in enumerate(self.turns_names_labels[10:]):
                    turn_name_label.grid(row=1, column=column_index)
                    turn_name_label.configure(text='', background=CONTAINERS_BACKGROUND)

                if len(solution) <= 11:
                    for count, turn_name in enumerate(solution[1:-1]):
                        self.turns_names_labels[count].configure(text=turn_name, font=('Arial', 40))
                else:
                    for count, turn_name in enumerate(solution[1:11]):
                        self.turns_names_labels[count].configure(text=turn_name, font=('Arial', 40))
                    for count, turn_name in enumerate(solution[11:-1]):
                        self.turns_names_labels[count + 10].configure(text=turn_name, font=('Arial', 40))
        self.previous_move.after(ms=1, func=self.solution_loop)

    def rewind(self):
        if self.current_move_index > 0:
            self.current_move_index -= 1

            self.next_move.configure(text=self.current_move['text'])
            self.current_move.configure(text=self.previous_move['text'])
            self.previous_move.configure(text=solution[self.current_move_index])

            for turn_name_label in self.turns_names_labels:
                turn_name_label.configure(foreground='black')
            self.turns_names_labels[self.current_move_index].configure(foreground='white')

    def forward(self):
        if self.current_move_index < len(solution) - 3:
            self.current_move_index += 1

            self.previous_move.configure(text=self.current_move['text'])
            self.current_move.configure(text=self.next_move['text'])
            self.next_move.configure(text=solution[self.current_move_index + 2])

            for turn_name_label in self.turns_names_labels:
                turn_name_label.configure(foreground='black')
            self.turns_names_labels[self.current_move_index].configure(foreground='white')


class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, master=parent, background=PAGES_BACKGROUND)
        self.grid_columnconfigure(0, weight=1)
        tk.Label(
            master=self,
            text='Settings Page',
            font=('Arial', 50),
            background=self['background']
        ).grid(
            column=0,
            row=0,
            sticky='nsew')

        tk.Button(master=self, text='Calibrate Filters', font=('Arial', 30),
                  command=lambda: cube_state_finder.frame_instance.calibrate_filters(cube_state_finder.video_feed)).grid(
            column=0, row=1, sticky='nsew')

        tk.Label(master=self, text='Minimum group search time (seconds):').grid(column=0, row=2, sticky='sew')
        self.min_group_search_time = tk.Scale(master=self, orient='horizontal', from_=0, to=600)
        self.min_group_search_time.set(thistlethwaite_solver.min_group_search_time)
        self.min_group_search_time.grid(column=0, row=3, sticky='nsew')

        tk.Button(master=self, text='Save\nChanges', command=self.save_changes).grid(column=0, row=4, sticky='ns')

    def save_changes(self):
        thistlethwaite_solver.min_group_search_time = self.min_group_search_time.get()
        logging.info(f"min group search time set to {self.min_group_search_time.get()}")


class TutorialPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, master=parent, background=PAGES_BACKGROUND)
        self.grid_columnconfigure(0, weight=1)
        tk.Label(
            master=self,
            text='Tutorial Page',
            font=('Arial', 50),
            background=self['background']
        ).grid(
            column=0,
            row=0)
        tutorial_text = '''
        Capture page:
        The video on the left shows the video feed.
        The image overlays show the Rubik's cubes that have been found. (The red squares indicate a cube face. The white squares indicate cube tiles.)
        The diagram on the right shows the cube state that the program has identified.
        It can be changed by using the colour grid or by using the camera.
        When using the camera, show the Rubik's cube face to the camera in the same orientation it they appears in the diagram. (For example if you need to show the red face, the white face has to be on the top side of the cube).
        To use the colour grid, click on a colour and then click on a cube tile on the diagram.
        The cube tile on the diagram will change to the colour selected on the colour grid.
        When the cube state identified could be a valid Rubik's cube the solve button will turn green and will become pressable.
        When you click the solve button, a solution will start to be searched for, for the Rubik's cube state identified.
        Once a solution has been found, the program automatically switches the current page to the solution page.

        Solution page:
        The bottom box of the screen shows the cube face turns that will solve the identified cube state.
        The bigger box on the top of the screen shows the cube face turns but magnified. It only shows the previous, current and next move.
        The current move is in white (in both the bottom and top box).
        The previous move is on the left of the zoomed-in current move. The next move is on the right of the zoomed-in current move.
        The previous and next moves on the top box are buttons.
        When you click the next move, you forward to the next move.
        When you click the previous move, you rewind back to the last move.
        You can do this to keep easy track of the move you are currently executing when following the cube face turn moves.
        When you are finished with the solution, you can use the capture page to find the solution to another Rubik's cube state.

        Settings page:
        On top is the button to calibrate the filters in the video feed that allow the Rubik's cube to be detected by the cameras.
        By calibrating the filters, it become much easier to identify Rubik's cube faces in the camera feed.
        Below it, is the minimum group search time slider.
        This is the minimum amount of time that needs to be spent in each group of cube states before moving on.
        The longer that is spent searching in one group, the higher the chance of finding a shorter solution.
        However, this is risky: it can make the search much longer or shorter and is dependent on the cube state.
        The minimum time is initially set to 30 second.
        After 30 seconds, if a new set of cube states has been found, the new group will be searched instead.
        You can use the slider to change this time. However, you have to press the save changes button below it to make sure that it takes effect.

        Calibration of filters:
        Read the tutorial for the settings page to find out what the calibration does.
        1. Press the spacebar twice to choose a frame you would like to experiment on. (this should have the Rubik's cube face on it)
           If you accidentally press the spacebar, you can press any other key to cancel the choosing process.
        2. Move the sliders until the space around the Rubik's cube tiles can be seen in white. 
           All the cube tiles should be black. You can experiment with the settings to see which works best for you.
        3. Press the spacebar twice again to confirm your changes. They will be automatically saved.
        '''
        tk.Label(master=self, text=tutorial_text).grid(column=0, row=1, sticky='ew')


def main():
    app = GuiBase()
    app.mainloop()
    cube_state_finder.video_feed.video_capture.release()


if __name__ == "__main__":
    main()
