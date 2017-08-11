from progressbar import ProgressBar, Bar, AdaptiveETA, Timer, Percentage, FormatCustomText


## Adapted from examples found here:
## http://progressbar-2.readthedocs.org/en/latest/usage.html#bar-with-custom-widgets
## http://stackoverflow.com/a/8460856
## http://pythonhosted.org/progressbar2/examples.html
class ezProgressBar:

    def __init__(self, iterations):
        self.textFormatter = FormatCustomText("%(msg)s",{"msg":""})
        self.widgets = [self.textFormatter, Percentage(), " | ", Timer(), " | ", AdaptiveETA(), Bar()]
        self.pbar = ProgressBar(widgets = self.widgets, max_value = iterations)
        self.pbar.start()
        self.iterationCount = 0
        self.maxIterations = iterations
        
    def update(self, step = 1, label = ""):
        if label <> "":
            self.textFormatter.update_mapping(msg = "%s | " % label.strip())
        self.iterationCount += step
        if self.iterationCount <= self.maxIterations:
            self.pbar.update(self.iterationCount)
        
    def finish(self):
        self.pbar.finish()


if __name__ == "__main__":

    from time import sleep
        
    ezPBar = ezProgressBar(12)
    for i in xrange(12):
        
        sleep(1)
        ezPBar.update(label = "%s iteration" % i)

        
    ezPBar.finish()
