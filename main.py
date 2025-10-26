import pygame
from sensor import Sensor, add_sensor, sensor_list, gen_mesh, calc_dist, flood_fill, delete_sensor, Hub, generate_hex_sensor_mesh, send_message_on_click, gen_mesh_no_update_MQTT

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
running = True
start_time = pygame.time.get_ticks()


sensors = sensor_list()
hub = Hub(screen.get_size()[0] - 50, screen.get_size()[1] - 50, 200)

mode = 0
mouse_pos_1 = pygame.Vector2(-1, -1)
#modes: 0 is add sensors
#modes: 1 delete sensors
#modes: 2 send message from sensor

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_0:
                mode = 0
            elif event.key == pygame.K_1:
                mode = 1
            elif event.key == pygame.K_2:
                mode = 2
            elif event.key == pygame.K_3:
                generate_hex_sensor_mesh(sensors, screen, hub)
                gen_mesh(sensors, hub)
                flood_fill(sensors, hub)
            elif event.key == pygame.K_SPACE:
                hub.publish("Hello from hub")
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and mode == 0:
                if mouse_pos_1 == pygame.Vector2(-1, -1):
                    mouse_pos_1 = pygame.Vector2(event.pos[0], event.pos[1])
                else:
                    add_sensor(sensors, Sensor(int(mouse_pos_1.x), int(mouse_pos_1.y), event.pos[0], event.pos[1]))
                    mouse_pos_1 = pygame.Vector2(-1, -1)
                    gen_mesh(sensors, hub)
                    flood_fill(sensors, hub)
            if event.button == 1 and mode == 1:
                delete_sensor(sensors, pygame.Vector2(pygame.mouse.get_pos()))
                gen_mesh_no_update_MQTT(sensors, hub)
                flood_fill(sensors, hub)
            if event.button == 1 and mode == 2:
                send_message_on_click(sensors, pygame.Vector2(pygame.mouse.get_pos()))
            
    screen.fill("dark green")
    if mouse_pos_1 == pygame.Vector2(-1, -1):
        pass
    else:
        pygame.draw.circle(screen, "orange", mouse_pos_1, 3)
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = pygame.Vector2(mouse_pos[0], mouse_pos[1])
        pygame.draw.circle(screen, "orange", mouse_pos_1, calc_dist(mouse_pos_1, mouse_pos), 3)
    pygame.draw.circle(screen, "blue", hub.get_location(), hub.range, 3)
    pygame.draw.circle(screen, "blue", hub.get_location(), 3)
    for sensor in sensors:
        color = "black"
        if not sensor.visited:
            color = "red"
            time_mils = pygame.time.get_ticks() - start_time
            time_secs = time_mils / 1000
            if int(time_secs) % 2 == 1:
                color = "dark gray"
        pygame.draw.circle(screen, color, sensor.get_location(), sensor.get_range(), 3)
        pygame.draw.circle(screen, color, sensor.get_location(), 3)
        if not sensor.visited: continue
        for a in sensor.connected_sensors:
            pygame.draw.aaline(screen, "blue", sensor.get_location(), a.get_location())
    pygame.display.flip()
    clock.tick(60)

pygame.quit()