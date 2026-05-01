import keyring
import getpass
import sys

SERVICE_NAME = "AutoPoster-Agent"

def main():
    print("========================================")
    print("AutoPoster-Agent Secure Keychain Setup")
    print("========================================")
    print("\nThis script will securely store your API Key into your System Keychain (macOS, Windows, or Linux).")
    print("It will NOT be saved in any plain text file or .env file.\n")
    
    api_key = getpass.getpass("Please enter your OpenAI API Key: ").strip()
    
    if not api_key:
        print("Error: API Key cannot be empty.")
        sys.exit(1)
        
    try:
        keyring.set_password(SERVICE_NAME, "OPENAI_API_KEY", api_key)
        print("\n✅ Success! Your API key has been securely stored in the System Keychain.")
        print(f"Service Name: {SERVICE_NAME}")
        print("Account: OPENAI_API_KEY")
        print("\nTest Retrieval: ", "Success" if keyring.get_password(SERVICE_NAME, "OPENAI_API_KEY") else "Failed")
    except Exception as e:
        print(f"\n❌ Error storing the API key in the keychain: {e}")
        print("Please ensure your system has a supported keychain backend installed.")

if __name__ == "__main__":
    main()
