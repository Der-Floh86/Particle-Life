"""
A class to simulate vivid particle movements based on custom interaction rules
The project was inspired by https://github.com/CapedDemon/Particle-life
Thanks a lot for the great idea and the valuable inspiration.
The code was modified making extensive use of numpy functionalities to make it more efficient and run smoother.
"""

import pygame
import numpy as np


class ParticleSimulation:
    def __init__(self, running, width, height, color, n_particles):
        pygame.init()
        self.width = width
        self.height = height
        self.n_teilchen = n_particles
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(color)
        self.running = running
        self.clock = pygame.time.Clock()

        # Farben
        self.blue = (0, 0, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.yellow = (255, 255, 0)

        # leere Teilchenvariablen
        self.yellow_particles = None
        self.blue_particles = None
        self.green_particles = None
        self.red_particles = None

        pygame.display.set_caption("Particle Life")
        pygame.display.update()

        # Start der Simulation
        self.game_loop(n_particles)

    def create_particles(self, n_particles, p_color):
        """
        Erzeugt ein Numpy-Array der Länge "n_particles" (Zahl der zu simulierenden Teilchen der betreffenden Farbe) mit 7
        Feldern in der 2. Dimension. Die ersten 3 enthalten den Farbwert (RGB), Nr. 4 u. 5 die Position (x, y) und
        6 u. 7 die Geschwindigkeit. Die Positionen werden mit Zufallszahlen zwischen 1 und der Breite bzw Höhe des
        Displays initialisiert, die Anfangsgeschwindigkeiten auf 0 gesetzt.
        :param n_particles: Zahl der Teilchen
        :param p_color: Teilchenfarbe als RGB-Wert-Tuple
        :return: Numpy-Array mit Teilchenfarbe und -positionen
        """
        particles = np.zeros((n_particles, 7))

        for i in range(3):
            particles[:, i] = p_color[i]

        particles[:, 3] = np.random.randint(0, self.width - 1, n_particles)
        particles[:, 4] = np.random.randint(0, self.height - 1, n_particles)
        return particles

    def draw_particles(self, particle_array):
        """
        Erzeugt eine grafische Repräsentation der simulierten Teilchen auf dem pygame-Screen.
        :param particle_array:
        """
        for ptl in particle_array:
            color = ptl[0:3]
            x = ptl[3]
            y = ptl[4]
            pygame.draw.circle(self.screen, color, (x, y), 1)

    def particle_interaction(self, particles_1, particles_2, g=1.0, r_eq=40, box='cyclic'):
        """
        Berechnet die Kräfte zwischen den Teilchen in den Arrays particles_1 und particles_2, daraus resultierende
        Änderungen in Geschwindigkeit und Position für teilchen1 und liefert das modifizierte Array particles_1 zurück.

        1. Berechnung der Teilchenabstände in x- bzw. y-Richtung
        x-Koordinaten von particles_1 bzw. particles_2 werden jeweils in 2D-Arrays namens x1 bzw. x2 abgelegt. Die erste
        Dimension entspricht der jeweiligen Teilchenzahl, die Zweite der Teilchenzahl des jeweils anderen Arrays.
        In dieser Dimension werden die betreffenden Werte gebroadkastet, sodass anschließend durch Differenzbildung
        (x2-x1 bzw. y2-y1) ein 2D-Array mit den Abständen in x- bzw. y-Richtung erhalten wird.
        Damit nicht n_particle mal dieselbe Differenz berechnet wird, sondern die Differenz zwischen jedem Partikel
        aus particle_1 und jedem Partikel aus particle_2, wird zuvor das Array x2 bzw y2 um 90° gedreht. Hierfür wird
        die Funktion swapaxes verwendet. Das Ergebnis der Differenzbildung wird in einem 3D-Array namens d abgelegt.
        x-Komponenten: d[:, :, 0]; y-Komponenten: d[:, :, 0]

        2. Berechnung der Einheitsvektoren zwischen den Teilchen
        Die Beträge der so erzeugten Abstandsvektoren werden in einem 2D-Array namens d_abs abgelegt. Division der in d
        abgelegten Komponenten durch d_abs normiert die Vektoren auf den Betrag von 1.

        3. Berechnung der Kräfte zwischen den Teilchen
        Der Parameter g entspricht einer Beschleunigungskonstanten zwischen den Teilchen. (Da die Teilchen masselos
        sind, macht eine Unterscheidung zwischen Kraft und Beschleunigung hier keinen Sinn.) Im Falle einer repulsiven
        Wechselwirkung (g < 0) ist die Kraft umgekehrt proportional zum Teilchenabstand d_abs und wird einfach durch
        Bildung des Quotienten g/d_abs berechnet. Im Falle einer anziehenden Wechselwirkung wird ein
        Gleichgewichtsabstand r_eq angenommen.
        Ist d_abs > r_eq, wird wiederum der Quotient gebildet. Unterschreitet der Abstand d_abs jedoch den
        Gleichgewichtsabstand r_eq, wird die Wechselwirkung als Abstoßung modelliert, indem der Quotient mit -1
        multipliziert wird. Das Ergebnis ist eine Matrix names f, die Kräfte zwischen allen Partikeln in Abhängigkeit
        von deren Abstand d_abs als Skalarwert enthält.

        4. Berechnung der neuen Geschwindigkeiten
        Um den Kräften bzw. Beschleunigungen eine Richtung zu verleihen (die Kräfte wirken entlang der Einheitsvektoren)
        werden deren Komponenten im Array d mit der Matrix f multipliziert. Die resultierenden Beschleunigungen werden
        für jedes Teilchen aufsummiert und zu den Geschwindigkeitskomponenten im array particles_1 addiert.
        Da die Annahmen über die Wechselwirkungen in dieser Simulation unphysikalisch sind (die Kräfte wirken nicht
        paarweise und nehmen auch nicht mit dem Quadrat des Abstands ab) gelten hier die üblichen Erhaltungssätze nicht,
        sodass dem System durch Multiplikation der Kraftkomponenten mit 0.5 und der Geschwindigkeiten mit 0.995
        künstlich Energie entzogen wird. Dieser Parameter kann bzw. muss in Abhängigkeit von der Teilchendichte,
        der asymmetrie der Wechselwirkungen in der Liste "interactions" und nach gewünschter Lebhaftigkeit der
        Simulation variiert werden.

        der Parameter box:
        Bei Angabe 'repulsive' finden elastische Stöße der Teilchen an den Rändern der Simulationszelle (d. h. des
        Bildschirms) statt. Die Angabe 'cyclic' bewirkt, dass Teilchen, die die Grenzen überschreiten, auf der
        gegenüberliegenden Seite wieder eintreten. Die Wechselwirkungen werden jedoch nicht über diese Grenzfläche
        berechnet.

        :param particles_1: Array mit Teilchenfarben (0-2) Positionen (3-4) und Geschwindigkeiten (5-6) der Teilchen
        :param particles_2: Array mit Teilchenfarben (0-2) Positionen (3-4) und Geschwindigkeiten (5-6) der Teilchen
        :param g: Kraftkonstante (>0: anziehende Ww, <0: repulsive WW)
        :param r_eq: Gleichgewichtsabstand
        :param box: 'cyclic': Zyklische Simulationsbox, 'repulsive': Elastische Stöße an den Wänden
        :return: particles_1 (np-Array mit modifizierten Geschwindigkeits- und Positionsangaben)
        """
        if box not in ['repulsive', 'cyclic']:
            print(f'Kein Gültiger Wert für den Parameter "box" übergeben: {box}'
                  'Der Wert wird auf "cyclic" gesetzt')
            box = 'cyclic'

        # leere Arrays
        # zur Aufnahme der Abstände in x-Richtung([0] und y-Richtung([1])
        d = np.zeros((particles_1.shape[0], particles_2.shape[0], 2))

        # zur Aufnahme der Koordinaten in x- und y-Richtung
        x1 = np.zeros((particles_1.shape[0], particles_2.shape[0]))
        x2 = np.zeros((particles_2.shape[0], particles_1.shape[0]))
        y1 = np.zeros((particles_1.shape[0], particles_2.shape[0]))
        y2 = np.zeros((particles_2.shape[0], particles_1.shape[0]))

        # Broadkasten der Koordinaten in x- und y-Richtung
        x1[:, :] = particles_1[:, 3]
        x2[:, :] = particles_2[:, 3]
        x2 = np.swapaxes(x2, 0, 1)

        y1[:, :] = particles_1[:, 4]
        y2[:, :] = particles_2[:, 4]
        y2 = np.swapaxes(y2, 0, 1)

        # Komponentenweise Berechnung der Teilchenabstände
        d[:, :, 0] = x2 - x1
        d[:, :, 1] = y2 - y1
        d[d == 0] = np.nan

        # Normierung der Abstandsvektoren
        d_abs = np.sqrt(np.square(d[:, :, 0]) + np.square(d[:, :, 1]))
        d[:, :, 0] /= d_abs
        d[:, :, 1] /= d_abs

        # Berechnung der Wechselwirkungen
        if g > 0:
            # Anziehende WW: Anziehung nur, sofern Abstand d_abs > Gleichgewichtsabstand r_eq, andernfalls Abstoßung
            f = np.zeros(d_abs.shape)
            mask_1 = np.zeros(d_abs.shape).astype(bool)
            mask_2 = np.zeros(d_abs.shape).astype(bool)
            mask_1[d_abs > r_eq] = True
            mask_2[d_abs < r_eq] = True
            f[mask_1] = g / d_abs[mask_1]
            f[mask_2] = - g / d_abs[mask_2]

        else:
            # repulsive WW
            f = g / d_abs

        # Multiplikation der Einheitsvektoren mit der WW-Matrix
        d[:, :, 0] *= f
        d[:, :, 1] *= f
        np.nan_to_num(d, copy=False)

        # Aufsummieren sämtlicher WW für jedes Teilchen
        fx = np.sum(d[:, :, 0], axis=0)
        fy = np.sum(d[:, :, 1], axis=0)

        # Addition der WW zu bestehenden Geschwindigkeiten, Berechnung neuer Ortspositionen
        # Da die hier gemachten Annahmen unphysikalisch sind, gelten die Erhaltungssätze nicht.
        particles_1[:, 5] += fx * 0.5
        particles_1[:, 6] += fy * 0.5
        particles_1[:, 5] *= 0.995
        particles_1[:, 6] *= 0.995

        particles_1[:, 3] += particles_1[:, 5]
        particles_1[:, 4] += particles_1[:, 6]

        # Berechnung des Partikelverhaltens an den Bilschirmrändern
        if box == 'repulsive':
            # elastischer Stoß
            particles_1[:, 5][particles_1[:, 3] >= self.width] *= -1
            particles_1[:, 5][particles_1[:, 3] <= 0] *= -1
            particles_1[:, 6][particles_1[:, 4] >= self.height] *= -1
            particles_1[:, 6][particles_1[:, 4] <= 0] *= -1

        elif box == 'cyclic':
            # Wiedereintritt am gegenüberliegenden Bildschirmrand
            particles_1[:, 3][particles_1[:, 3] >= self.width] -= self.width
            particles_1[:, 3][particles_1[:, 3] <= 0] += self.width
            particles_1[:, 4][particles_1[:, 4] >= self.height] -= self.height
            particles_1[:, 4][particles_1[:, 4] <= 0] += self.height

        return particles_1

    def game_loop(self, n_teilchen=200):
        # Erzeugung der Teilchen
        self.yellow_particles = self.create_particles(n_particles=n_teilchen, p_color=self.yellow)
        self.blue_particles = self.create_particles(n_particles=n_teilchen, p_color=self.blue)
        self.green_particles = self.create_particles(n_particles=n_teilchen, p_color=self.green)
        self.red_particles = self.create_particles(n_particles=n_teilchen, p_color=self.red)

        # Prüfung auf Abbruch durch Benutzer
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Erzeugung eines neuen Bildes
            self.screen.fill(0)
            self.draw_particles(self.yellow_particles)
            self.draw_particles(self.blue_particles)
            self.draw_particles(self.green_particles)
            self.draw_particles(self.red_particles)
            pygame.display.update()

            particles = [self.yellow_particles, self.blue_particles, self.green_particles, self.red_particles]

            # Angabe der Wechselwirkungen zwischen den Teilchensorten particle_2 -> particle_1
            # Z. B. Zeile 1: Alle WW, die die gelben Teilchen bei Interaktion mit sich selbst und den jeweils anderen
            # Teilchensorten erfahren. Ein Wert > 0 bedeutet Anziehung, ein Wert < 0 Abstoßung.
            # Die Werte können beliebig variiert werden.
            # Wichtig: Die Matrix ist nicht symmetrisch. Das ist zwar unphysikalisch, hier aber beabsichtigt.

            # particles_2: yellow  blue   green  red   particles_1:
            interactions = [[0.1, -0.01, -0.03, 0.01],  # yellow
                            [0.2, -0.02, -0.02, 0.01],  # blue
                            [0.1, -0.02, 0.05, -0.01],  # green
                            [0.09, -0.1, 0.1, 0.05]]    # red

            # Berechnung der neuen Teilchenpositionen anhand der hier angegebenen Kraftkonstanten
            for n1, particles_1 in enumerate(particles):
                for n2, particles_2 in enumerate(particles):
                    particles_1 = self.particle_interaction(particles_1, particles_2, interactions[n1][n2])

            self.clock.tick(60)
        pygame.quit()


def main():
    particle_life = ParticleSimulation(True, 1400, 1000, (0, 0, 0), 200)


if __name__ == "__main__":
    main()
