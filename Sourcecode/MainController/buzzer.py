import RPi.GPIO as GPIO
import time

from settings import BUZZ_DURATION, BUZZ_SLEEP
from daemon_threads import start_daemon_timer

class Buzzer(object):
    """
    Buzzer
    """
    def __init__(self, enabled=True):
        super(Buzzer, self).__init__()
        self.buzzer_pin = 21
        self.buzzer_timer = start_daemon_timer(0, None, start=False)
        self.enabled = enabled
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)

    def buzzer_on(self):
        """
        Turn buzzer on
        """
        GPIO.output(self.buzzer_pin, True)

    def buzzer_off(self, amount=0):
        """
        Turn buzzer off, if amount > 0 then start timer to turn buzzer on again
        """
        GPIO.output(self.buzzer_pin, False)
        if amount > 0:
            self.buzzer_timer = start_daemon_timer(BUZZ_SLEEP, self.buzz, args=(amount,))

    def buzz(self, amount=1):
        """
        Check if enabled, turn buzzer on and start timer to turn it off.
        Decrease given amount, so when buzzer turns off it can start a new timer
        """
        if not self.enabled:
            return

        self.buzzer_on()
        amount -= 1
        self.buzzer_timer.cancel()
        self.buzzer_timer = start_daemon_timer(BUZZ_DURATION, self.buzzer_off, args=(amount,))

    def set_enabled(self, enabled):
        """
        Enable the buzzer, buzz once to let the user know its enabled
        """
        self.enabled = enabled
        if enabled:
            self.buzz()

    def kill(self):
        """
        Kill the buzzer, cancel running timer, turn buzzer of and clean GPIO
        """
        self.buzzer_timer.cancel()
        GPIO.output(self.buzzer_pin, False)
        GPIO.cleanup()


if __name__ == '__main__':
    """
    Test buzzer, buzz 4 times or given amount (max 10)
    """
    import sys
    import time

    buzzer = Buzzer()

    buzz_amount = 4
    if len(sys.argv) is 2:
        buzz_amount = int(sys.argv[1])

    buzzer.buzz(buzz_amount)

    # Sleep so buzz 
    time.sleep(buzz_amount * (BUZZ_SLEEP + BUZZ_DURATION) * 1.1)
    buzzer.kill()