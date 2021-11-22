import pygame
import time
import math
import os


class TreeSim:
    screen_height = 700
    screen_width = 900
    # game run flag
    running = True
    colors = {"white": [255, 255, 255],
              "black": [0, 0, 0],
              "nice blue": pygame.Color("#80D8FF"),
              "nice orange": pygame.Color("#F9A825")}
    vertex_list = []
    button_list = []
    draw_mode = "vertex"
    vertexes_selected = []
    vertexes_being_dragged = []

    def __init__(self):
        # window setup
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.fill(self.colors["white"])
        pygame.display.set_icon(self.screen)
        pygame.display.set_caption("Tree Simulator")
        self.setup_buttons()
        # run main loop
        self.main_loop()

    def draw_all(self):
        self.screen.fill(self.colors["white"])
        self.draw_all_buttons()
        self.draw_all_vertices()

    def draw_all_vertices(self):
        for vertex in self.vertex_list:
            vertex.draw()

    def draw_all_buttons(self):
        for button in self.button_list:
            button.draw()

    def setup_buttons(self):
        vb = VertexButton(self.screen, self.colors["nice blue"], 10, 10)
        lb = LineButton(self.screen, self.colors["nice blue"], 70, 10)
        db = DragButton(self.screen, self.colors["nice blue"], 130, 10)
        sb = ScreenShotButton(self.screen, self.colors["nice blue"], 400, 10)
        cb = ClearButton(self.screen, self.colors["nice blue"], 400, 10)
        sb.left = self.screen_width - sb.width - 10
        cb.left = sb.left - cb.width - 10
        self.button_list.append(vb)
        self.button_list.append(lb)
        self.button_list.append(db)
        self.button_list.append(sb)
        self.button_list.append(cb)

    def create_vertex(self, pos):
        v = Vertex(self.screen, self.colors["black"], pos)
        self.vertex_list.append(v)
        print("Drew vertex at: {}".format(v.center))

    def set_button_color_states(self):
        for button in self.button_list:
            if button.button_type == self.draw_mode:
                button.set_selected()
            elif button.button_type != self.draw_mode:
                button.set_default()

    def filepath_fixer(self, filepath, count=0):
        if os.path.exists(filepath):
            filepath = "screenshot_copy({}).jpg".format(count)
            return self.filepath_fixer(filepath, count+1)
        else:
            return filepath

    def left_click(self):
        # grab mouse position
        pos = pygame.mouse.get_pos()
        # check to see if we've clicked a button
        for button in self.button_list:
            if button.is_clicked(pos):
                self.draw_mode = button.button_type
                self.set_button_color_states()
                # if we are clicking the screenshot button
                if self.draw_mode == "screenshot":
                    filepath = self.filepath_fixer("screenshot.jpg")

                    # clear the screen, draw only vertices
                    self.screen.fill(self.colors["white"])
                    self.draw_all_vertices()
                    pygame.display.flip()

                    # take a screenshot
                    pygame.image.save(self.screen, filepath)

                    self.draw_all()
                    pygame.font.init()
                    my_font = pygame.font.SysFont("Comic Sans MS", 45)
                    text_surface = my_font.render("Screenshot saved!", True, TreeSim.colors["black"])
                    self.screen.blit(text_surface, (math.floor(self.screen_width/4), math.floor(self.screen_height/3)))
                    pygame.display.flip()
                    time.sleep(0.3)
                    print("screenshot saved!")
                elif self.draw_mode == "clear":
                    self.vertex_list = []
                    self.vertexes_selected = []
                print("Mode changed to: {}".format(self.draw_mode))
                return
        # if we're drawing vertices, draw one
        if self.draw_mode == "vertex":
            self.create_vertex(pos)
        # if we're drawing lines
        elif self.draw_mode == "line":
            # either select or unselect a vertex, if we click on it
            for vertex in self.vertex_list:
                if vertex.is_clicked(pos):
                    if vertex.selected is True:
                        vertex.set_unselected()
                    elif vertex.selected is False:
                        vertex.set_selected()
                        # if a vertex is clicked add it to the list of clicked vertices
                        self.vertexes_selected.append(vertex)
                        # if we've clicked two vertices, tell them to connect to one another
                        if len(self.vertexes_selected) == 2:
                            self.vertexes_selected[0].connected_neighbors.append(self.vertexes_selected[1])
                            self.vertexes_selected[1].connected_neighbors.append(self.vertexes_selected[0])
                            self.vertexes_selected[0].set_unselected()
                            self.vertexes_selected[1].set_unselected()
                            self.vertexes_selected = []
                    return
        elif self.draw_mode == "drag":
            if len(self.vertexes_being_dragged) > 0:
                self.vertexes_being_dragged[0].toggle_drag_mode()
                self.vertexes_being_dragged = []
            # either select or unselect a vertex, if we click on it
            for vertex in self.vertex_list:
                if vertex.is_clicked(pos):
                    if vertex.selected is True:
                        vertex.set_unselected()
                    elif vertex.selected is False:
                        vertex.set_selected()
                        vertex.toggle_drag_mode()
                        self.vertexes_being_dragged.append(vertex)

    # function that loops through pygame events to check for a close window click
    def check_events(self):
        for event in pygame.event.get():
            # close window if x clicked
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # left click
                if event.button == 1:
                    self.left_click()
                # right click
                if event.button == 3:
                    pos = pygame.mouse.get_pos()
                    if self.draw_mode == "vertex":
                        # check if we should remove a vertex
                        for vertex in self.vertex_list:
                            if vertex.is_clicked(pos):
                                for x in self.vertex_list:
                                    if vertex in x.connected_neighbors:
                                        x.connected_neighbors.remove(vertex)
                                self.vertex_list.remove(vertex)
                    elif self.draw_mode == "line":
                        pass

    # main game loop
    def main_loop(self):
        while self.running:
            self.draw_all()
            pygame.display.flip()
            self.check_events()


class Vertex:
    center: tuple
    radius = 10
    color: TreeSim.colors.values
    screen = pygame.display
    selected = False
    drag_mode = False
    connected_neighbors: list

    def __init__(self, screen, color, pos):
        self.connected_neighbors = []
        self.center = pos
        self.color = color
        self.screen = screen
        self.draw()

    def draw(self):
        if self.drag_mode is True:
            self.center = pygame.mouse.get_pos()
        pygame.draw.circle(self.screen, self.color, self.center, self.radius)

        # draw neighbor lines
        if len(self.connected_neighbors) > 0:
            for neighbor in self.connected_neighbors:
                pygame.draw.line(self.screen, TreeSim.colors["black"], self.center, neighbor.center, 5)

    def set_selected(self):
        self.color = TreeSim.colors["nice orange"]
        self.selected = True

    def set_unselected(self):
        self.color = TreeSim.colors["black"]
        self.selected = False

    def toggle_drag_mode(self):
        if self.drag_mode is True:
            self.drag_mode = False
            self.center = pygame.mouse.get_pos()
        elif self.drag_mode is False:
            self.drag_mode = True

    def is_clicked(self, pos):
        mouse_x = pos[0]
        mouse_y = pos[1]
        vertex_x = self.center[0]
        vertex_y = self.center[1]
        # the distance from the center of the vertex to the mouse position
        # distance formula
        distance = math.sqrt((math.pow((mouse_x - vertex_x), 2)) + (math.pow((mouse_y - vertex_y), 2)))
        if distance <= self.radius:
            return True
        else:
            return False


class Button:
    default_color: TreeSim.colors.values
    current_color: TreeSim.colors.values
    selected_color = TreeSim.colors["nice orange"]
    left: int
    top: int
    width: int
    height: int
    screen: pygame.display
    click_radius = 28

    def __init__(self, screen, color, left, top, width=50, height=50):
        self.screen = screen
        self.default_color = color
        self.current_color = color
        # [left, top, width, height]
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def draw(self):
        pass

    def set_selected(self):
        self.current_color = self.selected_color

    def set_default(self):
        self.current_color = self.default_color

    def is_clicked(self, pos):
        mouse_x = pos[0]
        mouse_y = pos[1]
        vertex_x = self.get_center()[0]
        vertex_y = self.get_center()[1]
        # the distance from the center of the vertex to the mouse position
        # distance formula
        distance = math.sqrt((math.pow((mouse_x - vertex_x), 2)) + (math.pow((mouse_y - vertex_y), 2)))
        if distance <= self.click_radius:
            return True
        else:
            return False

    def get_center(self):
        return (self.left + math.floor(self.width / 1.4), self.top + math.floor(self.height / 1.4))


class VertexButton(Button):
    def __init__(self, screen, color, left, top):
        super().__init__(screen, color, left, top)
        self.button_type = "vertex"

    def draw(self):
        pygame.draw.rect(self.screen, TreeSim.colors["black"], [self.left-2, self.left-2, self.width+4, self.height+4])
        pygame.draw.rect(self.screen, self.current_color, [self.left, self.top, self.width, self.height])
        pygame.draw.circle(self.screen, TreeSim.colors["black"], (math.floor(self.width/1.4), math.floor(self.height/1.4)), 10)


class LineButton(Button):
    def __init__(self, screen, color, left, top):
        super().__init__(screen, color, left, top)
        self.button_type = "line"

    def draw(self):
        pygame.draw.rect(self.screen, TreeSim.colors["black"], [self.left-2, self.top-2, self.width+4, self.height+4])
        pygame.draw.rect(self.screen, self.current_color, [self.left, self.top, self.width, self.height])
        pygame.draw.line(self.screen, TreeSim.colors["black"], (self.left+8, self.top+8), (self.left+self.width-8, self.top+self.height-8), 10)


class DragButton(Button):
    def __init__(self, screen, color, left, top):
        super().__init__(screen, color, left, top)
        self.button_type = "drag"
        self.width = 80
        self.click_radius = 40

    def draw(self):
        pygame.draw.rect(self.screen, TreeSim.colors["black"], [self.left-2, self.top-2, self.width+4, self.height+4])
        pygame.draw.rect(self.screen, self.current_color, [self.left, self.top, self.width, self.height])

        pygame.font.init()
        my_font = pygame.font.SysFont("Comic Sans MS", 15)
        text_surface = my_font.render("Transform", True, TreeSim.colors["black"])
        self.screen.blit(text_surface, (self.left+2, self.top+15))


class ScreenShotButton(Button):
    def __init__(self, screen, color, left, top):
        super().__init__(screen, color, left, top)
        self.button_type = "screenshot"
        self.width = 90
        self.click_radius = 40

    def draw(self):
        pygame.draw.rect(self.screen, TreeSim.colors["black"], [self.left-2, self.top-2, self.width+4, self.height+4])
        pygame.draw.rect(self.screen, self.current_color, [self.left, self.top, self.width, self.height])

        pygame.font.init()
        my_font = pygame.font.SysFont("Comic Sans MS", 15)
        text_surface = my_font.render("Screenshot", True, TreeSim.colors["black"])
        self.screen.blit(text_surface, (self.left+2, self.top+15))


class ClearButton(Button):
    def __init__(self, screen, color, left, top):
        super().__init__(screen, color, left, top)
        self.button_type = "clear"
        self.width = 90

    def draw(self):
        pygame.draw.rect(self.screen, TreeSim.colors["black"], [self.left-2, self.top-2, self.width+4, self.height+4])
        pygame.draw.rect(self.screen, self.current_color, [self.left, self.top, self.width, self.height])

        pygame.font.init()
        my_font = pygame.font.SysFont("Comic Sans MS", 15)
        text_surface = my_font.render("Clear screen", True, TreeSim.colors["black"])
        self.screen.blit(text_surface, (self.left+2, self.top+15))


sim = TreeSim()


