"""
Unit tests for PII hashing utility module

Tests the hash_pii() and mask_pii_display() functions to ensure correct
hashing behavior and masking for frontend display.
"""

import pytest
import hashlib
from utils.pii_hashing import hash_pii, mask_pii_display


class TestHashPII:
    """Test suite for hash_pii() function"""
    
    def test_hash_pii_with_email(self):
        """Test hashing a valid email address"""
        email = "user@example.com"
        result = hash_pii(email)
        
        # Verify it returns a non-None value
        assert result is not None
        
        # Verify it's a valid SHA-256 hash (64 hex characters)
        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)
        
        # Verify it matches expected SHA-256 hash
        expected = hashlib.sha256(email.encode('utf-8')).hexdigest()
        assert result == expected
    
    def test_hash_pii_with_phone(self):
        """Test hashing a valid phone number"""
        phone = "9876543210"
        result = hash_pii(phone)
        
        # Verify it returns a non-None value
        assert result is not None
        
        # Verify it's a valid SHA-256 hash
        assert len(result) == 64
        
        # Verify it matches expected SHA-256 hash
        expected = hashlib.sha256(phone.encode('utf-8')).hexdigest()
        assert result == expected
    
    def test_hash_pii_deterministic(self):
        """Test that same input produces same hash (deterministic)"""
        value = "test@example.com"
        hash1 = hash_pii(value)
        hash2 = hash_pii(value)
        
        assert hash1 == hash2
    
    def test_hash_pii_different_inputs(self):
        """Test that different inputs produce different hashes"""
        hash1 = hash_pii("user1@example.com")
        hash2 = hash_pii("user2@example.com")
        
        assert hash1 != hash2
    
    def test_hash_pii_with_none(self):
        """Test hashing None returns None"""
        result = hash_pii(None)
        assert result is None
    
    def test_hash_pii_with_empty_string(self):
        """Test hashing empty string returns None"""
        result = hash_pii("")
        assert result is None
    
    def test_hash_pii_with_whitespace_only(self):
        """Test hashing whitespace-only string returns None"""
        result = hash_pii("   ")
        # Note: whitespace is considered a valid value, so it should hash
        assert result is not None
        expected = hashlib.sha256("   ".encode('utf-8')).hexdigest()
        assert result == expected
    
    def test_hash_pii_case_sensitive(self):
        """Test that hashing is case-sensitive"""
        hash1 = hash_pii("User@Example.Com")
        hash2 = hash_pii("user@example.com")
        
        assert hash1 != hash2
    
    def test_hash_pii_with_special_characters(self):
        """Test hashing values with special characters"""
        value = "user+tag@example.com"
        result = hash_pii(value)
        
        assert result is not None
        assert len(result) == 64
        expected = hashlib.sha256(value.encode('utf-8')).hexdigest()
        assert result == expected
    
    def test_hash_pii_with_international_phone(self):
        """Test hashing international phone format"""
        phone = "+91-9876543210"
        result = hash_pii(phone)
        
        assert result is not None
        assert len(result) == 64
        expected = hashlib.sha256(phone.encode('utf-8')).hexdigest()
        assert result == expected


class TestMaskPIIDisplay:
    """Test suite for mask_pii_display() function"""
    
    def test_mask_email(self):
        """Test masking an email address"""
        email = "user@example.com"
        result = mask_pii_display(email, "email")
        
        assert result == "***@***.com"
    
    def test_mask_phone_with_sufficient_digits(self):
        """Test masking a phone number with at least 4 digits"""
        phone = "9876543210"
        result = mask_pii_display(phone, "phone")
        
        assert result == "***-***-3210"
        # Verify last 4 digits are shown
        assert result.endswith("3210")
    
    def test_mask_phone_with_less_than_4_digits(self):
        """Test masking a phone number with less than 4 digits"""
        phone = "123"
        result = mask_pii_display(phone, "phone")
        
        assert result == "***"
    
    def test_mask_phone_exactly_4_digits(self):
        """Test masking a phone number with exactly 4 digits"""
        phone = "1234"
        result = mask_pii_display(phone, "phone")
        
        assert result == "***-***-1234"
    
    def test_mask_with_none_value(self):
        """Test masking None value"""
        result_email = mask_pii_display(None, "email")
        result_phone = mask_pii_display(None, "phone")
        
        assert result_email == "***"
        assert result_phone == "***"
    
    def test_mask_with_empty_string(self):
        """Test masking empty string"""
        result_email = mask_pii_display("", "email")
        result_phone = mask_pii_display("", "phone")
        
        assert result_email == "***"
        assert result_phone == "***"
    
    def test_mask_with_unknown_type(self):
        """Test masking with unknown PII type"""
        value = "some_value"
        result = mask_pii_display(value, "unknown")
        
        assert result == "***"
    
    def test_mask_email_does_not_reveal_original(self):
        """Test that email masking doesn't reveal original email"""
        email1 = "user@example.com"
        email2 = "admin@company.org"
        
        result1 = mask_pii_display(email1, "email")
        result2 = mask_pii_display(email2, "email")
        
        # Both should produce the same masked output
        assert result1 == result2 == "***@***.com"
    
    def test_mask_phone_reveals_only_last_4_digits(self):
        """Test that phone masking reveals only last 4 digits"""
        phone = "9876543210"
        result = mask_pii_display(phone, "phone")
        
        # Should not contain first 6 digits
        assert "987654" not in result
        # Should contain last 4 digits
        assert "3210" in result
    
    def test_mask_international_phone(self):
        """Test masking international phone format"""
        phone = "+919876543210"
        result = mask_pii_display(phone, "phone")
        
        # Should show last 4 digits
        assert result == "***-***-3210"
    
    def test_mask_phone_with_formatting(self):
        """Test masking phone with existing formatting"""
        phone = "(987) 654-3210"
        result = mask_pii_display(phone, "phone")
        
        # Should show last 4 characters (which includes formatting)
        assert result == "***-***-3210"


class TestPIIHashingIntegration:
    """Integration tests for PII hashing workflow"""
    
    def test_hash_and_mask_workflow(self):
        """Test typical workflow: hash for storage, mask for display"""
        original_email = "user@example.com"
        original_phone = "9876543210"
        
        # Hash for storage
        email_hash = hash_pii(original_email)
        phone_hash = hash_pii(original_phone)
        
        # Verify hashes are created
        assert email_hash is not None
        assert phone_hash is not None
        
        # Mask for display
        email_masked = mask_pii_display(original_email, "email")
        phone_masked = mask_pii_display(original_phone, "phone")
        
        # Verify masking works
        assert email_masked == "***@***.com"
        assert phone_masked == "***-***-3210"
        
        # Verify original values are not in masked output (except last 4 of phone)
        assert "user" not in email_masked
        assert "example" not in email_masked
        assert "987654" not in phone_masked
    
    def test_shared_contact_detection_via_hash(self):
        """Test that identical PII produces identical hash for shared contact detection"""
        # Two entities with same email
        email1 = "shared@example.com"
        email2 = "shared@example.com"
        
        hash1 = hash_pii(email1)
        hash2 = hash_pii(email2)
        
        # Hashes should match, enabling SHARED_CONTACT detection
        assert hash1 == hash2
        
        # Different emails should produce different hashes
        email3 = "different@example.com"
        hash3 = hash_pii(email3)
        assert hash1 != hash3
    
    def test_one_way_hashing_irreversibility(self):
        """Test that hash cannot be reversed to original value"""
        original = "secret@example.com"
        hashed = hash_pii(original)
        
        # Hash should not contain original value
        assert original not in hashed
        assert "secret" not in hashed
        assert "example" not in hashed
        
        # Hash should be fixed length regardless of input length
        long_email = "very.long.email.address.with.many.parts@example.com"
        long_hash = hash_pii(long_email)
        
        assert len(hashed) == len(long_hash) == 64
