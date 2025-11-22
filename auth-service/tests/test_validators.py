import pytest
from app.utils.validators import (
    validate_username, validate_email, validate_password_strength,
    validate_name, sanitize_input, validate_registration_data
)

class TestValidators:
    
    def test_validate_username_valid(self):
        result = validate_username('testuser')
        assert result['valid'] is True
    
    def test_validate_username_too_short(self):
        result = validate_username('ab')
        assert result['valid'] is False
        assert 'at least 3' in result['error']
    
    def test_validate_username_too_long(self):
        result = validate_username('a' * 21)
        assert result['valid'] is False
        assert 'no more than 20' in result['error']
    
    def test_validate_username_invalid_chars(self):
        result = validate_username('test@user')
        assert result['valid'] is False
    
    def test_validate_email_valid(self):
        result = validate_email('test@example.com')
        assert result['valid'] is True
    
    def test_validate_email_invalid(self):
        result = validate_email('invalid-email')
        assert result['valid'] is False
        assert 'Invalid email' in result['error']
    
    def test_validate_email_empty(self):
        result = validate_email('')
        assert result['valid'] is False
        assert 'required' in result['error']
    
    def test_validate_password_valid(self):
        result = validate_password_strength('Password123')
        assert result['valid'] is True
        assert result['strength'] == 'medium'
    
    def test_validate_password_strong(self):
        result = validate_password_strength('Password123!')
        assert result['valid'] is True
        assert result['strength'] == 'strong'
    
    def test_validate_password_no_uppercase(self):
        result = validate_password_strength('password123')
        assert result['valid'] is False
        assert 'uppercase' in result['error']
    
    def test_validate_password_no_lowercase(self):
        result = validate_password_strength('PASSWORD123')
        assert result['valid'] is False
        assert 'lowercase' in result['error']
    
    def test_validate_password_no_digit(self):
        result = validate_password_strength('Password')
        assert result['valid'] is False
        assert 'number' in result['error']
    
    def test_validate_password_too_short(self):
        result = validate_password_strength('Pass1')
        assert result['valid'] is False
        assert 'at least' in result['error']
    
    def test_validate_name_valid(self):
        result = validate_name('John Doe')
        assert result['valid'] is True
    
    def test_validate_name_empty(self):
        result = validate_name('')
        assert result['valid'] is True  # Names are optional
    
    def test_validate_name_invalid_chars(self):
        result = validate_name('John123')
        assert result['valid'] is False
    
    def test_sanitize_input_html(self):
        result = sanitize_input('<script>alert("xss")</script>test')
        assert '<script>' not in result
        assert 'test' in result
    
    def test_sanitize_input_null_bytes(self):
        result = sanitize_input('test\x00data')
        assert '\x00' not in result
        assert 'testdata' == result
    
    def test_validate_registration_data_valid(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'firstName': 'John',
            'lastName': 'Doe'
        }
        result = validate_registration_data(data)
        assert result['valid'] is True
        assert result['sanitized_data']['username'] == 'testuser'
    
    def test_validate_registration_data_invalid(self):
        data = {
            'username': 'ab',  # Too short
            'email': 'invalid',  # Invalid email
            'password': 'weak'  # Weak password
        }
        result = validate_registration_data(data)
        assert result['valid'] is False
        assert 'username' in result['errors']
        assert 'email' in result['errors']
        assert 'password' in result['errors']
    
    def test_validate_registration_data_not_dict(self):
        result = validate_registration_data("not a dict")
        assert result['valid'] is False
        assert 'Invalid data format' in result['errors']['general']