class Logger(object):
    def __init__(self):
        self.log_file = open("logfile.log", "w+", encoding="utf-8")

    def log(self, message):
        print(message)
        self.log_file.write(message + '\n')
        
    def close(self):
        self.log_file.close()
