"""A module for time logging functionality."""
import time

class TimeLogger:
    """A class containing time logging functionality."""

    def __init__(self, _nb_iterations: int, refresh_rate_sec: float=1):
        self._nb_iterations = _nb_iterations
        self._refresh_rate = refresh_rate_sec
        self._prnt_str = ''
        self._start_time: float = 0
        self._time_prev: float = 0
        self._nb_its_done: int = 0

    def start(self) -> None:
        """Initialize the timer."""
        self._start_time = time.time()
        self._time_prev = self._start_time-1
        self._nb_its_done = 0

    def iterate(self) -> None:
        """Proceed the timer with one iteration."""
        self._nb_its_done += 1
        time_now = time.time()
        if time_now - self._time_prev > self._refresh_rate:
            self._time_prev = time_now
            ratio_done = int(self._nb_its_done / self._nb_iterations * 100 + 0.5)
            time_done = time_now - self._start_time
            print(' ' * len(self._prnt_str), end='\r')
            self._prnt_str = f' {ratio_done:03d} % |{"#" * ratio_done}{" " * (100 - ratio_done)}| '
            time_per_it = time_done / self._nb_its_done
            time_remaining = (self._nb_iterations - self._nb_its_done) * time_per_it
            hours = f'{int(time_remaining / 3600):02d}'
            mins = f'{int(time_remaining/60)%60:02d}'
            secs = f'{int(time_remaining%60):02d}'
            self._prnt_str += f'{hours}:{mins}:{secs} remaining'
            print(self._prnt_str, end='\r')

    def log(self, message: str) -> None:
        """Log the given message."""
        self.clear()
        print(message)

    def clear(self) -> None:
        """Clear the terminal after the iteration has finished."""
        print(' ' * len(self._prnt_str), end='\r')
        self._prnt_str = ''