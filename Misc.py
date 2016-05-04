import string
import random

# Adapted from http://stackoverflow.com/a/2257449/6214388
def randomString(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

if __name__ == "__main__":
    print randomString()
