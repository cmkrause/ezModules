from progressbar import ProgressBar, Bar, ETA, Timer, Percentage


# Adapted from examples found here:
# http://progressbar-2.readthedocs.org/en/latest/usage.html#bar-with-custom-widgets
class ezProgressBar:

    def __init__(self, iterations):
        widgets = [Percentage(), " | ", Timer(), " | ", ETA(), " | ", Bar()]
        self.pbar = ProgressBar(widgets=widgets, max_value=iterations)
        self.pbar.start()
        self.iterationCount = 0
        self.maxIterations = iterations
        
    def update(self):
        self.iterationCount += 1
        if self.iterationCount <= self.maxIterations:
            self.pbar.update(self.iterationCount)
        
    def finish(self):
        self.pbar.finish()


if __name__ == "__main__":

    from time import sleep
        
    ezPBar = ezProgressBar(12)
    for i in xrange(12):
        sleep(1)
        ezPBar.update()
    ezPBar.finish()
