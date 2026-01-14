import sys
print("Sys Path:", sys.path)
try:
    import numpy
    print("Numpy Version:", numpy.__version__)
    print("Numpy File:", numpy.__file__)
except ImportError as e:
    print("ImportError:", e)
except Exception as e:
    print("Error:", e)
