import sys
from argparse import ArgumentParser
from types import ModuleType


class FigoModule(ModuleType):
    __doc__ = "Get the OBJECT keyword from a fits file"
    def __call__(self, filename: str) -> str:
        """
        Args:
            filename (str): Name of the fits file

        Returns:
            str: Value of the OBJECT keyword in the fits file
        """
        f = open(filename, 'rb', buffering=1024)
        key_value = f.read(80)
        while not key_value.startswith(b'OBJECT'):
            key_value = f.read(80)
        f.close()
        # find the start of the comment, or -1 if no comment
        comment = key_value.rfind(b'/')
        # search for the second quote, the first quote is at index 11 for sure
        second = key_value.rindex(b"'", 11, comment)
        return key_value[11 : second].replace(b"''", b"'").decode()

    def _main(self):
        parser = ArgumentParser(prog='figo', add_help=False)
        parser.add_argument('filename')
        args = parser.parse_args()
        print(self(args.filename))
    
    def afap(self, filename: str) -> str:
        import cfigo
        return cfigo.get(filename)


sys.modules[__name__] = FigoModule(__name__)