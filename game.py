from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader

random.seed(0)

app = Ursina()
window.borderless = False
always_on_top = False
window.title = 'py-om'
# window.fullscreen = True
camera.fov = 30
window.forced_aspect_ratio = 1.230

editor_camera = EditorCamera(enabled=False, ignore_paused=True)

MAP = Entity(model='e1m1-ver_9.blend', collider='mesh', shader=basic_lighting_shader, scale=(5), texture='2dassets/textures.png')

# (model='e1m1.obj', texture='placeholder.png')
player = FirstPersonController(model='quad', z=-10, texture='2dassets/PLAYA1', origin_y=-.5, world_scale=2, jump_height=4)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

# position=(.10, -.25, .50), rotation=(90, 90, 0)
gun = Entity(load_texture('pistol.png'), parent=camera, on_cooldown=False, origin_z=-.5,)
# origin_z=-.5, color=color.gray, scale=(2, 2, 2), position=(-1, -.10, .20), rotation=(.30, 90, 0)
gun.muzzle_flash = Entity(parent=gun, world_scale=.5, model='quad', color=color.yellow, enabled=False, z=1)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

def update():
    if held_keys['left mouse']:
        shoot()
    if held_keys['c']:
        player.scale = 1, 1, 1
        player.speed = 2
    else:
        player.scale = 2, 2, 2
        player.speed = 20
    if held_keys['shift']:
        player.speed = 35
    else:
        player.speed = 20

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

Sky(texture='F_SKY1.png', color=color.red)
pivot = Entity()
# DirectionalLight(parent=pivot, y=2, z=3, shadows=True, rotation=(45, -45, 45), color=color.red)
# AmbientLight(color=color.black10)

app.run()

