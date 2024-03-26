import pygame
import numpy as np
import pylab
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

h = 1        # spatial step width
k = 1        # time step width
c = 0.5      # wave velocity
dimx = dimy = int(600)
tau = ( (c*k) / h )**2
kappa = k * c / h  
cellsize = 1
period = 3
pulse_frequency = (1/period)*0.4
colour_amp = 20

# Place Obstacles
alpha = np.zeros((dimx, dimy))
alpha[:] = tau

# Define the center and radius of the circular obstacle (feedwell boundary)
center = (dimx/2, dimy/2)
inner_rad = 50
outer_rad = 55

center_x = dimx/2 # x-coordinate of the center of the circle
center_y = dimy/2  # y-coordinate of the center of the circle
R_max = 200         # radius of outer circle
R_min = 50          # radius of inner circle

# Iterate through each point in the simulation domain
for i in range(dimx):
    for j in range(dimy):
        # Calculate the distance between the current point and the center of the circle
        distance_to_center = np.sqrt((i - center_x) ** 2 + (j - center_y) ** 2)
        
        # Check if the distance is greater than the radius R_max
        if distance_to_center > R_max:
            # Mark the point as an obstacle
            alpha[i, j] = 0  # Set the obstacle value as desired (e.g., 0)
        
        ''' This is just going to set everything but the origin to zero... 
        # Check if the distance is less than the radius R_min
        if distance_to_center < R_min:
            # Mark the point as an obstacle
            alpha[i, j] = 0  # Set the obstacle value as desired (e.g., 0)
        '''

def update(u):
    u[2] = u[1]
    u[1] = u[0]

    # Solving the Wave Equation
    u[0, 2:dimx-2, 2:dimy-2]  = alpha[2:dimx-2, 2:dimy-2] * ( -  1 * u[1, 2:dimx-2, 0:dimy-4] + 16 * u[1, 2:dimx-2, 1:dimy-3]
                                          -  1 * u[1, 0:dimx-4, 2:dimy-2] + 16 * u[1, 1:dimx-3, 2:dimy-2] 
                                          - 60 * u[1, 2:dimx-2, 2:dimy-2] + 16 * u[1, 3:dimx-1, 2:dimy-2]
                                          -  1 * u[1, 4:dimx,   2:dimy-2] + 16 * u[1, 2:dimx-2, 3:dimy-1] 
                                          -  1 * u[1, 2:dimx-2, 4:dimy] ) / 12 \
                                + 2*u[1, 2:dimx-2, 2:dimy-2] -   u[2, 2:dimx-2, 2:dimy-2]                                     

    # Absorbing Boundary Conditions
    u[0, dimx-3:dimx-1, 1:dimy-1] = u[1,  dimx-4:dimx-2, 1:dimy-1] + (kappa-1)/(kappa+1) * (u[0,  dimx-4:dimx-2, 1:dimy-1] - u[1, dimx-3:dimx-1,1:dimy-1])
    u[0,           0:2, 1:dimy-1] = u[1,            1:3, 1:dimy-1] + (kappa-1)/(kappa+1) * (u[0,            1:3, 1:dimy-1] - u[1,0:2,1:dimy-1])
    u[0, 1:dimx-1, dimy-3:dimy-1] = u[1,  1:dimx-1, dimy-4:dimy-2] + (kappa-1)/(kappa+1) * (u[0, 1:dimx-1,  dimy-4:dimy-2] - u[1, 1:dimx-1, dimy-3:dimy-1])
    u[0, 1:dimx-1, 0:2] = u[1, 1:dimx-1, 1:3] + (kappa-1)/(kappa+1) * (u[0, 1:dimx-1, 1:3] - u[1, 1:dimx-1, 0:2])

def main():
    pygame.init()
    display = pygame.display.set_mode((dimx*cellsize, dimy*cellsize))
    pygame.display.set_caption("Solving the 2d Wave Equation")

    u = np.zeros((3, dimx, dimy))
    pixeldata = np.ones((dimx, dimy, 3), dtype=np.uint8)

    #Overlay custom pixel changes for visuals:
    for i in range(dimx):
        for j in range(dimy):
            distance_to_center = np.sqrt((i - center[0]) ** 2 + (j - center[1]) ** 2)
            if distance_to_center < (R_max+5) and distance_to_center > R_max:
                pixeldata[i, j, :] = [255, 255, 255] #Set obstacle

            if distance_to_center < (R_min+5) and distance_to_center > R_min:
                pixeldata[i, j, :] = [255, 255, 255] #Set obstacle

    # Create initial figure and axis for 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x, y = np.meshgrid(np.arange(dimx), np.arange(dimy))
    surface = ax.plot_surface(x, y, pixeldata[:,:,1], cmap='viridis')
    # Set the scale of the axes
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 600)
    ax.set_zlim(0, 200)

    tick = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        tick += 1
        u[0, dimx//2, dimy//2] = np.sin(tick * pulse_frequency) * colour_amp  # Set initial circular wave
        update(u)

        # Set the color intensity based on the positive amplitude of the wave, clamping it between 0 and 255
        pixeldata[1:dimx, 1:dimy, 1] = np.clip((u[0, 1:dimx, 1:dimy] > 0) * 10 * u[0, 1:dimx, 1:dimy] + u[1, 1:dimx, 1:dimy] + u[2, 1:dimx, 1:dimy], 0, 255)
        # Set the color intensity based on the negative amplitude of the wave, clamping it between 0 and 255
        pixeldata[1:dimx, 1:dimy, 2] = np.clip((u[0, 1:dimx, 1:dimy] <= 0) * -10 * u[0, 1:dimx, 1:dimy] + u[1, 1:dimx, 1:dimy] + u[2, 1:dimx, 1:dimy], 0, 255) 
        
        #''' 2D PLOT CODE SECTION
        #Display the surface
        surf = pygame.surfarray.make_surface(pixeldata)
        display.blit(pygame.transform.scale(surf, (dimx * cellsize, dimy * cellsize)), (0, 0))
        #pygame.Color(50, 100, 100, 255)

        # Display current time at the bottom of the plot
        clock = pygame.time.Clock()  # For controlling the frame rate
        # Font settings
        time_font = pygame.font.Font(None, 20)  # Choose a font and size
        text_color = (255, 255, 255)  # Text color

        current_time = pygame.time.get_ticks() / 1000  # Convert time to seconds
        time_text = time_font.render(f"Time: {current_time:.2f}s", True, text_color)  # Render time text
        display.blit(time_text, (10, dimy * cellsize - 40))  # Adjust position as needed
        
        
        clock.tick(30)  # Limit frame rate to 30 frames per second

        # Display the title at the top center
        title_font = pygame.font.SysFont(None, 36)
        title_text = title_font.render("2D Wave Equation Simulation - Even Sloshing", True, (255, 255, 255))
        text_rect = title_text.get_rect(center=(dimx * cellsize // 2, 30))
        display.blit(title_text, text_rect)

        pygame.display.update()
        #'''

        ''' 3D PLOT CODE SECTION
        # Update the data for the 3D surface plot
        surface.remove()  # Remove the previous surface
        surface = ax.plot_surface(x, y, pixeldata[:,:,1]/10, cmap='viridis')  # Plot the updated surface
        plt.pause(0.001)  # Pause to allow the plot to update
        '''
if __name__ == "__main__":
    main()