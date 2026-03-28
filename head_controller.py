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
        Déplace le servo avec un profil simple plus naturel :
        départ doux, milieu plus rapide, arrivée douce.
        """
        target_us = int(target_us)
        start_us = self.current_us
        distance = target_us - start_us

        print(f"[head_controller] move_to: {self.current_us} -> {target_us}")

        if distance == 0:
            print(f"[head_controller] reached: {self.current_us}")
            return

        total_steps = max(1, abs(distance) // max(1, step_us))

        for i in range(1, total_steps + 1):
            progress = i / total_steps

            # Courbe simple "ease in / ease out"
            eased = 6 * (progress ** 5) - 15 * (progress ** 4) + 10 * (progress ** 3)

            next_us = int(start_us + distance * eased)

            if next_us != self.current_us:
                self.current_us = next_us
                self.pi.set_servo_pulsewidth(self.gpio_pin, self.current_us)

            time.sleep(step_delay)

        self.current_us = target_us
        self.pi.set_servo_pulsewidth(self.gpio_pin, self.current_us)

        print(f"[head_controller] reached: {self.current_us}")

    def stop(self):
        """Coupe le signal (évite de maintenir le servo sous tension en permanence)."""
        self.pi.set_servo_pulsewidth(self.gpio_pin, 0)
        self.pi.stop()


if __name__ == "__main__":
    head = HeadController(gpio_pin=18, start_us=1500)
    try:
        head.move_to(1200)
        time.sleep(0.5)
        head.move_to(1800)
        time.sleep(0.5)
        head.move_to(1500)
        time.sleep(0.5)
    finally:
        head.stop()
        print("HeadController: terminé.")
