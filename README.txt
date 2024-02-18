A class to simulate vivid particle movements based on custom interaction rules

Applied Python distribution and libraries:
Python 3.10.5
pygame (hier: 2.5.2)
numpy (hier 1.26.3)

The Particle class takes the following arguments:
- True for running the main loop
- screen width
- screen height
- particle color as rgb value
- number of particles to create

create_particles
The function create_particles will reaturn a numpy array of the lenth n_particles (number of particles to create) which contains the rgb values of the corresponding color in index positions 0-2. 
Index positions 3 and 4 contain the partcicle positions while 5 and 6 contain the velocities. Position values are initialized as random values, velocities are set to zero.

draw_particles
This funcion will draw the particles on the screen

attraction rules
calculates the interactions between particles and thereof new particle positions employing numpy functionalities to make the code efficient.

game_loop
the main simulation loop