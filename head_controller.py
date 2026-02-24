import time
import pigpio


class HeadController:
    """
    Contrôleur simple de servo pour la tête.
    On pilote en microsecondes (µs) : typiquement 1000..2000.
    """

    def __init__(self, gpio_pin: int = 18, start_us: int = 1500):
        self.gpio_pin = gpio_pin
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Impossible de se connecter à pigpiod. Lance: sudo systemctl start pigpiod")

        self.current_us = start_us
        self.pi.set_servo_pulsewidth(self.gpio_pin, self.current_us)

    def move_to(self, target_us: int, step_us: int = 10, step_delay: float = 0.02):
        """
        Déplace le servo en douceur vers target_us.
        - step_us: taille des petits pas (plus petit = plus doux)
        - step_delay: pause entre pas (plus petit = plus rapide)
        """
        target_us = int(target_us)
        print(f"[head_controller] move_to: {self.current_us} -> {target_us}")

        while self.current_us != target_us:
            if self.current_us < target_us:
                self.current_us = min(self.current_us + step_us, target_us)
            else:
                self.current_us = max(self.current_us - step_us, target_us)

            self.pi.set_servo_pulsewidth(self.gpio_pin, self.current_us)
            time.sleep(step_delay)

        print(f"[head_controller] reached: {self.current_us}")
    def stop(self):
        """Coupe le signal (évite de maintenir le servo sous tension en permanence)."""
        self.pi.set_servo_pulsewidth(self.gpio_pin, 0)
        self.pi.stop()


if __name__ == "__main__":
    # Petit test manuel
    head = HeadController(gpio_pin=18, start_us=1500)
    try:
        head.move_to(1200)  # gauche
        time.sleep(0.5)
        head.move_to(1800)  # droite
        time.sleep(0.5)
        head.move_to(1500)  # centre
        time.sleep(0.5)
    finally:
        head.stop()
        print("HeadController: terminé.")
