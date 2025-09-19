from .core import (
    # Basic DTP functions
    encrypt_dtp, 
    decrypt_dtp, 
    generate_decoy, 
    load_decoy_data,
    decrypt_decoy,
    extract_secret,
    
    # Enhanced functions with client secret
    encrypt_dtp_with_client_secret,
    decrypt_dtp_with_client_secret,
    
    # Decoy detection and security utilities
    is_decoy_password,
    hash_password,
    generate_client_secret,
    
    # Custom exceptions
    DTPError,
    DTPDecryptionError
)
