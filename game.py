from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
# from ursina.shaders import lit_with_shadows_shader
# from ursina.shaders import normals_shader
# from ursina.shaders import unlit_shader
from ursina.shaders import basic_lighting_shader
Entity.default_shader = basic_lighting_shader
# from ursina.shaders import matcap_shader - un re viaje

random.seed(0)

app = Ursina()
window.borderless = False
always_on_top = False
window.title = 'py-doom'
# window.fullscreen = True
camera.fov = 90
window.show_ursina_splash = True

editor_camera = EditorCamera(enabled=False, ignore_paused=True)

MAP = Entity(model='E1M1_ME.obj', texture='2dassets/FLOOR7_1.PNG')
# (model='e1m1.obj', texture='placeholder.png')
MAP.collider = MeshCollider(MAP, center=(0, 0, 0))
player = FirstPersonController(model='cube', texture='2dassets/py.png', speed=20)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

# position=(.10, -.25, .50), rotation=(90, 90, 0)
gun = Entity(model='3dassets/gun1.obj', parent=camera, origin_z=-.5, color=color.gray, scale=(2, 2, 2), position=(-1, -.10, .20), rotation=(.30, 90, 0), 
              on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, world_scale=.5, model='quad', color=color.yellow, enabled=False, z=1)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

def update():
    if held_keys['left mouse']:
        shoot()
    if held_keys['c']:
        player.scale = 1, 1, 1
        player.speed = 8
    else:
        player.scale = 2, 2, 2
        player.speed = 20

from ursina.prefabs.health_bar import HealthBar

# position=(5, 0, 0

class bidon(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='3dassets/bidon.obj', origin_y=-.5, texture='2dassets/bidon.png', collider='box', **kwargs) 
        self.max_hp = 20
        self.hp = self.max_hp

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            print("PLUUUUMM")
            return

class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube', scale_y=2, origin_y=-.5, texture='2dassets/FormerHumanSheet.png', collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 50
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            print("mama i just killed a man!")
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

# Enemy()
enemies = [Enemy(x=x*1) for x in range(1)]

[bidon(x=x*4) for x in range(2)]

def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)

def pause_input(key):
    if key == 'tab':  # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled


pause_handler = Entity(ignore_paused=True, input=pause_input)

Sky(texture='F_SKY1.png', color=color.red, filtering=True)

app.run()

