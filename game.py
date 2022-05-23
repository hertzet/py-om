from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
# from ursina.shaders import unlit_shader
# from ursina.shaders import normals_shader
# from ursina.shaders import lit_with_shadows_shader
from ursina.shaders import basic_lighting_shader

# from ursina.shaders import matcap_shader - un re viaje
application.development = not False

app = Ursina()
window.borderless = False
always_on_top = False
window.title = 'py-doom'
# window.fullscreen = True
camera.fov = 100

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
Entity.default_shader = basic_lighting_shader

MAP = Entity(model='e1m1.obj', texture='texturesheet.png', filtering=False)
MAP.collider = MeshCollider(MAP, center=(0, 0, 0))
# Entity(model='plane', collider='box', scale=500, texture='grass', texture_scale=(4,4))
player = FirstPersonController(scale=(2, 2, 2), speed=20)
player.collider = BoxCollider(player, Vec3(2, 2, 2))

gun = Entity(model='cube', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5, color=color.red,
             on_cooldown=False)
# gun = Entity(model='gun.fbx', parent=camera, color=color.red, on_cooldown=False, world_scale=1)
# position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)


def shoot():
    if not gun.on_cooldown:
        print('pow pow')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        # from ursina.prefabs.ursfx import ursfx
        # ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
        # pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=1)
        print('reloading')
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)


shootables_parent = Entity()
mouse.traverse_target = shootables_parent


class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube', texture='FormerHumanSheet.png', scale_y=2, origin_y=-.5,
                         collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 20
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
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
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1


# Enemy()
enemies = [Enemy(x=x * 4) for x in range(4)]


def update():
    if held_keys['left mouse']:
        shoot()


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

# Sky(texture='F_SKY1.png', filtering=False, color=color.red)

app.run()
