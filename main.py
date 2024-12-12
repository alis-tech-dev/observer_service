import logging
import os
import time
from textwrap import dedent
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


def setup_logging() -> None:
    """
    Configures the logging system. Logs are saved to both console
    and a log file. Creates the necessary directories if they do not exist.
    """
    os.makedirs('/home/admin/web/pythonScripts/observer', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                '/home/admin/web/pythonScripts/observer/loger.log'
            )
        ]
    )


class MyHandler(FileSystemEventHandler):
    """
    Custom event handler for monitoring file system changes.
    """

    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Handles the event when a file is deleted. If the deleted file matches
        a specific name, it attempts to recreate it with predefined content.

        Args:
            event (FileSystemEvent): The event object containing information
            about the deleted file.
        """
        if event.src_path.endswith("modules.php"):
            directory: str = os.path.dirname(event.src_path)
            timeout: int = 10
            start_time: float = time.time()

            while not os.path.exists(directory):
                if time.time() - start_time > timeout:
                    logging.error(
                        f"Directory {directory} did not appear within timeout."
                    )
                    return
                time.sleep(0.1)
            self.add_content_to_file(event.src_path)

    @staticmethod
    def add_content_to_file(path: str) -> None:
        """
        Writes predefined PHP content to a specified file.

        Args:
            path (str): The path of the file to write the content to.
        """
        content: str = dedent("""\
        <?php
        return [
          'Advanced' => [
            'order' => 15
          ],
          'ChatPlugin' => [],
          'Crm' => [
            'order' => 10
          ],
          'Erp' => [],
          'Google' => [
            'order' => 21
          ],
          'PM' => [],
          'PushNotifications' => [],
          'Sales' => []
        ];
        """)
        with open(path, 'w') as f:
            f.write(content)


if __name__ == "__main__":
    setup_logging()

    path_to_watch: str = (
        '/home/admin/web/alis-is.com/public_html/data/cache/application'
    )
    event_handler: MyHandler = MyHandler()
    observer: Observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
