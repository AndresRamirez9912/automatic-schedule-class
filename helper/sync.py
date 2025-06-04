import os
import time
import errno

LOCK_PATH = "/app/shared/selenium.lock"

def acquire_lock(timeout=120):
    """Atomically create lock file or wait until it is released."""
    start = time.time()
    while True:
        try:
            # os.O_CREAT: create if not exists
            # os.O_EXCL: fail if already exists
            # os.O_WRONLY: write
            fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                f.write("LOCKED")
            print("[LOCK ACQUIRED] Proceeding with Selenium session.")
            return
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise  # otro error inesperado

            print("[WAITING] Selenium in use, waiting for lock...")
            if time.time() - start > timeout:
                raise TimeoutError("Timeout waiting for Selenium lock.")
            time.sleep(5)  # menos tiempo para reintentar más ágil

def release_lock():
    """Remove the lock file when done."""
    if os.path.exists(LOCK_PATH):
        os.remove(LOCK_PATH)
        print("[LOCK RELEASED] Selenium is now free.")
