A class to simulate vivid particle movements based on custom interaction rules

Applied Python distribution and libraries:
Python 3.10.5
pygame (hier: 2.5.2)
numpy (hier 1.26.3)

The ParticleSimulation class takes the following arguments:
- True for running the main loop
- screen width
- screen height
- particle color as rgb value
- number of particles to create

create_particles
The function create_particles will return a numpy array of the length n_particles (number of particles to create) which
contains the rgb values of the corresponding color in index positions 0-2.
Index positions 3 and 4 contain the particle positions in x- and y-direction,respectively while pos 5 and 6 contain the
x- and y-velocities. Position values are initialized as random values, velocities are set to zero.

draw_particles
This function will draw the particles on the screen

particle_interaction
calculates the interactions between particles and thereof new particle positions employing numpy functionalities to make
the code more efficient and run smoother.

game_loop
the main simulation loop

The project was inspired by https://github.com/CapedDemon/Particle-life
Thanks a lot for the great idea and the valuable inspiration.
