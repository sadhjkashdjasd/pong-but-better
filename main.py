import src.DGL.alpha_process
from src import gui
from src import player as pl
from src import vfx
from src.config import *
from src import sound


def pause():
    done = False
    delta = 1
    ticks = 0
    paused_text_x = -728
    paused_text = font16.render('Paused', True, (255, 255, 255))
    paused_text_ = paused_text.copy()
    paused_text_.set_alpha(120)
    buttons = [gui.Button(0, 0), gui.Button(0, 0)]

    buttons[0].text_ = 'Continue'
    buttons[0].font = font16
    buttons[0].text_reflection = True
    buttons[0].animation_type = 'down'
    buttons[0].sprite = buttons[0].text
    buttons[0].update_data('text')
    buttons[0].x = (gs.get_width() - buttons[0].text.get_width()) // 2
    buttons[0].y = gs.get_height() - 64

    buttons[1].text_ = 'Back To Menu'
    buttons[1].font = font16
    buttons[1].text_reflection = True
    buttons[1].animation_type = 'right'
    buttons[1].sprite = buttons[1].text
    buttons[1].update_data('text')
    buttons[1].x = (gs.get_width() - buttons[1].text.get_width()) // 2
    buttons[1].y = gs.get_height() - 96

    mbut = []
    stars = []
    for _ in range(random.randint(9, 19)):
        stars.append([[random.randint(0, gs.get_width()), random.randint(0, gs.get_height())],
                      random.randint(2, 5), random.randint(2, 4)])

    while not done:
        gs.fill((0, 0, 0))
        ticks += 1 / delta
        mx, my = pygame.mouse.get_pos()
        mx //= 2
        my //= 2

        for star in stars:
            pygame.draw.circle(gs, (255, 255, 255), star[0], star[1])
            star[0][1] += star[2] / delta
            if star[0][1] > gs.get_width():
                stars.remove(star)
                stars.append([[random.randint(0, gs.get_width()), 0], random.randint(2, 5), random.randint(2, 4)])

        paused_text_x -= ((paused_text_x - (gs.get_width() - paused_text.get_width()) // 2) / 15) / delta

        for button in buttons:
            button.draw()
            if button.collide(mx, my):
                button.collide_ = True
                if button.text_ == 'Continue' and 1 in mbut:
                    sound.play_button_pressed_sound()
                    done = True
                if button.text_ == "Back To Menu" and 1 in mbut:
                    sound.play_button_pressed_sound()
                    menu()

            else:
                button.collide_ = False
            button.animate(delta)

        gs.blit(paused_text_, (paused_text_x + 3, 32 + 2))
        gs.blit(paused_text, (paused_text_x, 32))

        for i in pygame.event.get():
            if i.type == QUIT:
                quit(0)

            if i.type == KEYDOWN:
                if i.key == K_ESCAPE:
                    sound.play_button_pressed_sound()
                    done = True

            if i.type == MOUSEBUTTONDOWN:
                mbut.append(i.button)
            elif i.type == MOUSEBUTTONUP and i.button in mbut:
                mbut.remove(i.button)

        sc.blit(pygame.transform.scale(gs, sc.get_size()), (0, 0))
        pygame.display.update()

        clock.tick()
        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1


def main():
    done = False
    delta = 1
    keys = []
    ticks = 0
    ball_pos = [(gs.get_width() - 20) // 2, (gs.get_height() - 20) // 2]
    ball_energy = [random.randint(0, 0), random.randint(0, 0)]
    cls = pygame.Surface(gs.get_size())
    cls.set_alpha(18)
    ball_stoped_ticks = 0
    translate = 'eng'

    ball_stoped_text = font24.render(static['public']['text'][translate]['ball_stopped'], True, (255, 255, 255))
    ball_stoped_text_target_y = gs.get_height() // 2 - ball_stoped_text.get_height() // 2
    ball_stoped_text_pos = [gs.get_width() // 2 - ball_stoped_text.get_width() // 2, 0]

    ball_out_text = font24.render(static['public']['text'][translate]['ball_out'], True, (255, 255, 255))
    ball_out_text_target_y = gs.get_height() // 2 - ball_out_text.get_height() // 2
    ball_out_text_pos = [gs.get_width() // 2 - ball_out_text.get_width() // 2, 0]
    ball_out_ticks = 0

    players = [pl.Player('1real', [25, random.randint(0, gs.get_height() - 48)], 'FirstPlayer'),
               pl.Player(f'2{settings["public"]["render"]["opponent"]}', [gs.get_width() - 25 - 16,
                                                                          random.randint(0, gs.get_height() - 48)],
                         'SecondPlayer')]
    fps_x = 0

    particles = []
    bg_color = [0, 0, 0]
    _bg_color = [0, 0, 0]
    sc_pos = [0, 0]

    st_score = 0
    player1_score_text_y = 600
    player_text_afk = 90
    nd_score = 0
    player2_score_text_y = 600
    _player_text_afk = 90
    bg_timer = 0
    screen_shake_time = 0
    screen_shake_power = 200
    idle_timer = 0
    dif_cof = 1
    if settings['public']['render']['Difficulty'] == "easy":
        dif_cof = 0.5
    elif settings['public']['render']['Difficulty'] == "normal":
        dif_cof = 1
    elif settings['public']['render']['Difficulty'] == "hard":
        dif_cof = 1.5

    while not done:
        ticks += 1 / delta
        prev_st_score = st_score
        prev_nd_score = nd_score
        idle_timer += 1 / delta

        if st_score > 50 or nd_score > 50:
            game_over(st_score, nd_score)

        if bg_timer >= 45:
            _bg_color = [0, 0, 0]
            bg_timer = 0
        bg_timer += 1 / delta

        if not settings['public']['render']['track_e']:
            gs.fill((0, 0, 0))
        else:
            gs.blit(cls, (0, 0))

        if ball_energy[0] > static['protected']['player']['speed']['max'] * dif_cof:
            ball_energy[0] = static['protected']['player']['speed']['max'] * dif_cof
        if ball_energy[1] > static['protected']['player']['speed']['max'] * dif_cof:
            ball_energy[1] = static['protected']['player']['speed']['max'] * dif_cof

        if ball_pos[0] < -10 or ball_pos[0] > gs.get_width() + 10 \
                or ball_pos[1] < -10 or ball_pos[1] > gs.get_height() + 10:
            if ball_out_text_pos[1] < ball_out_text_target_y:
                ball_out_text_pos[1] -= ((ball_out_text_pos[1] - ball_out_text_target_y) / 15) / delta
        else:
            if ball_out_text_pos[1] > -ball_out_text.get_width():
                ball_out_text_pos[1] += ((ball_out_text_pos[1] - ball_out_text_target_y) / 15) / delta

        if abs(ball_energy[0]) < 0.05 \
                and abs(ball_energy[1]) < 0.05:
            if ball_stoped_text_pos[1] < ball_stoped_text_target_y:
                ball_stoped_text_pos[1] -= ((ball_stoped_text_pos[1] - ball_stoped_text_target_y) / 15) / delta
        else:
            if ball_stoped_text_pos[1] > -ball_stoped_text.get_height():
                ball_stoped_text_pos[1] -= ((ball_stoped_text_pos[1] - -ball_stoped_text.get_width()) / 15) / delta

        pygame.draw.circle(gs, (255, 255, 255), ball_pos, 10)
        ball_pos[0] += ball_energy[0] / delta
        ball_pos[1] += ball_energy[1] / delta

        for particle in particles:
            particle.update(delta)
            particle.draw([0, 0])
            if not particle.alive:
                particles.remove(particle)

        if ball_energy[0] > 0:
            ball_energy[0] -= 0.01 / delta
        if ball_energy[0] < 0:
            ball_energy[0] += 0.01 / delta

        if ball_energy[1] > 0:
            ball_energy[1] -= 0.01 / delta
        if ball_energy[1] < 0:
            ball_energy[1] += 0.01 / delta

        if len(particles) > 25:
            particles = []

        for player in players:
            if not ball_stoped_ticks:
                player.draw()
            player.control(keys, delta, ball_pos, ball_energy)
            if player.collide_with_ball(ball_pos, ball_energy):
                _bg_color = [10, 10, 10]
                sound.play_player_hit_sound()
                screen_shake_time = 15
                screen_shake_power = random.randint(int(abs(ball_energy[0])),
                                                    int(abs(ball_energy[0])) + int(abs(ball_energy[1])))
                for _ in range(random.randint(5, 10)):
                    particles.append(vfx.Particle(
                        [ball_pos[0] + random.randint(-8, 8), ball_pos[1] + random.randint(-8, 8)],
                        random.randint(2, 5),
                        [random.randint(int(ball_energy[0]) - 4, int(ball_energy[0]) + 4),
                         random.randint(int(ball_energy[1]) - 4, int(ball_energy[1]) + 4)],
                        random.randint(1, 5) / 100, r_alpha=10, color=(255, 255, 255), reflection=False
                    ))

        if ball_pos[0] >= gs.get_width() - 5 or ball_pos[0] <= 5:
            ball_energy[0] *= -1.06
            sound.play_border_hit_sound()
            screen_shake_power = int(abs(ball_energy[0] + ball_energy[1]))
            screen_shake_time = int(abs(ball_energy[0] + ball_energy[1]))
            for _ in range(random.randint(5, 10)):
                particles.append(vfx.Particle(
                    [ball_pos[0] + random.randint(-8, 8), ball_pos[1] + random.randint(-8, 8)],
                    random.randint(2, 5),
                    [random.randint(int(ball_energy[0]) - 4, int(ball_energy[0]) + 4),
                     random.randint(int(ball_energy[1]) - 4, int(ball_energy[1]) + 4)],
                    random.randint(1, 5) / 100, r_alpha=10, color=(255, 255, 255), reflection=False
                ))

        if ball_pos[1] >= gs.get_height() - 5 or ball_pos[1] <= 5:
            ball_energy[1] *= -1.06
            sound.play_border_hit_sound()
            screen_shake_power = int(abs(ball_energy[0] + ball_energy[1]))
            screen_shake_time = int(abs(ball_energy[0] + ball_energy[1]))
            for _ in range(random.randint(2, 4)):
                particles.append(vfx.Particle(
                    [ball_pos[0] + random.randint(-8, 8), ball_pos[1] + random.randint(-8, 8)],
                    random.randint(2, 5),
                    [random.randint(int(ball_energy[0]) - 4, int(ball_energy[0]) + 4),
                     random.randint(int(ball_energy[1]) - 4, int(ball_energy[1]) + 4)],
                    random.randint(1, 5) / 100, r_alpha=10, color=(255, 255, 255), reflection=False
                ))

        if keys:
            idle_timer = 0
        if idle_timer >= 5400:
            players[0].mode = '1ai'
            players[1].mode = '2ai'

        for i in pygame.event.get():
            if i.type == QUIT:
                quit(0)

            if i.type == KEYDOWN:
                keys.append(i.key)
                if i.key == K_ESCAPE:
                    sound.play_button_pressed_sound()
                    pause()

            elif i.type == KEYUP and i.key in keys:
                keys.remove(i.key)

        if settings['public']['render']['light']:
            gs.blit(prerender_light['player'], [ball_pos[0] - 23, ball_pos[1] - 23])
            for player in players:
                if not ball_stoped_ticks:
                    gs.blit(prerender_light['_player'], [player.pos[0] - 20, player.pos[1] - 18])

        if ball_stoped_text_pos[1] > 100:
            ball_stoped_ticks += 0.4 / delta
            if ball_stoped_ticks * 5 >= ball_stoped_text.get_width():
                ball_energy = [random.randint(-6, 6), random.randint(-1, 1)]

        else:
            ball_stoped_ticks = 0

        if ball_pos[0] >= gs.get_width() - 15:
            st_score += random.randint(2, 6) / 100

        if 15 >= ball_pos[0] > 2:
            nd_score += random.randint(1, 5) / 100

        if ball_out_text_pos[1] > 100:
            ball_out_ticks += 0.4 / delta
            if ball_out_ticks * 5 >= ball_out_text.get_width():
                ball_pos = [gs.get_width() // 2 - 10,
                            gs.get_height() // 2 - 10]
                for _ in range(random.randint(1, 2)):
                    particles.append(vfx.Particle(
                        [ball_pos[0] + random.randint(-8, 8), ball_pos[1] + random.randint(-8, 8)],
                        random.randint(2, 5),
                        [random.randint(-6, 6),
                         random.randint(-6, 6)],
                        random.randint(1, 5) / 100, r_alpha=10, color=(255, 255, 255), reflection=False
                    ))

        else:
            ball_out_ticks = 0

        if ball_stoped_text_pos[1] > -24:
            gs.blit(src.DGL.alpha_process.trs(ball_stoped_text, 15),
                    (ball_stoped_text_pos[0] + 3, ball_stoped_text_pos[1] + 2))
            gs.blit(ball_stoped_text, ball_stoped_text_pos)
            gs.blit(src.DGL.alpha_process.trs(vfx.rect_surf((255, 255, 255), ball_stoped_ticks * 5, 15), 10),
                    (ball_stoped_text_pos[0] + 7,
                     ball_stoped_text_pos[1] + ball_stoped_text.get_height() + 21))
            pygame.draw.rect(gs, (255, 255, 255), (ball_stoped_text_pos[0],
                                                   ball_stoped_text_pos[1] + ball_stoped_text.get_height() + 15,
                                                   ball_stoped_ticks * 5, 15))

        if nd_score == 0:
            nd_score += 1

        player1_score_text = font24.render('Player 1: ' + str(int(st_score)), True, (50, 50, 230))
        player2_score_text = font24.render('Player 2: ' + str(int(nd_score)), True, (230, 50, 50))
        gs.blit(src.DGL.alpha_process.trs(player1_score_text, 15),
                (gs.get_width() // 2 - player1_score_text.get_width() // 2 + 4,
                 player1_score_text_y + 3))

        gs.blit(player1_score_text, (gs.get_width() // 2 - player1_score_text.get_width() // 2, player1_score_text_y))

        gs.blit(src.DGL.alpha_process.trs(player2_score_text, 15),
                (gs.get_width() // 2 - player2_score_text.get_width() // 2 + 4,
                 player2_score_text_y + 3))

        gs.blit(player2_score_text, (gs.get_width() // 2 - player2_score_text.get_width() // 2, player2_score_text_y))

        if player_text_afk < 45:
            player1_score_text_y -= \
                ((player1_score_text_y - (gs.get_height() - player1_score_text.get_height() - 15)) / 15) / delta
        else:
            player1_score_text_y -= \
                ((player1_score_text_y - (gs.get_height() + player1_score_text.get_height() + 15)) / 15) / delta

        if _player_text_afk < 45:
            player2_score_text_y -= \
                ((player2_score_text_y - (gs.get_height() - player2_score_text.get_height() - 15)) / 15) / delta
        else:
            player2_score_text_y -= \
                ((player2_score_text_y - (gs.get_height() + player2_score_text.get_height() + 15)) / 15) / delta

        if ball_out_text_pos[1] > -24:
            gs.blit(src.DGL.alpha_process.trs(ball_out_text, 15),
                    (ball_out_text_pos[0] + 3, ball_out_text_pos[1] + 2))
            gs.blit(ball_out_text, ball_out_text_pos)
            if ball_out_ticks * 5 < ball_out_text.get_width():
                gs.blit(src.DGL.alpha_process.trs(vfx.rect_surf((255, 255, 255), ball_out_ticks * 5, 15), 10),
                        (ball_out_text_pos[0] + 7,
                         ball_out_text_pos[1] + ball_out_text.get_height() + 21))
                pygame.draw.rect(gs, (255, 255, 255), (ball_out_text_pos[0],
                                                       ball_out_text_pos[1] + ball_out_text.get_height() + 15,
                                                       ball_out_ticks * 5, 15))
            else:
                gs.blit(src.DGL.alpha_process.trs(vfx.rect_surf((255, 255, 255), ball_out_text.get_height() * 5,
                                                                15), 10),
                        (ball_out_text_pos[0] + 7,
                         ball_out_text_pos[1] + ball_out_text.get_height() + 21))
                pygame.draw.rect(gs, (255, 255, 255), (ball_out_text_pos[0],
                                                       ball_out_text_pos[1] + ball_out_text.get_height() + 15,
                                                       ball_out_text.get_width(), 15))

        if settings['public']['render']['screen_shake']:
            if screen_shake_time > 0:
                screen_shake_time -= 1 / delta
                sc_pos = [random.randint(-screen_shake_power, screen_shake_power),
                          random.randint(-screen_shake_power, screen_shake_power)]
            else:
                sc_pos = [0, 0]
        sc.blit(pygame.transform.scale(gs, sc.get_size()), sc_pos)
        if settings['public']['render']['display_fps']:
            sc.blit(font16.render(f'FPS: {int(clock.get_fps())}', True, (255, 255, 255)), (fps_x, 10))
            for player in players:
                if player.mode == '1real':
                    if player.pos[1] <= 15:
                        fps_x -= ((fps_x - 128) / 10) / delta
                    else:
                        fps_x -= ((fps_x - 10) / 10) / delta

        if st_score == prev_st_score:
            player_text_afk += 1 / delta
        else:
            player_text_afk = 0
            _bg_color = [5, 5, 10]

        if prev_nd_score == nd_score:
            _player_text_afk += 1 / delta
        else:
            _player_text_afk = 0 / delta
            _bg_color = [10, 5, 5]

        pygame.display.update()

        if settings['public']['render']['dynamic_bg'] and settings['public']['render']['track_e']:
            cls.fill((int(bg_color[0]), int(bg_color[1]), int(bg_color[2])))
            if bg_color[0] < _bg_color[0]:
                bg_color[0] += ((_bg_color[0] - bg_color[0]) / 15) / delta
            if bg_color[1] < _bg_color[1]:
                bg_color[1] += ((_bg_color[1] - bg_color[1]) / 15) / delta
            if bg_color[2] < _bg_color[2]:
                bg_color[2] += ((_bg_color[2] - bg_color[2]) / 15) / delta

            if bg_color[0] > _bg_color[0]:
                bg_color[0] += ((_bg_color[0] - bg_color[0]) / 15) / delta
            if bg_color[1] > _bg_color[1]:
                bg_color[1] += ((_bg_color[1] - bg_color[1]) / 15) / delta
            if bg_color[2] > _bg_color[2]:
                bg_color[2] += ((_bg_color[2] - bg_color[2]) / 15) / delta

        clock.tick(fps)
        delta = clock.get_fps() / default_tps
        if delta == 0:
            delta = 1


def menu():
    done = False
    sc_pos = [0, 0]
    screen_shake_time = 0
    screen_shake_power = 20
    delta = 1
    fps_x = 0
    in_font = pygame.font.Font(None, 0)
    try:
        segoi_print48 = pygame.font.SysFont('Segoe Print', 32)
    except:
        segoi_print48 = pygame.font.Font(None, 32)

    try:
        segoe_ui_emoji_48 = pygame.font.SysFont('Segoe UI Emoji', 48)
    except:
        segoe_ui_emoji_48 = pygame.font.Font(None, 48)

    buttons = [gui.Button(0, 0), gui.Button(0, 0), gui.Button(0, 0), gui.Button(0, 0)]
    buttons[0].font = font16
    buttons[0].text_ = 'Play'
    buttons[0].update_data('text')
    buttons[0].sprite = buttons[0].text
    buttons[0].text_reflection = True
    buttons[0].animation_type = 'up'
    buttons[0].y = gs.get_height() - 100
    buttons[0].x = (gs.get_width() - buttons[0].text.get_width()) // 2

    buttons[1].font = font16
    buttons[1].text_ = 'Quit'
    buttons[1].update_data('text')
    buttons[1].sprite = buttons[0].text
    buttons[1].text_reflection = True
    buttons[1].animation_type = 'left'
    buttons[1].y = gs.get_height() - 65
    buttons[1].x = (gs.get_width() - buttons[1].text.get_width()) // 2

    settings_image = pygame.Surface((32, 32))
    pygame.draw.rect(settings_image, (255, 255, 255), (0, 0, 32, 32), 1, border_radius=7)
    # settings_image.blit(arial48.render('*', True, (255, 255, 255)), (6, -1))
    settings_image.blit(segoe_ui_emoji_48.render('⚙', True, (255, 255, 255)), (0, -1))

    info_image = pygame.Surface((32, 32))
    pygame.draw.rect(info_image, (255, 255, 255), (0, 0, 32, 32), 1, border_radius=7)
    info_image.blit(segoi_print48.render('i', True, (255, 255, 255)), (10, -12))

    buttons[2].font = in_font
    buttons[2].text_ = 'Settings'
    buttons[2].update_data('text')
    buttons[2].sprite = settings_image
    buttons[2].text_reflection = True
    buttons[2].animation_type = 'left'
    buttons[2].y = 8
    buttons[2].x = (gs.get_width() - 32) - 8
    buttons[2].image = settings_image
    buttons[2].image_reflection = True
    buttons[2].update_data('image')

    buttons[3].font = in_font
    buttons[3].text_ = 'Info'
    buttons[3].update_data('text')
    buttons[3].sprite = info_image
    buttons[3].text_reflection = True
    buttons[3].animation_type = 'right'
    buttons[3].y = 24
    buttons[3].x = 8
    buttons[3].image = info_image
    buttons[3].image_reflection = True
    buttons[3].update_data('image')

    stars = []
    mbut = []
    for _ in range(random.randint(2, 5)):
        stars.append([random.choice([(255, 255, 255), (255, 255, 250), (230, 230, 230)]),
                      [random.randint(0, gs.get_width()), random.randint(0, gs.get_height())], random.randint(2, 4),
                      random.randint(2, 5)])
    game_logo = pygame.transform.scale(pygame.image.load('data/textures/game/logo/1.bmp'), (92, 92))
    game_logo_y = 24
    game_logo_y_direction = 'down'
    game_logo_x = (gs.get_width() - game_logo.get_width()) // 2
    game_logo_ = game_logo.copy()
    game_logo_.set_alpha(100)
    logo_blicks = []

    while not done:
        gs.fill((5, 5, 10))
        mx, my = pygame.mouse.get_pos()
        mx = mx // 2
        my = my // 2

        if game_logo_y_direction == 'down':
            game_logo_y += 0.1 / delta
        elif game_logo_y_direction == 'up':
            game_logo_y -= 0.1 / delta

        if game_logo_y <= 19:
            game_logo_y_direction = 'down'
        if game_logo_y >= 33:
            game_logo_y_direction = 'up'

        for star in stars:
            pygame.draw.circle(gs, star[0], star[1], star[2])
            star[1][0] -= star[3] / delta
            if star[1][0] < -16:
                stars.remove(star)
                stars.append([random.choice([(255, 255, 255), (255, 255, 250), (230, 230, 230)]),
                              [gs.get_width() + 32, random.randint(0, gs.get_height())], random.randint(2, 5),
                              random.randint(2, 5)])

        gs.blit(game_logo_, (game_logo_x + 5, game_logo_y + 3))
        gs.blit(game_logo, (game_logo_x, game_logo_y))
        if not random.randint(0, 100):
            logo_blicks.append([255,
                                [random.randint(int(game_logo_x), int(game_logo_x) + game_logo.get_width()),
                                 random.randint(int(game_logo_y), int(game_logo_y) + game_logo.get_height())],
                                random.randint(2, 4)])

        for logo_blick in logo_blicks:
            # pygame.draw.circle(gs, (255 - logo_blick[0], 255 - logo_blick[0], 255 - logo_blick[0]),
            #                    logo_blick[1], logo_blick[2])
            gs.blit(vfx.circle_surf((255, 255, 255),
                                    logo_blick[2], alpha=int(logo_blick[0])), logo_blick[1])
            logo_blick[0] -= 3 / delta
            if logo_blick[0] <= 200 or logo_blick[2] < 1:
                logo_blicks.remove(logo_blick)

        for i in pygame.event.get():
            if i.type == QUIT:
                quit(0)

            if i.type == MOUSEBUTTONDOWN:
                mbut.append(i.button)
            elif i.type == MOUSEBUTTONUP and i.button in mbut:
                mbut.remove(i.button)

        if settings['public']['render']['screen_shake']:
            if screen_shake_time > 0:
                screen_shake_time -= 1 / delta
                sc_pos = [random.randint(-screen_shake_power, screen_shake_power),
                          random.randint(-screen_shake_power, screen_shake_power)]

            else:
                sc_pos = [0, 0]

        for button in buttons:
            button.draw()
            if button.collide(mx, my):
                button.collide_ = True
                if button.text_ == 'Play' and 1 in mbut:
                    sound.play_button_pressed_sound()
                    main()
                if button.text_ == 'Quit' and 1 in mbut:
                    sound.play_button_pressed_sound()
                    quit(0)
                if button.text_ == 'Settings' and 1 in mbut:
                    sound.play_button_pressed_sound()
                    _settings()
                if button.text_ == "Info" and 1 in mbut:
                    sound.play_button_pressed_sound()
                    about()

            else:
                button.collide_ = False
            button.animate(delta)

        sc.blit(pygame.transform.scale(gs, sc.get_size()), sc_pos)
        if settings['public']['render']['display_fps']:
            fps_text = font16.render(f'FPS: {int(clock.get_fps())}', True, (255, 255, 255))
            sc.blit(fps_text, (fps_x, 10))

            if mx <= fps_text.get_width() and my <= fps_text.get_height():
                fps_x -= ((fps_x - fps_text.get_width()) / 10) / delta
            else:
                fps_x -= ((fps_x - 10) / 10) / delta
        pygame.display.update()
        clock.tick()

        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1


def _settings():
    done = False
    delta = 1
    ticks = 0
    stars = []
    fps_x = 0
    page = 'main_screen'
    buttons = [gui.Button(0, 0), gui.Button(0, 0), gui.Button(0, 0), gui.Button(20, 120), gui.Button(10, 145),
               gui.Button(3, 165), gui.Button(0, 0), gui.Button(0, 0), gui.Button(0, 0)]

    buttons[0].font = font8
    buttons[0].text_ = 'Back To Menu'
    buttons[0].update_data('text')
    buttons[0].animation_type = 'left'
    buttons[0].sprite = buttons[0].text
    buttons[0].text_reflection = True
    buttons[0].x = gs.get_width() - buttons[0].text.get_width() - 8
    buttons[0].y = gs.get_height() - buttons[0].text.get_height() - 8

    buttons[1].font = font16
    buttons[1].text_ = 'Graphics'
    buttons[1].update_data('text')
    buttons[1].animation_type = 'up'
    buttons[1].sprite = buttons[1].text
    buttons[1].text_reflection = True
    buttons[1].x = (gs.get_width() - buttons[1].text.get_width()) // 2
    buttons[1].y = ((gs.get_height() - buttons[1].text.get_height()) // 2) - 14

    buttons[2].font = font8
    buttons[2].text_ = 'Back'
    buttons[2].update_data('text')
    buttons[2].animation_type = 'left'
    buttons[2].sprite = buttons[2].text
    buttons[2].text_reflection = True
    buttons[2].x = gs.get_width() - buttons[2].text.get_width() - 8
    buttons[2].y = gs.get_height() - buttons[2].text.get_height() - 8

    buttons[3].font = font12
    buttons[3].text_ = 'light: '
    buttons[3].update_data('text')
    buttons[3].animation_type = 'right'
    buttons[3].sprite = buttons[3].text
    buttons[3].text_reflection = True

    buttons[4].font = font12
    buttons[4].text_ = 'display fps: '
    buttons[4].update_data('text')
    buttons[4].animation_type = 'right'
    buttons[4].sprite = buttons[4].text
    buttons[4].text_reflection = True

    buttons[5].font = font12
    buttons[5].text_ = 'screen shake: '
    buttons[5].update_data('text')
    buttons[5].animation_type = 'right'
    buttons[5].sprite = buttons[4].text
    buttons[5].text_reflection = True

    buttons[6].font = font16
    buttons[6].text_ = 'Gameplay'
    buttons[6].update_data('text')
    buttons[6].animation_type = 'down'
    buttons[6].sprite = buttons[6].text
    buttons[6].text_reflection = True
    buttons[6].x = (gs.get_width() - buttons[6].text.get_width()) // 2
    buttons[6].y = ((gs.get_height() - buttons[6].text.get_height()) // 2) + 14

    buttons[7].font = font12
    buttons[7].text_ = 'Opponent: '
    buttons[7].update_data('text')
    buttons[7].animation_type = 'right'
    buttons[7].sprite = buttons[7].text
    buttons[7].text_reflection = True
    buttons[7].x = ((gs.get_width() - buttons[7].text.get_width()) // 2) - 70
    buttons[7].y = 64

    buttons[8].font = font12
    buttons[8].text_ = 'Difficulty: '
    buttons[8].update_data('text')
    buttons[8].animation_type = 'right'
    buttons[8].sprite = buttons[8].text
    buttons[8].text_reflection = True
    buttons[8].x = ((gs.get_width() - buttons[8].text.get_width()) // 2) - 70
    buttons[8].y = 90

    mbut = []
    okey = pygame.Surface((150, 100))
    okey.set_colorkey((50, 200, 50))

    for _ in range(random.randint(3, 6)):
        stars.append([random.choice([(255, 255, 255), (255, 255, 250), (230, 230, 230)]),
                      [random.randint(0, gs.get_width()), random.randint(0, gs.get_height())], random.randint(2, 4),
                      random.randint(2, 5)])

    while not done:
        gs.fill((0, 0, 0))
        mx, my = pygame.mouse.get_pos()
        mx = mx // 2
        my = my // 2
        for button in buttons:
            if page == "gameplay":
                if button.text_ == "Back" or "Opponent: " in button.text_ or "Difficulty: " in button.text_:
                    button.draw()
                    if "Difficulty" in button.text_:
                        button.text_ = f"Difficulty: {settings['public']['render']['Difficulty']}"
                        button.update_data("text")

                    if button.collide(mx, my):
                        button.collide_ = True
                        if 1 not in mbut:
                            button.changed = True

                        if button.text_ == 'Back' and 1 in mbut:
                            page = "main_screen"
                        if "Opponent" in button.text_ and 1 in mbut and button.changed:
                            sound.play_button_pressed_sound()
                            if settings['public']['render']['opponent'] == 'ai':
                                settings['public']['render']['opponent'] = 'real'
                            elif settings['public']['render']['opponent'] == 'real':
                                settings['public']['render']['opponent'] = 'ai'
                            settings_data = json.dumps(settings)
                            s = open('data/json/settings.json', 'w')
                            s.write(settings_data)
                            s.close()
                            button.changed = False
                        if "Difficulty" in button.text_ and 1 in mbut and button.changed:
                            sound.play_button_pressed_sound()
                            if settings['public']['render']['Difficulty'] == 'hard':
                                settings['public']['render']['Difficulty'] = 'easy'
                            elif settings['public']['render']['Difficulty'] == 'easy':
                                settings['public']['render']['Difficulty'] = 'normal'
                            elif settings['public']['render']['Difficulty'] == 'normal':
                                settings['public']['render']['Difficulty'] = 'hard'
                            settings_data = json.dumps(settings)
                            s = open('data/json/settings.json', 'w')
                            s.write(settings_data)
                            s.close()
                            button.changed = False

                    else:
                        button.collide_ = False
                    button.animate(delta)

            if page == "main_screen":
                if button.text_ == "Back To Menu" or button.text_ == "Graphics" or button.text_ == "Gameplay":
                    button.draw()
                    if button.collide(mx, my):
                        button.collide_ = True
                        if 1 not in mbut:
                            button.changed = True

                        if button.text_ == 'Graphics' and 1 in mbut:
                            sound.play_button_pressed_sound()
                            page = "Graphics"
                        if button.text_ == 'Back To Menu' and 1 in mbut:
                            sound.play_button_pressed_sound()
                            menu()
                        if button.text_ == "Gameplay" and 1 in mbut:
                            sound.play_button_pressed_sound()
                            page = "gameplay"

                    else:
                        button.collide_ = False
                    button.animate(delta)

            if page == "Graphics":
                if button.text_ == "Back" or "light: " in button.text_ or "display fps: " in button.text_ \
                        or "screen shake: " in button.text_:
                    button.draw()
                    if button.collide(mx, my):
                        button.collide_ = True
                        if 1 not in mbut:
                            button.changed = True

                        if button.text_ == 'light: True' and 1 in mbut and button.changed:
                            sound.play_button_pressed_sound()
                            settings['public']['render']['light'] = False
                            settings_data = json.dumps(settings)
                            s = open('data/json/settings.json', 'w')
                            s.write(settings_data)
                            s.close()
                            button.changed = False

                        if button.text_ == 'light: False' and 1 in mbut and button.changed:
                            sound.play_button_pressed_sound()
                            settings['public']['render']['light'] = True
                            settings_data = json.dumps(settings)
                            s = open('data/json/settings.json', 'w')
                            s.write(settings_data)
                            s.close()
                            button.changed = False

                        if button.text_ == 'display fps: True' and 1 in mbut and button.changed:
                            sound.play_button_pressed_sound()
                            settings['public']['render']['display_fps'] = False
                            settings_data = json.dumps(settings)
                            s = open('data/json/settings.json', 'w')
                            s.write(settings_data)
                            s.close()
                            button.changed = False

                        if button.text_ == 'display fps: False' and 1 in mbut and button.changed:
                            sound.play_button_pressed_sound()
                            settings['public']['render']['display_fps'] = True
                            settings_data = json.dumps(settings)
                            s = open('data/json/settings.json', 'w')
                            s.write(settings_data)
                            s.close()
                            button.changed = False

                        if button.text_ == 'screen shake: True' and 1 in mbut and button.changed:
                            sound.play_button_pressed_sound()
                            settings['public']['render']['screen_shake'] = False
                            settings_data = json.dumps(settings)
                            s = open('data/json/settings.json', 'w')
                            s.write(settings_data)
                            s.close()
                            button.changed = False

                        if button.text_ == 'screen shake: False' and 1 in mbut and button.changed:
                            sound.play_button_pressed_sound()
                            settings['public']['render']['screen_shake'] = True
                            settings_data = json.dumps(settings)
                            s = open('data/json/settings.json', 'w')
                            s.write(settings_data)
                            s.close()
                            button.changed = False

                        if button.text_ == 'Back' and 1 in mbut:
                            sound.play_button_pressed_sound()
                            page = "main_screen"
                    else:
                        button.collide_ = False
                    button.animate(delta)

        for star in stars:
            pygame.draw.circle(gs, star[0], star[1], star[2])
            star[1][0] += star[3] / delta
            if star[1][0] > gs.get_width():
                stars.remove(star)
                stars.append([random.choice([(255, 255, 255), (255, 255, 250), (230, 230, 230)]),
                              [-32, random.randint(0, gs.get_height())], random.randint(2, 5),
                              random.randint(2, 5)])

        if page == "main_screen":
            pass
        elif page == "Graphics":
            okey.fill((10, 10, 20))
            pygame.draw.circle(okey, (255, 255, 255), (50, 50), 10)
            pygame.draw.rect(okey, (255, 255, 255), (0, 65, 16, 48))
            buttons[3].text_ = f'light: {settings["public"]["render"]["light"]}'
            buttons[3].update_data('text')
            buttons[3].sprite = buttons[3].text

            buttons[4].text_ = f'display fps: {settings["public"]["render"]["display_fps"]}'
            buttons[4].update_data('text')
            buttons[4].sprite = buttons[4].text

            buttons[5].text_ = f'screen shake: {settings["public"]["render"]["screen_shake"]}'
            buttons[5].update_data('text')
            buttons[5].sprite = buttons[5].text
            if settings['public']['render']['light']:
                okey.blit(prerender_light['player_'], [50 - 23, 50 - 23])
                okey.blit(prerender_light['_player_'], [0 - 20, 65 - 18])
            gs.blit(okey, (gs.get_width() - 150, 0))
        elif page == "gameplay":
            buttons[7].text_ = f'Opponent: {settings["public"]["render"]["opponent"]}'
            buttons[7].update_data('text')
            buttons[7].sprite = buttons[7].text

        ticks += 1 / delta

        for i in pygame.event.get():
            if i.type == QUIT:
                quit(0)
            if i.type == MOUSEBUTTONDOWN:
                mbut.append(i.button)
            elif i.type == MOUSEBUTTONUP and i.button in mbut:
                mbut.remove(i.button)

            if i.type == KEYDOWN:
                if i.key == K_ESCAPE:
                    if page == "main_screen":
                        sound.play_button_pressed_sound()
                        menu()
                    elif page == "Graphics" or page == "gameplay":
                        sound.play_button_pressed_sound()
                        page = "main_screen"

        sc.blit(pygame.transform.scale(gs, sc.get_size()), (0, 0))

        if settings['public']['render']['display_fps']:
            fps_text = font16.render(f'FPS: {int(clock.get_fps())}', True, (255, 255, 255))
            sc.blit(fps_text, (fps_x, 10))

            if mx <= fps_text.get_width() and my <= fps_text.get_height():
                fps_x -= ((fps_x - fps_text.get_width()) / 10) / delta
            else:
                fps_x -= ((fps_x - 10) / 10) / delta

        pygame.display.update()

        clock.tick()
        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1


def game_over(first_player_score, second_player_score):
    done = False
    delta = 1
    stars = []
    first_player_score, second_player_score = int(first_player_score), int(second_player_score)

    for _ in range(random.randint(7, 15)):
        stars.append([random.choice([(255, 255, 255), (255, 255, 250), (230, 230, 230)]),
                      [random.randint(0, gs.get_width()), random.randint(0, gs.get_height())], random.randint(2, 4),
                      random.randint(2, 5)])
    if first_player_score > second_player_score:
        some_player_win_text = font16.render('Player 1 Won!', True, (50, 50, 230))
    elif first_player_score < second_player_score:
        some_player_win_text = font16.render('Player 2 Won!', True, (230, 50, 50))
    else:
        some_player_win_text = font16.render('Draw!', True, (230, 230, 50))

    some_player_win_text_ = some_player_win_text.copy()
    some_player_win_text_.set_alpha(120)
    win_text_pos_x = -256
    first_player_score, second_player_score = str(first_player_score), str(second_player_score)
    if len(first_player_score) < 2:
        first_player_score = sorted(first_player_score, reverse=True)
        first_player_score += '0'
        first_player_score = first_player_score[1] + first_player_score[0]
    if len(second_player_score) < 2:
        second_player_score = sorted(second_player_score, reverse=True)
        second_player_score += '0'
        second_player_score = second_player_score[1] + second_player_score[0]

    score_text_part_1 = font12.render(f'{first_player_score}', True, (50, 50, 230))
    score_text_part_2 = font12.render(f':', True, (240, 240, 200))
    score_text_part_3 = font12.render(f'{second_player_score}', True, (230, 50, 50))
    score_text = pygame.Surface((score_text_part_3.get_width() + score_text_part_2.get_width()
                                 + score_text_part_1.get_width(),
                                 score_text_part_1.get_height()))
    score_text.blit(score_text_part_1, (0, 0))
    score_text.blit(score_text_part_2, (score_text_part_1.get_width() + 1, 0))
    score_text.blit(score_text_part_3, (score_text_part_1.get_width() + score_text_part_2.get_width() + 2, 0))
    score_text_ = score_text.copy()
    score_text_.set_alpha(120)
    score_text_pos = -48
    mbut = []
    buttons = [gui.Button(0, 0)]
    buttons[0].text_ = 'Back To Menu'
    buttons[0].font = font16
    buttons[0].text_reflection = True
    buttons[0].animation_type = 'left'
    buttons[0].animation_mm = 20
    buttons[0].sprite = buttons[0].text
    buttons[0].update_data('text')
    buttons[0].x = (gs.get_width() - buttons[0].text.get_width()) // 2
    buttons[0].y = gs.get_height() - 96
    fps_x = 0

    while not done:
        gs.fill((0, 0, 0))

        win_text_pos_x -= ((win_text_pos_x - (gs.get_width() - some_player_win_text.get_width()) / 2) / 10) / delta
        if win_text_pos_x >= ((gs.get_width() - some_player_win_text.get_width()) // 2) - 16:
            if score_text_pos < 180:
                score_text_pos -= ((score_text_pos - (some_player_win_text.get_width() + 16)) / 30) / delta
            gs.blit(score_text_, (score_text_pos + win_text_pos_x + 3, 52 + 2))
            gs.blit(score_text, (score_text_pos + win_text_pos_x, 52))

        gs.blit(some_player_win_text_, (win_text_pos_x + 3, 24 + 2))
        gs.blit(some_player_win_text, (win_text_pos_x, 24))
        mx, my = pygame.mouse.get_pos()
        mx //= 2
        my //= 2

        for button in buttons:
            button.draw()
            if button.collide(mx, my):
                button.collide_ = True
                if button.text_ == "Back To Menu" and 1 in mbut:
                    sound.play_button_pressed_sound()
                    menu()

            else:
                button.collide_ = False
            button.animate(delta)

        for star in stars:
            pygame.draw.circle(gs, star[0], star[1], star[2])
            star[1][0] -= star[3] / delta
            if star[1][0] < -16:
                stars.remove(star)
                stars.append([random.choice([(255, 255, 255), (255, 255, 250), (230, 230, 230)]),
                              [gs.get_width() + 32, random.randint(0, gs.get_height())], random.randint(2, 5),
                              random.randint(2, 5)])

        for i in pygame.event.get():
            if i.type == QUIT:
                quit(0)

            if i.type == MOUSEBUTTONDOWN:
                mbut.append(i.button)
            elif i.type == MOUSEBUTTONUP and i.button in mbut:
                mbut.remove(i.button)

        sc.blit(pygame.transform.scale(gs, sc.get_size()), (0, 0))
        if settings['public']['render']['display_fps']:
            fps_text = font16.render(f'FPS: {int(clock.get_fps())}', True, (255, 255, 255))
            sc.blit(fps_text, (fps_x, 10))

            if mx <= fps_text.get_width() and my <= fps_text.get_height():
                fps_x -= ((fps_x - fps_text.get_width()) / 10) / delta
            else:
                fps_x -= ((fps_x - 10) / 10) / delta
        pygame.display.update()
        clock.tick()

        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1


def about():
    done = False
    delta = 1
    fps_x = 0
    stars = []
    buttons = [gui.Button(0, 0)]
    buttons[0].font = font8
    buttons[0].text_ = 'Back'
    buttons[0].update_data('text')
    buttons[0].animation_type = 'left'
    buttons[0].sprite = buttons[0].text
    buttons[0].text_reflection = True
    buttons[0].x = gs.get_width() - buttons[0].text.get_width() - 8
    buttons[0].y = gs.get_height() - buttons[0].text.get_height() - 8
    mbut = []
    about_ = json.loads(open('data/json/about.json').read())
    creator_text_part_1 = font8.render('Developer: ', True, (255, 255, 250))
    creator_text_part_2 = font8.render(str(about_['creator']), True, (50, 50, 250))

    creator_text = pygame.Surface((creator_text_part_1.get_width() + creator_text_part_2.get_width() + 5,
                                   creator_text_part_1.get_height()))
    creator_text.blit(creator_text_part_1, (0, 0))
    creator_text.blit(creator_text_part_2, (creator_text_part_1.get_width() + 5, 0))

    creator_text_shade = creator_text.copy()
    creator_text_shade.set_alpha(120)

    game_page_available = about_['type']
    version_color = about_['version_color']
    type_text_color = (200, 200, 50)
    try:
        float(about_['version'])
    except:
        game_page_available = 'invalid'
        version_color = (249, 50, 50)
        type_text_color = (200, 10, 10)

    version_text_part_1 = font8.render('Version: ', True, (255, 255, 250))
    version_text_part_2 = font8.render(str(about_['version']), True, version_color)
    version_text_part_3 = font4.render(game_page_available, True, type_text_color)

    version_text = pygame.Surface((version_text_part_1.get_width() + version_text_part_2.get_width()
                                   + version_text_part_3.get_width() + 14,
                                   version_text_part_1.get_height()))
    version_text.blit(version_text_part_1, (0, 0))
    version_text.blit(version_text_part_2, (version_text_part_1.get_width() + 5, 0))
    version_text.blit(version_text_part_3, (version_text_part_1.get_width() + version_text_part_2.get_width() + 14, 0))

    version_text_shade = version_text.copy()
    version_text_shade.set_alpha(120)

    tools_text_part_1 = font8.render('Tools: ', True, (255, 255, 250))
    tools_text_part_2 = font8.render(about_["tools"], True, (50, 255, 250))

    tools_text = pygame.Surface((tools_text_part_1.get_width() + tools_text_part_2.get_width() + 10,
                                 tools_text_part_1.get_height()))
    tools_text.blit(tools_text_part_1, (0, 0))
    tools_text.blit(tools_text_part_2, (tools_text_part_1.get_width() + 7, 0))

    tools_text_shade = tools_text.copy()
    tools_text_shade.set_alpha(120)

    version_text_x = -256
    creator_text_x = -512
    tools_text_x = -1024

    for _ in range(random.randint(6, 13)):
        stars.append([[random.randint(0, gs.get_width()), random.randint(0, gs.get_height())],
                      random.randint(2, 5), random.randint(2, 4)])

    while not done:
        gs.fill((0, 0, 0))
        mx, my = pygame.mouse.get_pos()
        mx //= 2
        my //= 2

        for star in stars:
            pygame.draw.circle(gs, (255, 255, 255), star[0], star[1])
            star[0][1] += star[2] / delta
            if star[0][1] > gs.get_width():
                stars.remove(star)
                stars.append([[random.randint(0, gs.get_width()), 0], random.randint(2, 5), random.randint(2, 4)])

        gs.blit(creator_text_shade, (creator_text_x + 5, 48 + 4))
        gs.blit(creator_text, (creator_text_x, 48))
        creator_text_x -= ((creator_text_x - 30) / 15) / delta

        gs.blit(version_text_shade, (version_text_x + 5, 76 + 4))
        gs.blit(version_text, (version_text_x, 76))
        version_text_x -= ((version_text_x - 30) / 15) / delta

        gs.blit(tools_text_shade, (tools_text_x + 5, 102 + 4))
        gs.blit(tools_text, (tools_text_x, 102))
        tools_text_x -= ((tools_text_x - 30) / 15) / delta

        for button in buttons:
            button.draw()
            if button.collide(mx, my):
                button.collide_ = True
                if button.text_ == 'Back' and 1 in mbut:
                    sound.play_button_pressed_sound()
                    menu()
            else:
                button.collide_ = False
            button.animate(delta)

        for i in pygame.event.get():
            if i.type == QUIT:
                quit(0)

            if i.type == KEYDOWN:
                if i.key == K_ESCAPE:
                    sound.play_button_pressed_sound()
                    menu()

            if i.type == MOUSEBUTTONDOWN:
                mbut.append(i.button)
            elif i.type == MOUSEBUTTONUP and i.button in mbut:
                mbut.remove(i.button)

        sc.blit(pygame.transform.scale(gs, sc.get_size()), (0, 0))
        if settings['public']['render']['display_fps']:
            fps_text = font16.render(f'FPS: {int(clock.get_fps())}', True, (255, 255, 255))
            sc.blit(fps_text, (fps_x, 10))

            if mx <= fps_text.get_width() and my <= fps_text.get_height():
                fps_x -= ((fps_x - fps_text.get_width()) / 10) / delta
            else:
                fps_x -= ((fps_x - 10) / 10) / delta
        pygame.display.update()
        clock.tick()

        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1


def menu_():
    done = False
    delta = 1
    fps_x = 0
    stars = []
    buttons = [gui.Button(0, 0)]
    buttons[0].font = font8
    buttons[0].text_ = 'Back'
    buttons[0].update_data('text')
    buttons[0].animation_type = 'left'
    buttons[0].sprite = buttons[0].text
    buttons[0].text_reflection = True
    buttons[0].x = gs.get_width() - buttons[0].text.get_width() - 8
    buttons[0].y = gs.get_height() - buttons[0].text.get_height() - 8
    mbut = []
    about_ = json.loads(open('data/json/about.json').read())
    creator_text_part_1 = font8.render('Developer: ', True, (255, 255, 250))
    creator_text_part_2 = font8.render(str(about_['creator']), True, (50, 50, 250))

    creator_text = pygame.Surface((creator_text_part_1.get_width() + creator_text_part_2.get_width() + 5,
                                   creator_text_part_1.get_height()))
    creator_text.blit(creator_text_part_1, (0, 0))
    creator_text.blit(creator_text_part_2, (creator_text_part_1.get_width() + 5, 0))

    creator_text_shade = creator_text.copy()
    creator_text_shade.set_alpha(120)

    game_page_available = about_['type']
    version_color = about_['version_color']
    type_text_color = (200, 200, 50)
    try:
        float(about_['version'])
    except:
        game_page_available = 'invalid'
        version_color = (249, 50, 50)
        type_text_color = (200, 10, 10)

    version_text_part_1 = font8.render('Version: ', True, (255, 255, 250))
    version_text_part_2 = font8.render(str(about_['version']), True, version_color)
    version_text_part_3 = font4.render(game_page_available, True, type_text_color)

    version_text = pygame.Surface((version_text_part_1.get_width() + version_text_part_2.get_width()
                                   + version_text_part_3.get_width() + 14,
                                   version_text_part_1.get_height()))
    version_text.blit(version_text_part_1, (0, 0))
    version_text.blit(version_text_part_2, (version_text_part_1.get_width() + 5, 0))
    version_text.blit(version_text_part_3, (version_text_part_1.get_width() + version_text_part_2.get_width() + 14, 0))

    version_text_shade = version_text.copy()
    version_text_shade.set_alpha(120)

    tools_text_part_1 = font8.render('Tools: ', True, (255, 255, 250))
    tools_text_part_2 = font8.render(about_["tools"], True, (50, 255, 250))

    tools_text = pygame.Surface((tools_text_part_1.get_width() + tools_text_part_2.get_width() + 10,
                                 tools_text_part_1.get_height()))
    tools_text.blit(tools_text_part_1, (0, 0))
    tools_text.blit(tools_text_part_2, (tools_text_part_1.get_width() + 7, 0))

    tools_text_shade = tools_text.copy()
    tools_text_shade.set_alpha(120)

    version_text_x = -256
    creator_text_x = -512
    tools_text_x = -1024

    for _ in range(random.randint(25, 30)):
        stars.append([[random.randint(0, gs.get_width()), random.randint(0, gs.get_height())],
                      random.randint(2, 5), random.randint(2, 4)])

    while not done:
        gs.fill((0, 0, 0))
        mx, my = pygame.mouse.get_pos()
        mx //= 2
        my //= 2

        for star in stars:
            pygame.draw.circle(gs, (255, 255, 255), star[0], star[1])
            star[0][0] += star[2] / delta
            if star[0][0] > gs.get_width():
                stars.remove(star)
                stars.append([[0, random.randint(0, gs.get_height())], random.randint(2, 5), random.randint(2, 4)])

        for i in pygame.event.get():
            if i.type == QUIT:
                quit(0)

            if i.type == KEYDOWN:
                if i.key == K_ESCAPE:
                    sound.play_button_pressed_sound()
                    menu()

            if i.type == MOUSEBUTTONDOWN:
                mbut.append(i.button)
            elif i.type == MOUSEBUTTONUP and i.button in mbut:
                mbut.remove(i.button)

        sc.blit(pygame.transform.scale(gs, sc.get_size()), (0, 0))
        pygame.display.update()
        clock.tick()

        delta = clock.get_fps() / 90
        if delta == 0:
            delta = 1


if __name__ == "__main__":
    menu()
