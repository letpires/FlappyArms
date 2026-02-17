import pygame
import cv2
import mediapipe as mp
import random
import sys

# Inicializar Pygame
pygame.init()

try:
    logo_image = pygame.image.load("bird_logo.png")
    logo_image = pygame.transform.scale(logo_image, (200, 200))
except:
    logo_image = None

# Configurações da tela
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Arms - Gym Edition")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 250)
LIGHT_BLUE = (173, 216, 230)
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
GOLD = (255, 200, 0)
RED = (220, 20, 60)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Configurações do jogo
GRAVITY = 0.5
FLAP_STRENGTH = -10
PIPE_WIDTH = 70
PIPE_GAP = 200
PIPE_SPEED = 3
BIRD_SIZE = 90

# Carregar imagem do pássaro
try:
    _bird_img = pygame.image.load("bird.png").convert_alpha()
    bird_image = pygame.transform.scale(_bird_img, (BIRD_SIZE, BIRD_SIZE))
except Exception:
    bird_image = None

# FPS
clock = pygame.time.Clock()
FPS = 60

# Fontes
font_small = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_title = pygame.font.Font(None, 90)

# ==================== CLASSES NOVAS ====================

class Cloud:
    """Classe para nuvens decorativas"""
    def __init__(self, x, y, speed, size=1.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        
    def update(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH + 100:
            self.x = -100
            
    def draw(self, screen):
        # Desenhar nuvem com múltiplos círculos
        base_size = int(40 * self.size)
        color = WHITE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), base_size)
        pygame.draw.circle(screen, color, (int(self.x + base_size), int(self.y)), int(base_size * 0.8))
        pygame.draw.circle(screen, color, (int(self.x + base_size * 1.8), int(self.y)), base_size)
        pygame.draw.circle(screen, color, (int(self.x + base_size * 0.5), int(self.y - base_size * 0.5)), int(base_size * 0.7))
        pygame.draw.circle(screen, color, (int(self.x + base_size * 1.3), int(self.y - base_size * 0.5)), int(base_size * 0.7))

# ==================== CLASSES ORIGINAIS ====================

class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = BIRD_SIZE
        self.image = bird_image
        
    def flap(self):
        self.velocity = FLAP_STRENGTH
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Limites da tela
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        if self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
            self.velocity = 0
            
    def draw(self, screen):
        if self.image is not None:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.image, rect)
        else:
            # Fallback: desenho do pássaro (círculo amarelo com olho e bico)
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size // 2)
            pygame.draw.circle(screen, BLACK, (int(self.x + 10), int(self.y - 5)), 5)
            pygame.draw.polygon(screen, RED, [
                (self.x + self.size // 2, self.y),
                (self.x + self.size // 2 + 15, self.y - 5),
                (self.x + self.size // 2 + 15, self.y + 5)
            ])
        
    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(150, SCREEN_HEIGHT - PIPE_GAP - 150)
        self.width = PIPE_WIDTH
        self.scored = False
        
    def update(self):
        self.x -= PIPE_SPEED
        
    def draw(self, screen):
        # Cano superior
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.gap_y))
        pygame.draw.rect(screen, (0, 100, 0), (self.x, 0, self.width, self.gap_y), 3)
        
        # Cano inferior
        pygame.draw.rect(screen, GREEN, (self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT))
        pygame.draw.rect(screen, (0, 100, 0), (self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT), 3)
        
    def collides_with(self, bird):
        bird_rect = bird.get_rect()
        
        # Cano superior
        top_pipe = pygame.Rect(self.x, 0, self.width, self.gap_y)
        # Cano inferior
        bottom_pipe = pygame.Rect(self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT)
        
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)
    
    def is_off_screen(self):
        return self.x < -self.width

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = cv2.VideoCapture(0)
        self.baseline_shoulder_y = None
        self.calibrated = False
        self.arms_raised = False
        self.last_raised = False
        
    def calibrate(self):
        """Calibra a posição inicial dos ombros"""
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)
            
            if results.pose_landmarks:
                # Pegar posição Y dos ombros
                left_shoulder = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
                
                self.baseline_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
                self.calibrated = True
                return True
        return False
    
    def detect_arms_raised(self):
        """Detecta se os braços estão levantados"""
        ret, frame = self.cap.read()
        if not ret:
            return False, None
            
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        
        if results.pose_landmarks and self.calibrated:
            # Pegar posição dos pulsos e ombros
            left_wrist = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            left_shoulder = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            
            # Verificar se os pulsos estão acima dos ombros
            left_raised = left_wrist.y < left_shoulder.y - 0.1
            right_raised = right_wrist.y < right_shoulder.y - 0.1
            
            # Detectar apenas a transição de não-levantado para levantado
            currently_raised = left_raised or right_raised
            flap_triggered = currently_raised and not self.last_raised
            
            self.last_raised = currently_raised
            self.arms_raised = currently_raised
            
            return flap_triggered, cv2.flip(frame, 1)
        
        return False, cv2.flip(frame, 1) if ret else None
    
    def release(self):
        self.cap.release()

# ==================== FUNÇÕES NOVAS ====================

def draw_text_with_outline(text, font, color, outline_color, x, y, center=False):
    """Desenha texto com contorno"""
    # Desenhar contorno
    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
        text_surface = font.render(text, True, outline_color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x + dx, y + dy)
        else:
            text_rect.topleft = (x + dx, y + dy)
        screen.blit(text_surface, text_rect)
    
    # Desenhar texto principal
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def draw_rounded_rect(surface, color, rect, radius=20, border=0, border_color=None):
    """Desenha retângulo com bordas arredondadas"""
    x, y, width, height = rect
    
    # Desenhar retângulo principal
    pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
    pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
    
    # Desenhar cantos arredondados
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)
    
    # Desenhar borda se especificada
    if border > 0 and border_color:
        draw_rounded_rect_border(surface, border_color, rect, radius, border)

def draw_rounded_rect_border(surface, color, rect, radius=20, width=3):
    """Desenha borda de retângulo arredondado"""
    x, y, w, h = rect
    
    # Linhas
    pygame.draw.line(surface, color, (x + radius, y), (x + w - radius, y), width)
    pygame.draw.line(surface, color, (x + radius, y + h), (x + w - radius, y + h), width)
    pygame.draw.line(surface, color, (x, y + radius), (x, y + h - radius), width)
    pygame.draw.line(surface, color, (x + w, y + radius), (x + w, y + h - radius), width)
    
    # Cantos
    pygame.draw.arc(surface, color, (x, y, radius*2, radius*2), 1.57, 3.14, width)
    pygame.draw.arc(surface, color, (x + w - radius*2, y, radius*2, radius*2), 0, 1.57, width)
    pygame.draw.arc(surface, color, (x, y + h - radius*2, radius*2, radius*2), 3.14, 4.71, width)
    pygame.draw.arc(surface, color, (x + w - radius*2, y + h - radius*2, radius*2, radius*2), 4.71, 6.28, width)

def draw_button(text, x, y, width, height, color, hover_color, text_color=WHITE):
    """Desenha botão estilizado"""
    mouse_pos = pygame.mouse.get_pos()
    is_hover = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height
    
    button_color = hover_color if is_hover else color
    
    # Sombra
    draw_rounded_rect(screen, (0, 0, 0, 100), (x + 5, y + 5, width, height), 15)
    
    # Botão
    draw_rounded_rect(screen, button_color, (x, y, width, height), 15, 4, (255, 255, 255))
    
    # Texto
    draw_text(text, font_medium, text_color, x + width // 2, y + height // 2, center=True)
    
    return is_hover

def draw_star(surface, color, x, y, size):
    """Desenha uma estrela decorativa"""
    points = []
    for i in range(10):
        angle = 3.14159 * 2 * i / 10
        if i % 2 == 0:
            r = size
        else:
            r = size / 2
        points.append((x + r * pygame.math.Vector2(1, 0).rotate_rad(angle).x,
                      y + r * pygame.math.Vector2(1, 0).rotate_rad(angle).y))
    pygame.draw.polygon(surface, color, points)

# ==================== FUNÇÕES ORIGINAIS ====================

def draw_text(text, font, color, x, y, center=False):
    """Desenha texto na tela"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)

def draw_camera_feed(frame, x, y, width, height, rounded=True):
    """Desenha o feed da câmera na tela do Pygame"""
    if frame is not None:
        frame_small = cv2.resize(frame, (width, height))
        frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        
        if rounded:
            # Desenhar borda arredondada branca
            draw_rounded_rect(screen, WHITE, (x - 5, y - 5, width + 10, height + 10), 20)
            draw_rounded_rect(screen, LIGHT_BLUE, (x - 3, y - 3, width + 6, height + 6), 18)
            
        screen.blit(frame_surface, (x, y))
        
        if rounded:
            # Adicionar borda decorativa
            draw_rounded_rect_border(screen, WHITE, (x, y, width, height), 15, 3)

# ==================== TELA DE MENU REFORMULADA ====================

def menu_screen(pose_detector):
    """Tela de menu inicial com design aprimorado"""
    waiting = True
    calibrating = False
    
    # Criar nuvens
    clouds = [
        Cloud(100, 100, 0.3, 1.2),
        Cloud(400, 150, 0.2, 0.8),
        Cloud(700, 80, 0.25, 1.0),
        Cloud(200, 300, 0.15, 1.1),
        Cloud(800, 250, 0.35, 0.9),
    ]
    
    star_positions = [
        (150, 80), (950, 120), (300, 450), (1000, 400), (500, 150),
        (200, 200), (800, 180), (400, 350), (900, 320)
    ]
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    calibrating = True
                    if pose_detector.calibrate():
                        return "play"
                if event.key == pygame.K_SPACE and pose_detector.calibrated:
                    return "play"
                if event.key == pygame.K_ESCAPE:
                    return "quit"
        
        # Pegar frame da câmera
        _, frame = pose_detector.cap.read()
        if frame is not None:
            frame = cv2.flip(frame, 1)
        
        # Gradiente de fundo
        for i in range(SCREEN_HEIGHT):
            color_value = BLUE[0] + (LIGHT_BLUE[0] - BLUE[0]) * i // SCREEN_HEIGHT
            pygame.draw.line(screen, (color_value, color_value + 30, 235), (0, i), (SCREEN_WIDTH, i))
        
        # Atualizar e desenhar nuvens
        for cloud in clouds:
            cloud.update()
            cloud.draw(screen)
        
        # Desenhar estrelas decorativas
        for i, (sx, sy) in enumerate(star_positions):
            alpha = abs(pygame.time.get_ticks() % 2000 - 1000) / 1000
            size = 8 + 3 * alpha if i % 2 == 0 else 8 + 3 * (1 - alpha)
            draw_star(screen, (255, 255, 200), sx, sy, size)
        
        # Desenhar logo do pássaro se existir
        logo_height = 200  # mesmo tamanho do scale da logo
        if logo_image:
            logo_x = SCREEN_WIDTH // 2 - 100
            logo_y = 10
            screen.blit(logo_image, (logo_x, logo_y))
            title_y = logo_y + logo_height + 20  # título logo abaixo da logo
        else:
            title_y = 70
        
        # Título "FLAPPY ARMS" com efeito
        draw_text_with_outline("FLAPPY ARMS", font_title, WHITE, ORANGE, SCREEN_WIDTH // 2, title_y, center=True)
        
        # Subtítulo
        draw_text("Wave to Play!", font_medium, GOLD, SCREEN_WIDTH // 2, title_y + 80, center=True)
        
        # Painel principal
        panel_width = 500
        panel_height = 360
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = 295
        
        # Sombra do painel
        draw_rounded_rect(screen, (100, 150, 200, 50), 
                         (panel_x + 8, panel_y + 8, panel_width, panel_height), 25)
        
        # Painel com borda
        draw_rounded_rect(screen, LIGHT_BLUE, 
                         (panel_x, panel_y, panel_width, panel_height), 25, 5, WHITE)
        
        # Título do painel
        if not pose_detector.calibrated:
            draw_text('Press "C" to CALIBRATE', font_small, (50, 100, 150), 
                     SCREEN_WIDTH // 2, panel_y + 30, center=True)
        else:
            draw_text('CALIBRATED!', font_medium, GREEN, 
                     SCREEN_WIDTH // 2, panel_y + 30, center=True)
        
        # Feed da câmera
        cam_width = 450
        cam_height = 250
        cam_x = (SCREEN_WIDTH - cam_width) // 2
        cam_y = panel_y + 70
        
        draw_camera_feed(frame, cam_x, cam_y, cam_width, cam_height, rounded=True)
        
        # Botão JOGAR (abaixo da câmera)
        if pose_detector.calibrated:
            button_width = 300
            button_height = 70
            button_x = (SCREEN_WIDTH - button_width) // 2
            button_y = cam_y + cam_height + 50
            
            # Setas decorativas
            arrow_y = button_y + button_height // 2
            for arrow_x in [button_x - 60, button_x + button_width + 30]:
                pygame.draw.polygon(screen, GOLD, [
                    (arrow_x, arrow_y - 15),
                    (arrow_x, arrow_y + 15),
                    (arrow_x + 25, arrow_y)
                ])
            
            draw_button("PLAY", button_x, button_y, button_width, button_height, 
                       GOLD, ORANGE, WHITE)
            
            draw_text('Press SPACE', font_small, WHITE, 
                     SCREEN_WIDTH // 2, button_y + button_height + 25, center=True)
        elif calibrating:
            draw_text("Calibrating...", font_medium, YELLOW, 
                     SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120, center=True)
        
        pygame.display.flip()
        clock.tick(30)
    
    return "quit"

# ==================== TELA DE GAME OVER REFORMULADA ====================

def game_over_screen(score, high_score):
    """Tela de game over com design aprimorado"""
    waiting = True
    clouds = [
        Cloud(100, 100, 0.3, 1.2),
        Cloud(400, 150, 0.2, 0.8),
        Cloud(700, 80, 0.25, 1.0),
    ]
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "play"
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        
        # Gradiente de fundo
        for i in range(SCREEN_HEIGHT):
            color_value = BLUE[0] + (LIGHT_BLUE[0] - BLUE[0]) * i // SCREEN_HEIGHT
            pygame.draw.line(screen, (color_value, color_value + 30, 235), (0, i), (SCREEN_WIDTH, i))
        
        # Desenhar nuvens
        for cloud in clouds:
            cloud.update()
            cloud.draw(screen)
        
        # Painel de Game Over
        panel_width = 600
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = 200
        
        draw_rounded_rect(screen, (255, 200, 200), 
                         (panel_x, panel_y, panel_width, panel_height), 30, 6, RED)
        
        draw_text_with_outline("GAME OVER!", font_large, RED, (100, 0, 0), 
                              SCREEN_WIDTH // 2, panel_y + 60, center=True)
        
        draw_text(f"Score: {score}", font_medium, BLACK, 
                 SCREEN_WIDTH // 2, panel_y + 150, center=True)
        draw_text(f"High Score: {high_score}", font_medium, GOLD, 
                 SCREEN_WIDTH // 2, panel_y + 210, center=True)
        
        # Botões
        button_y = panel_y + 280
        draw_text("SPACE - Play Again", font_small, (50, 50, 50), 
                 SCREEN_WIDTH // 2, button_y, center=True)
        draw_text("ESC - Menu", font_small, (50, 50, 50), 
                 SCREEN_WIDTH // 2, button_y + 50, center=True)
        
        pygame.display.flip()
        clock.tick(30)
    
    return "quit"

# ==================== LOOP PRINCIPAL DO JOGO ====================

def main():
    """Loop principal do jogo"""
    pose_detector = PoseDetector()
    high_score = 0
    
    state = "menu"
    
    try:
        while True:
            if state == "menu":
                state = menu_screen(pose_detector)
                if state == "quit":
                    break
                    
            elif state == "play":
                # Inicializar jogo
                bird = Bird()
                pipes = [Pipe(SCREEN_WIDTH + 200)]
                score = 0
                running = True
                
                # Nuvens de fundo
                game_clouds = [
                    Cloud(random.randint(0, SCREEN_WIDTH), random.randint(50, 300), 
                          random.uniform(0.2, 0.4), random.uniform(0.8, 1.2))
                    for _ in range(5)
                ]
                
                while running:
                    # Eventos
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            state = "quit"
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                                state = "menu"
                    
                    # Detectar braços levantados
                    flap_triggered, camera_frame = pose_detector.detect_arms_raised()
                    if flap_triggered:
                        bird.flap()
                    
                    # Atualizar pássaro
                    bird.update()
                    
                    # Atualizar canos
                    for pipe in pipes:
                        pipe.update()
                        
                        # Verificar colisão
                        if pipe.collides_with(bird):
                            running = False
                            if score > high_score:
                                high_score = score
                            state = "game_over"
                        
                        # Pontuar
                        if not pipe.scored and pipe.x + pipe.width < bird.x:
                            pipe.scored = True
                            score += 1
                    
                    # Remover canos fora da tela
                    pipes = [p for p in pipes if not p.is_off_screen()]
                    
                    # Adicionar novos canos
                    if len(pipes) == 0 or pipes[-1].x < SCREEN_WIDTH - 300:
                        pipes.append(Pipe(SCREEN_WIDTH))
                    
                    # Verificar se o pássaro saiu da tela
                    if bird.y >= SCREEN_HEIGHT - bird.size or bird.y <= 0:
                        running = False
                        if score > high_score:
                            high_score = score
                        state = "game_over"
                    
                    # Desenhar gradiente de fundo
                    for i in range(SCREEN_HEIGHT):
                        color_value = BLUE[0] + (LIGHT_BLUE[0] - BLUE[0]) * i // SCREEN_HEIGHT
                        pygame.draw.line(screen, (color_value, color_value + 30, 235), (0, i), (SCREEN_WIDTH, i))
                    
                    # Desenhar nuvens
                    for cloud in game_clouds:
                        cloud.update()
                        cloud.draw(screen)
                    
                    # Desenhar canos
                    for pipe in pipes:
                        pipe.draw(screen)
                    
                    # Desenhar pássaro
                    bird.draw(screen)
                    
                    # Desenhar pontuação com estilo
                    score_text = f"Score: {score}"
                    draw_rounded_rect(screen, (255, 255, 255, 200), (5, 5, 200, 60), 15)
                    draw_text(score_text, font_medium, BLACK, 15, 15)
                    
                    # Desenhar feed da câmera (pequeno no canto)
                    if camera_frame is not None:
                        draw_camera_feed(camera_frame, 250, 10, 140, 105, rounded=False)
                    
                    # Indicador de braços levantados
                    if pose_detector.arms_raised:
                        indicator_width = 250
                        indicator_height = 50
                        indicator_x = (SCREEN_WIDTH - indicator_width) // 2
                        indicator_y = SCREEN_HEIGHT - 60
                        
                        draw_rounded_rect(screen, GREEN, 
                                        (indicator_x, indicator_y, indicator_width, indicator_height), 15)
                        draw_text("ARMS UP!", font_small, WHITE, 
                                SCREEN_WIDTH // 2, indicator_y + 25, center=True)
                    
                    pygame.display.flip()
                    clock.tick(FPS)
            
            elif state == "game_over":
                state = game_over_screen(score, high_score)
                if state == "quit":
                    break
            
            else:
                break
    
    finally:
        pose_detector.release()
        pygame.quit()

if __name__ == "__main__":
    main()