import psutil
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)

class IBKRServerManager:

    def __init__(self, target_port, target_cmd_substring, gw_path=None):
        self.target_port = target_port
        self.target_cmd_substring = target_cmd_substring
        self.gw_path = gw_path if gw_path else os.path.join(os.path.dirname(os.path.realpath(__file__)), "clientportal.gw")

    def _get_server_process(self):
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == self.target_port:
                pid = conn.pid
                try:
                    return psutil.Process(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    logging.warning(f"Failed to get process: {e}")
        return None

    def is_server_running(self):
        process = self._get_server_process()
        if process and self.target_cmd_substring in ' '.join(process.cmdline()):
            return True
        return False

    def terminate_server(self):
        process = self._get_server_process()
        if process:
            try:
                process.terminate()
                logging.info(f"Successfully terminated the server process.")
            except Exception as e:
                logging.error(f"Could not terminate the server process: {e}")

    def manage_server(self, restart=False):
        if restart:
            self.terminate_server()
            if self.is_server_running():
                logging.error("IBKR server is still running. Please kill the process manually.")
                exit(1)

        if self.is_server_running():
            logging.info("IBKR server is already running.")
        else:
            self.start_server()

    def start_server(self):
        try:
            subprocess.Popen(
                f"cd {self.gw_path} && bin/run.sh root/conf.yaml",
                shell=True,
                stdout=open("stdout.log", 'a'),
                stderr=open("stderr.log", 'a'),
                executable="/usr/bin/zsh"
            )
            logging.info("Server started successfully.")
        except Exception as e:
            logging.error(f"Failed to start the server: {e}")