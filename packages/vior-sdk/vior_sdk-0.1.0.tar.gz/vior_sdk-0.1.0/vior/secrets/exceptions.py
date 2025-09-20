import sys

class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

class ViorSecretsError(Exception):
    pass

class AuthenticationError(ViorSecretsError):
    def __init__(self, message="Authentication failed"):
        super().__init__(message)
        if "Configuration not found" in message:
            print(f"\n{Colors.RED}Error:{Colors.RESET} No configuration found on your system.")
            print()
            print(f"{Colors.YELLOW}Hint:{Colors.RESET} Configure your credentials using: {Colors.BLUE}vior configure{Colors.RESET}")
            print()
            print(f"{Colors.CYAN}Note:{Colors.RESET} Please get your credentials from {Colors.BLUE}https://secrets.viorcloud.com{Colors.RESET}")
            print(f"      or refer to the documentation at {Colors.BLUE}https://secrets.viorcloud.com/docs{Colors.RESET}")
            print()
            print("For more information, please refer to the documentation.")
            print()
            sys.exit(1)

class ConfigurationError(ViorSecretsError):
    def __init__(self, message="Configuration error"):
        super().__init__(message)
        if "Vior CLI not found" in message:
            print(f"\n{Colors.RED}Error:{Colors.RESET} vior-cli not found on your system.")
            print()
            print(f"{Colors.YELLOW}Hint:{Colors.RESET} Install it using: {Colors.BLUE}pip install vior-cli{Colors.RESET}")
            print()
            print(f"{Colors.CYAN}Note (macOS):{Colors.RESET} Ensure pipx is installed and in PATH. If not, run:")
            print(f"  {Colors.BLUE}brew install pipx{Colors.RESET}")
            print(f"  {Colors.BLUE}pipx ensurepath{Colors.RESET}")
            print(f"  {Colors.BLUE}pipx install vior-cli{Colors.RESET}")
            print()
            print(f"For more information, please refer to the documentation: {Colors.BLUE}https://secrets.viorcloud.com/docs{Colors.RESET}")
            print()
            sys.exit(1)

class SecretNotFoundError(ViorSecretsError):
    def __init__(self, secret_name):
        super().__init__(f"Secret '{secret_name}' not found")
        print(f"\n{Colors.RED}Error:{Colors.RESET} Secret '{secret_name}' not found.")
        print()
        print(f"{Colors.YELLOW}Hint:{Colors.RESET} Check if the secret name is correct or create it at {Colors.BLUE}https://secrets.viorcloud.com{Colors.RESET}")
        print()
        sys.exit(1)