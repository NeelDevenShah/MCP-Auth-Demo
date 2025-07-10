from fastmcp.server.auth.providers.bearer import RSAKeyPair
import os

def generate_and_save_keys():
    print("Generating new RSA key pair...")
    key_pair = RSAKeyPair.generate()

    # Create mcp_auth directory if it doesn't exist
    os.makedirs("mcp_auth", exist_ok=True)

    with open("mcp_auth/private.pem", "w") as f:
        f.write(key_pair.private_key.get_secret_value())
    print("Saved private key to mcp_auth/private.pem")

    with open("mcp_auth/public.pem", "w") as f:
        f.write(key_pair.public_key)
    print("Saved public key to mcp_auth/public.pem")

if __name__ == "__main__":
    generate_and_save_keys() 