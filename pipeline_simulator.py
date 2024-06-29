import pygame
import sys
import random

class Instruction:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class PipelineStage:
    def __init__(self, name):
        self.name = name
        self.current_instruction = None

    def set_instruction(self, instruction):
        self.current_instruction = instruction

class CPU:
    def __init__(self):
        self.stages = {
            'Fetch': PipelineStage('Fetch'),
            'Decode': PipelineStage('Decode'),
            'Execute': PipelineStage('Execute'),
            'Memory Access': PipelineStage('Memory Access'),
            'Write-back': PipelineStage('Write-back')
        }
        self.registers = {f'R{i}': random.randint(0, 100) for i in range(8)}
        self.memory = Memory()
        self.program_counter = 0
        self.instructions = []
        self.cycle_completed = False
        self.new_instruction_name = ""
        self.input_active = False

    def cycle(self):
        if not self.cycle_completed:
            if self.new_instruction_name:
                new_instruction = Instruction(self.new_instruction_name)
                self.instructions.append(new_instruction)
                self.new_instruction_name = ""

            for stage_name in ['Write-back', 'Memory Access', 'Execute', 'Decode', 'Fetch']:
                current_stage = self.stages[stage_name]
                next_stage = self.stages[stage_name if stage_name == 'Fetch' else list(self.stages.keys())[list(self.stages.keys()).index(stage_name)-1]]
                current_stage.set_instruction(next_stage.current_instruction)

            if self.program_counter < len(self.instructions):
                self.stages['Fetch'].set_instruction(self.instructions[self.program_counter])
                self.program_counter += 1
            else:
                self.stages['Fetch'].set_instruction(None)

            for reg in self.registers:
                self.registers[reg] = random.randint(0, 100)

            for address in range(100):
                self.memory.data[address] = random.randint(0, 255)

            self.cycle_completed = True
        else:
            self.cycle_completed = False
            return False

class Memory:
    def __init__(self):
        self.data = {i: random.randint(0, 255) for i in range(100)}

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BACKGROUND_COLOR = (173, 216, 230)
PANEL_COLOR = (144, 238, 144)
TEXT_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 140, 0)
SHADOW_COLOR = (105, 105, 105)
STAGE_COLORS = {
    'Fetch': (255, 182, 193),
    'Decode': (200, 255, 200),
    'Execute': (135, 206, 250),
    'Memory Access': (255, 160, 122),
    'Write-back': (221, 160, 221)
}

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Simulador de Pipeline de CPU Avanzado')

title_font = pygame.font.SysFont('Arial', 28, bold=True)
header_font = pygame.font.SysFont('Arial', 20, bold=True)
normal_font = pygame.font.SysFont('Comic Sans MS', 16)

cpu = CPU()

def draw_panel(x, y, width, height, title):
    pygame.draw.rect(screen, PANEL_COLOR, (x, y, width, height))
    pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x, y, width, height), 2)
    title_surface = header_font.render(title, True, TEXT_COLOR)
    screen.blit(title_surface, (x + 10, y + 10))

def draw_button(x, y, width, height, text):
    pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x, y, width, height), border_radius=5)
    pygame.draw.rect(screen, SHADOW_COLOR, (x+2, y+2, width-4, height-4), border_radius=5)
    button_text = normal_font.render(text, True, TEXT_COLOR)
    text_x = x + (width - button_text.get_width()) // 2
    text_y = y + (height - button_text.get_height()) // 2
    screen.blit(button_text, (text_x, text_y))

def draw_interface():
    draw_button(20, 60, 200, 30, "Insertar Instrucción")
    if cpu.input_active:
        pygame.draw.rect(screen, PANEL_COLOR, (240, 60, 200, 30))
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, (240, 60, 200, 30), 2)
        if len(cpu.new_instruction_name) > 0:
            input_text = normal_font.render(cpu.new_instruction_name, True, TEXT_COLOR)
        else:
            input_text = normal_font.render("Ingrese nombre", True, SHADOW_COLOR)
        screen.blit(input_text, (250, 67))

def draw_pipeline():
    draw_panel(20, 100, WINDOW_WIDTH - 40, 200, "Pipeline Stages")
    y = 130
    for stage in cpu.stages.values():
        color = STAGE_COLORS.get(stage.name, PANEL_COLOR)
        pygame.draw.rect(screen, SHADOW_COLOR, (30, y+5, WINDOW_WIDTH - 60, 30), border_radius=5)
        pygame.draw.rect(screen, color, (30, y, WINDOW_WIDTH - 60, 30), border_radius=5)
        if stage.current_instruction:
            text = normal_font.render(f"{stage.name}: {stage.current_instruction}", True, TEXT_COLOR)
        else:
            text = normal_font.render(f"{stage.name}: empty", True, TEXT_COLOR)
        screen.blit(text, (40, y + 5))
        y += 35

def draw_registers():
    draw_panel(20, 320, (WINDOW_WIDTH - 60) // 2, 250, "Registers")
    y = 350
    for reg, value in cpu.registers.items():
        text = normal_font.render(f"{reg}: {value}", True, TEXT_COLOR)
        screen.blit(text, (40, y))
        y += 25

def draw_memory():
    draw_panel((WINDOW_WIDTH + 20) // 2, 320, (WINDOW_WIDTH - 60) // 2, 250, "Memory")
    y = 350
    line_height = 20
    max_lines = 10
    for i, (address, value) in enumerate(list(cpu.memory.data.items())[:max_lines]):
        text = normal_font.render(f"Mem[{address}]: {value}", True, TEXT_COLOR)
        if y + line_height <= 570:
            screen.blit(text, ((WINDOW_WIDTH // 2) + 40, y))
            y += line_height

def draw_stats(cycle_count):
    stats_text = f"Cycle: {cycle_count} | PC: {cpu.program_counter}"
    stats_surface = header_font.render(stats_text, True, TEXT_COLOR)
    screen.blit(stats_surface, (20, 20))

running = True
clock = pygame.time.Clock()
cycle_count = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if 20 <= mouse_x <= 220 and 60 <= mouse_y <= 90:
                cpu.input_active = not cpu.input_active
        elif event.type == pygame.KEYDOWN:
            if cpu.input_active:
                if event.key == pygame.K_RETURN:
                    cpu.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    cpu.new_instruction_name = cpu.new_instruction_name[:-1]
                else:
                    cpu.new_instruction_name += event.unicode

    if not cpu.input_active and cpu.cycle():
        cycle_count += 1

    screen.fill(BACKGROUND_COLOR)
    draw_interface()
    draw_pipeline()
    draw_registers()
    draw_memory()
    draw_stats(cycle_count)
    
    title_surface = title_font.render("Simulador de Pipeline de CPU", True, HIGHLIGHT_COLOR)
    screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, 20))

    pygame.display.flip()
    clock.tick(1)

pygame.quit()
sys.exit()
