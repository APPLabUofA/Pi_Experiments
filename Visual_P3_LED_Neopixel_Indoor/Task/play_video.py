import pygame

FPS = 60

pygame.init()
clock = pygame.time.Clock()
movie = pygame.movie.Movie('/home/pi/research_experiments/Experiments/Visual_P3_LED_Neopixel_Indoor/Task/Bike_Video.mp4')
screen = pygame.display.set_mode(movie.get_size())
movie_screen = pygame.Surface(movie.get_size()).convert()

movie.set_display(movie_screen)
movie.play()


playing = True
while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            movie.stop()
            playing = False

    screen.blit(movie_screen,(0,0))
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
