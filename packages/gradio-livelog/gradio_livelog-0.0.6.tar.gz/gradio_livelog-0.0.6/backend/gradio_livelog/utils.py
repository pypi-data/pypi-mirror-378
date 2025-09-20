# backend/gradio_livelog/utils.py

import io
import logging
import queue
import re
import time
from contextlib import contextmanager
from typing import Callable, List, Iterator, Dict, Any, Literal, Optional, Union

class _QueueLogHandler(logging.Handler):
    """A private logging handler that directs log records into a queue."""
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord):
        self.log_queue.put(record)

@contextmanager
def capture_logs(
    log_name: Union[str, List[str], None] = None, 
    log_level: int = logging.INFO,
    disable_console: bool = False
) -> Iterator[Callable[[], List[logging.LogRecord]]]:
    """
    A context manager to capture logs from one or more specified loggers.

    This function temporarily attaches a thread-safe, queue-based handler to the
    target logger(s) to intercept all log messages. If `disable_console` is True,
    it will also temporarily remove other console-based StreamHandlers from the
    target loggers to prevent duplicate output to the terminal.

    Args:
        log_name: The name of the logger(s) to capture.
                - `str`: Captures logs from a single named logger.
                - `List[str]`: Captures logs from multiple named loggers.
                - `None` or `""`: Captures logs from the root logger.
        log_level: The minimum level of logs to capture (e.g., `logging.INFO`).
        disable_console: If True, prevents the captured logs from also being
                        printed to the console by other handlers on the same logger.

    Yields:
        A callable function. When this function is called, it returns a list
        of all log records captured since the last time it was called, effectively
        acting as a "get new logs" utility.
        
    Example:
        >>> with capture_logs(log_name=["my_app", "my_library"]) as get_logs:
        ...     logging.getLogger("my_app").info("Starting process.")
        ...     new_logs = get_logs()  # Contains the first log record
        ...     logging.getLogger("my_library").warning("A potential issue.")
        ...     more_logs = get_logs() # Contains only the warning record
    """
    # Step 1: Determine the target loggers based on the `log_name` argument.
    target_loggers: List[logging.Logger] = []
    log_names_to_process = []
    if log_name is None or log_name == "":
        log_names_to_process.append(None) # `None` is the identifier for the root logger
    elif isinstance(log_name, list):
        log_names_to_process.extend(log_name)
    elif isinstance(log_name, str):
        log_names_to_process.append(log_name)
    
    # Get the actual logger objects from their names.
    for name in set(log_names_to_process): # Use set to avoid duplicates
        target_loggers.append(logging.getLogger(name))

    # Step 2: Set up the thread-safe queue and the custom handler.
    log_queue = queue.Queue()
    queue_handler = _QueueLogHandler(log_queue)

    # Step 3: Store the original state of each logger to restore it later.
    original_levels = {logger.name: logger.level for logger in target_loggers}
    original_handlers = {logger.name: logger.handlers[:] for logger in target_loggers}
    
    # Step 4: Modify the target loggers for the duration of the context.
    for logger in target_loggers:
        # Set the desired capture level.
        logger.setLevel(log_level)

        if disable_console:
            # If disabling console, remove all existing StreamHandlers.
            # We keep other handlers (e.g., FileHandler) intact.
            logger.handlers = [
                h for h in logger.handlers if not isinstance(h, logging.StreamHandler)
            ]
        
        # Add our custom queue handler to start capturing logs.
        logger.addHandler(queue_handler)

    # This holds all records captured during the context's lifetime.
    all_captured: List[logging.LogRecord] = [] 
    # This index tracks the last record that was returned to the caller.
    last_returned_index = 0 

    try:
        def get_captured_records() -> List[logging.LogRecord]:
            """
            Retrieves new log records from the queue and returns them.
            This function is what the context manager yields to the user.
            """
            nonlocal last_returned_index
            
            # Drain the queue into our master list of captured records.
            while not log_queue.empty():
                try:
                    record = log_queue.get_nowait()
                    all_captured.append(record)
                except queue.Empty:
                    # This handles a rare race condition where the queue becomes empty
                    # between the `empty()` check and `get_nowait()`.
                    break 
            
            # Slice the master list to get only the new records.
            new_records = all_captured[last_returned_index:]
            # Update the index to the end of the list for the next call.
            last_returned_index = len(all_captured)
            
            return new_records

        # Yield the function to the `with` block.
        yield get_captured_records

    finally:
        # Step 5: Restore the loggers to their original state, ensuring no side effects.
        for logger in target_loggers:
            # Remove our custom handler.
            logger.removeHandler(queue_handler)
            
            # Restore the original log level.
            if logger.name in original_levels:
                logger.setLevel(original_levels[logger.name])
            
            # If we disabled the console, restore the original handlers.
            if disable_console and logger.name in original_handlers:
                # It's safest to clear handlers and then re-add the originals.
                logger.handlers = []
                for handler in original_handlers[logger.name]:
                    logger.addHandler(handler)
                    
class Tee(io.StringIO):
    """
    A file-like object that acts like the Unix 'tee' command.
    It writes to multiple file-like objects simultaneously.
    """
    def __init__(self, *files):
        """
        Initializes the Tee object.
        Args:
            *files: A variable number of file-like objects (e.g., sys.stderr,
                    a TqdmToQueueWriter instance, etc.).
        """
        super().__init__()
        self.files = files

    def write(self, s: str) -> int:
        """
        Writes the string 's' to all managed files.
        """
        for f in self.files:
            f.write(s)
            # Some file-like objects, like the console, might need to be flushed.
            if hasattr(f, 'flush'):
                f.flush()
        return len(s)

    def flush(self):
        """Flushes all managed files."""
        for f in self.files:
            if hasattr(f, 'flush'):
                f.flush()
class TqdmToQueueWriter(io.StringIO):
    """
    A custom, thread-safe, file-like object that intercepts tqdm's output.

    This class is designed to be passed to a `tqdm` instance (or a library
    that uses `tqdm`, like `diffusers`) via its `file` argument. It uses a
    regular expression to parse the formatted progress string in real-time.

    It extracts key metrics:
    - The iteration rate value (e.g., 2.73).
    - The rate unit ("it/s" or "s/it").
    - Any additional status information that follows the rate.

    The extracted data is packaged into a dictionary and put onto a
    `queue.Queue`, allowing a consumer thread (like a Gradio UI thread)
    to receive real-time progress data from a worker thread.
    """
    def __init__(self, rate_queue: queue.Queue):
        """
        Initializes the writer with a queue for communication.

        Args:
            rate_queue (queue.Queue): The thread-safe queue to which the
                                      extracted rate data will be sent.
        """
        super().__init__()
        self.rate_queue = rate_queue
        self.rate_regex = re.compile(
            # Optional Rate and Unit (e.g., "2.05s/it")
            r"(?:(\d+\.?\d*)\s*(it/s|s/it))?"
            # Optional ETA (e.g., "<00:53")
            r".*?(?:<(\d{2}:\d{2}))?"
            # Optional final comma and the rest of the string
            r"(?:,\s*(.*))?$"
        )

    def write(self, s: str) -> int:
        """
        This method is called by `tqdm` whenever it updates the progress bar.
        It receives the full, formatted progress string.

        Args:
            s (str): The string output from `tqdm` (e.g., "75%|...| 2.73it/s, ...").

        Returns:
            int: The number of characters written, as required by the file-like
                 object interface.
        """
        match = self.rate_regex.search(s)
        rate_info = {}
        if match:
            # Group 1: rate, Group 2: unit
            if match.group(1) and match.group(2):
                try:
                    rate_info["rate"] = float(match.group(1))
                    rate_info["unit"] = match.group(2)
                except ValueError:
                    pass
            
            # Group 3: ETA
            if match.group(3):
                rate_info["eta"] = match.group(3)

            # Group 4: The rest of the string
            if match.group(4):
                # Clean up the extra info
                extra = match.group(4).strip()
                if extra.startswith('[') and extra.endswith(']'):
                    extra = extra[1:-1]
                rate_info["extra_text"] = extra.strip()

        if rate_info:
             self.rate_queue.put(rate_info)

        return len(s)
                    
class ProgressTracker:
    """
    A helper class to track and format progress updates for the LiveLog component.

    This versatile class operates in a hybrid mode for calculating iteration rates:
    1.  **Internal Calculation (Default):** It uses an Exponential Moving Average (EMA)
        to compute a smoothed, stable rate. The unit for this internal calculation
        (`it/s` or `s/it`) can be specified during initialization, making it flexible
        for different types of processes.
    2.  **External Override (Preferred):** It can accept a dictionary of externally
        captured rate data (e.g., from a `tqdm` instance). This provides the most
        accurate possible display by sourcing the rate and its unit directly from
        the process being monitored, overriding any internal calculations.

    The tracker also intelligently "freezes" the last known rate when the process
    status changes to 'success' or 'error', ensuring the final speed remains visible on the UI.
    """
    def __init__(self, total: int, description: str = "Processing...", 
                 smoothing_factor: float = 0.3, 
                 rate_unit: Literal["it/s", "s/it"] = "s/it"):
        """
        Initializes the progress tracker.

        Args:
            total (int): The total number of iterations for the process.
            description (str): A short, fixed description of the task being performed.
            smoothing_factor (float): The EMA smoothing factor used for the internal
                                      rate calculation. A smaller value (e.g., 0.1)
                                      results in smoother but less responsive updates.
            rate_unit (Literal["it/s", "s/it"]): The preferred unit for the
                                                 internal rate calculation when no
                                                 external data is provided. Defaults to "it/s".
        """
        self.total = total
        self.description = description
        self.smoothing_factor = smoothing_factor
        self.preferred_rate_unit = rate_unit  # Stores the user's preference for internal calculations.
        
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_update_item = 0
        
        # State fields that will be updated and returned.
        self.rate = 0.0
        self.rate_unit = self.preferred_rate_unit  # Sets the initial unit.
        self.extra_info = {}
        self.has_started = False

    def update(self, advance: int = 1, status: str = "running", 
               logs: Optional[List[Dict]] = None, log_content: Optional[str] = None, 
               rate_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Updates the tracker's state and returns a dictionary formatted for the frontend.

        This is the core method of the tracker. It's designed to be called repeatedly
        during a long-running process. Its key feature is the ability to handle two
        distinct types of updates:

        1.  **Progress Updates (`advance > 0`):** When `advance` is a positive integer,
            the internal progress counter (`self.current`) is incremented. If no external
            `rate_data` is provided, the tracker will perform its internal rate
            calculation based on the time elapsed since the last advancing update.

        2.  **Text-Only Updates (`advance = 0`):** When `advance` is zero, the progress
            bar's position remains unchanged. This is useful for updating contextual
            information on the UI (e.g., "Processing tile 2/10...") without moving the
            main progress bar. In this mode, the method relies exclusively on the
            `rate_data` dictionary to update text fields like `extra_info`. The internal
            rate calculation is skipped, preserving the last known rate.

        Args:
            advance (int): The number of steps to advance the progress counter.
                           Defaults to 1. If 0, no progress is made, but other
                           information (like `extra_info` from `rate_data`) can still be updated.
            status (str): The current status of the process ("running", "success", "error").
            logs (Optional[List[Dict]]): An optional list of log dictionaries to pass to the frontend.
            log_content (Optional[str]): An optional string to override the fixed description for this update.
            rate_data (Optional[Dict]): A dictionary from an external source (like `tqdm`)
                                        containing keys like 'rate', 'unit', and 'extra'.
                                        If provided, this data will override all internal
                                        rate calculations and text fields.

        Returns:
            Dict[str, Any]: A state dictionary formatted for a frontend component,
                            containing all the necessary information to render the
                            progress bar and associated text.
        """
        # --- Progress Advancement ---
        if advance > 0 and not self.has_started:
            self.has_started = True
            # For better accuracy, reset the start time to when the first step is taken.
            self.start_time = time.time() 
        
        # Only increment the progress counter if explicitly told to.
        if advance > 0:
            self.current += advance
            self.current = min(self.current, self.total)

        now = time.time()
        self.extra_info = {}
        
        if self.has_started:
            # 1. Calculate and format elapsed time.
            elapsed_seconds = now - self.start_time
            minutes = int(elapsed_seconds // 60)
            seconds = int(elapsed_seconds % 60)
            self.extra_info['elapsed'] = f"{minutes:02d}:{seconds:02d}"
            
        # --- Rate and Information Update Logic ---
        
        # Priority 1: Use external `rate_data` if available. This is the most accurate
        # source and is processed regardless of the `advance` value, allowing for
        # text-only updates.
        if rate_data:
            # Update values only if the corresponding key exists in the dictionary.
            # This prevents overwriting existing values with None if a key is missing.
            if "rate" in rate_data: 
                self.rate = rate_data["rate"]
            if "unit" in rate_data: 
                self.rate_unit = rate_data["unit"]
            # Store ETA and extra_text if they exist
            if "eta" in rate_data: 
                self.extra_info['eta'] = rate_data["eta"]
            if "extra_text" in rate_data: 
                self.extra_info['extra_text'] = rate_data["extra_text"]
                    
        # Priority 2: If no external data is provided, fall back to internal calculation.
        # This block is only executed when the process is running AND progress has actually
        # been made (`advance > 0`), as rate calculation is meaningless otherwise.
        elif status == "running" and advance > 0:
            delta_time = now - self.last_update_time
            delta_items = self.current - self.last_update_item

            # Prevent division by zero if updates are too fast or no items progressed.
            if delta_time > 0 and delta_items > 0:
                # Calculate rate based on the user's preferred unit ("it/s" or "s/it").
                if self.preferred_rate_unit == "it/s":
                    instant_rate = delta_items / delta_time
                    self.rate_unit = "it/s"
                else:  # "s/it"
                    instant_rate = delta_time / delta_items
                    self.rate_unit = "s/it"

                # Apply Exponential Moving Average (EMA) for a smoother, less jumpy rate.
                if self.rate == 0.0:  # Initialize with the first measurement.
                    self.rate = instant_rate
                else:
                    self.rate = (self.smoothing_factor * instant_rate) + \
                                ((1 - self.smoothing_factor) * self.rate)
             
            self.last_update_time = now
            self.last_update_item = self.current
        
        # Priority 3: If status is 'success' or 'error', or if `advance` is 0 without
        # `rate_data`, the logic above is skipped. This effectively "freezes" the
        # rate and extra_info fields at their last known values, which is the desired
        # behavior for terminal states or text-only updates.
        
        # Determine the description to display for this specific update.
        desc = log_content if log_content is not None else self.description
        
        # Assemble and return the final state dictionary for the frontend.
        return {
            "type": "progress",
            "current": self.current,
            "total": self.total,
            "desc": desc,
            "rate": self.rate,
            "rate_unit": self.rate_unit,
            "extra_info": self.extra_info,
            "status": status,
            "logs": logs or [],
        }