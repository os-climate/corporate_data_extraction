from pathlib import Path

class TrainingMonitor:
    """Class for a simple monitoring of a training process
    """
    def __init__(self: 'TrainingMonitor', path_file_running=None) -> 'TrainingMonitor':
        self.path_file_running: Path = path_file_running if path_file_running is not None else self._set_default_path()
    
    @staticmethod
    def _set_default_path() -> Path:
        """Returns a default Path if no path is given

        :return: Default path
        :rtype: Path
        """
        return Path(__file__).parent.resolve() / 'trainingMonitorFile'
    
    def _delete_path_file_running(self) -> None:
        self.path_file_running.unlink(missing_ok=True)
    
    def set_running(self) -> None:
        """Creates a file at the path path_file_running for monitoring the status of the current training
        """
        self.path_file_running.touch()
        
    def clear_running(self) -> None:
        """Deletes the file at the path path_file_running
        """
        self.path_file_running.unlink()
      
    def check_running(self) -> bool:
        """Check if the file at path_file_running exists

        :return: Value if file exists or not
        :rtype: bool
        """
        return self.path_file_running.exists()