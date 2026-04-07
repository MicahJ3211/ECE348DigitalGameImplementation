import pygame
from src.config import *
from src.scenes import MenuScene, GameplayScene, GameOverScene
from src.scenes.ai_select_scene import AISelectScene
from src.scenes.ai_results_scene import AIResultsScene
from src.scenes.draft_scene import DraftScene


class Game:
    """Main game class managing scenes and game loop."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Asset storage
        self.assets = {
            'images': {},
            'sounds': {},
            'fonts': {}
        }
        
        # Scene management
        self.scenes = {}
        self.current_scene = None
        
        # Load assets before setting up scenes
        if not self.load_assets():
            print("Warning: Some assets failed to load, using fallbacks")
        
        self.setup_scenes()
    
    def load_assets(self) -> bool:
        """
        Load game assets with error handling.
        
        Returns:
            bool: True if all critical assets loaded, False if some failed
        """
        import os
        
        all_loaded = True
        
        # Try to load fonts
        try:
            self.assets['fonts']['default'] = pygame.font.Font(None, 32)
            self.assets['fonts']['large'] = pygame.font.Font(None, 48)
        except Exception as e:
            print(f"Error loading fonts: {e}")
            # Fallback to system fonts
            try:
                self.assets['fonts']['default'] = pygame.font.SysFont('arial', 32)
                self.assets['fonts']['large'] = pygame.font.SysFont('arial', 48)
            except:
                print("Critical: Could not load any fonts")
                all_loaded = False
        
        # Try to load card images (optional)
        card_image_path = 'assets/images/cards/'
        if os.path.exists(card_image_path):
            try:
                # Load card images if they exist
                for filename in os.listdir(card_image_path):
                    if filename.endswith('.png'):
                        img_path = os.path.join(card_image_path, filename)
                        self.assets['images'][filename] = pygame.image.load(img_path)
            except Exception as e:
                print(f"Warning: Could not load card images: {e}")
                print("Using colored rectangles as fallback")
        
        # Try to load sounds (optional)
        sounds_path = 'assets/sounds/'
        if os.path.exists(sounds_path):
            try:
                pygame.mixer.init()
                for filename in os.listdir(sounds_path):
                    if filename.endswith('.wav') or filename.endswith('.ogg'):
                        sound_path = os.path.join(sounds_path, filename)
                        self.assets['sounds'][filename] = pygame.mixer.Sound(sound_path)
            except Exception as e:
                print(f"Warning: Could not load sounds: {e}")
                print("Game will run without sound effects")
        
        return all_loaded
    
    def setup_scenes(self):
        """Initialize all scenes."""
        self.scenes['menu'] = MenuScene(self.screen)
        self.current_scene = self.scenes['menu']
    
    def change_scene(self, scene_name, *args):
        """Change to a different scene."""
        if scene_name == 'menu':
            self.scenes['menu'] = MenuScene(self.screen)
            self.current_scene = self.scenes['menu']
        elif scene_name == 'gameplay':
            # Start with draft phase
            self.scenes['draft'] = DraftScene(self.screen)
            self.current_scene = self.scenes['draft']
        elif scene_name == 'gameplay_draft':
            # Coming from draft scene with pre-drafted cards
            player_cards = args[0] if len(args) > 0 else None
            ai_cards = args[1] if len(args) > 1 else None
            self.scenes['gameplay'] = GameplayScene(self.screen, player_cards, ai_cards)
            self.current_scene = self.scenes['gameplay']
        elif scene_name == 'game_over':
            win_condition = args[0] if args else None
            self.scenes['game_over'] = GameOverScene(self.screen, win_condition)
            self.current_scene = self.scenes['game_over']
        elif scene_name == 'ai_select':
            self.scenes['ai_select'] = AISelectScene(self.screen)
            self.current_scene = self.scenes['ai_select']
        elif scene_name == 'ai_results':
            ai1 = args[0] if len(args) > 0 else None
            ai2 = args[1] if len(args) > 1 else None
            self.scenes['ai_results'] = AIResultsScene(self.screen, ai1, ai2)
            self.current_scene = self.scenes['ai_results']
    
    def handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            else:
                self.current_scene.handle_input(event)
    
    def update(self, delta_time: float):
        """Update game state."""
        self.current_scene.update(delta_time)
        
        # Check for scene transition
        if self.current_scene.next_scene:
            if isinstance(self.current_scene.next_scene, tuple):
                scene_name, *args = self.current_scene.next_scene
                self.change_scene(scene_name, *args)
            else:
                self.change_scene(self.current_scene.next_scene)
            self.current_scene.next_scene = None
    
    def render(self):
        """Render current scene."""
        self.current_scene.render()
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(delta_time)
            self.render()

    def quit(self):
        """Gracefully shutdown the game."""
        print("Shutting down game...")
        
        # Stop any playing sounds
        try:
            pygame.mixer.stop()
            pygame.mixer.quit()
        except:
            pass
        
        # Clean up resources
        self.assets = None
        self.scenes = None
        self.current_scene = None
        
        # Set running flag to False
        self.running = False
        
        print("Game shutdown complete")
