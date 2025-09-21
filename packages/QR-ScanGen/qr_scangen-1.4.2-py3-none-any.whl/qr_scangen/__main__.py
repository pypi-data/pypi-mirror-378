if __package__ is None:  # if this script is executed directly not as part of a package
    import os
    import sys
    os.system(f"{sys.executable} {os.path.dirname(os.path.dirname(__file__))}")
else:
    from .main import main
    main()
