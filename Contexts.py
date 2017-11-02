import arcpy
from arcpy import env
from contextlib import contextmanager

## These functions are adapted from:
## https://gis.stackexchange.com/a/158754
## https://gist.github.com/nickrsan/74461397d9af015db3879c7d2e5f3227#gistcomment-2111123

@contextmanager
def Extension(name):
    if arcpy.CheckExtension(name) == "Available":
        status = arcpy.CheckOutExtension(name)
        yield status
    else:
        raise RuntimeError("%s license isn't available" % name)

    arcpy.CheckInExtension(name)

@contextmanager
def Environment(variable, value):
    originalValue = env.__getitem__(variable)
    env.__setitem__(variable, value)
    yield value
    env.__setitem__(variable, originalValue)


if __name__ == "__main__":
    ## Need to make an example of using this
    pass
