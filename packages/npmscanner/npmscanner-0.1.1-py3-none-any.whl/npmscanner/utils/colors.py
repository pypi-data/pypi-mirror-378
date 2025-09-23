class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ColorOutput:
    """Color-coded output utility"""
    
    @staticmethod
    def critical(message: str):
        print(f"{Colors.RED}{Colors.BOLD}[CRITICAL]{Colors.END} {message}")
    
    @staticmethod
    def suspicious(message: str):
        print(f"{Colors.YELLOW}{Colors.BOLD}[SUSPICIOUS]{Colors.END} {message}")
    
    @staticmethod
    def check(message: str):
        print(f"{Colors.CYAN}{Colors.BOLD}[CHECK]{Colors.END} {message}")
    
    @staticmethod
    def clean(message: str):
        print(f"{Colors.GREEN}{Colors.BOLD}[CLEAN]{Colors.END} {message}")
    
    @staticmethod
    def info(message: str):
        print(f"{Colors.WHITE}[INFO]{Colors.END} {message}")
