"""
Domain-level constants for the raffle application.
"""

class PiiMode:
    """Constants for PII handling modes."""
    ORIGINAL = "original"           # Keep PII as is
    MASKED = "masked"               # Mask PII in display outputs
    PSEUDONYMIZED = "pseudonymized" # Replace PII with pseudonyms

    @classmethod
    def get_all_modes(cls) -> list:
        """Get all available PII modes.
        
        Returns:
            List of all PII modes
        """
        return [cls.ORIGINAL, cls.MASKED, cls.PSEUDONYMIZED]
        
    @classmethod
    def get_description(cls, mode: str) -> str:
        """Get a human-readable description for a PII mode.
        
        Args:
            mode: The PII mode
            
        Returns:
            Human-readable description
        """
        descriptions = {
            cls.ORIGINAL: "Original (no protection)",
            cls.MASKED: "Masked (basic protection)",
            cls.PSEUDONYMIZED: "Pseudonymized (advanced protection)"
        }
        return descriptions.get(mode, "Unknown mode")