from datetime import datetime


class Logger(object):
    def __init__(self):
        time_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.log_file = open(f"logfile-{time_str}.log", "w+", encoding="utf-8")

    def log(self, message):
        print(message)
        self.log_file.write(message + '\n')

    def close(self):
        self.log_file.close()
