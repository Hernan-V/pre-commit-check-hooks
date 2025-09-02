#!/usr/bin/env python3
"""Tests for custom required field names validation functionality."""

import os
import pytest
from hooks.validate_schema import validate_schema, validate_custom_field_names


class TestValidateCustomFieldNames:
    """Test the validate_custom_field_names function."""
    
    def test_no_required_fields(self):
        """Test that validation passes when no required fields are specified."""
        schema_fields = [{"name": "test", "type": "STRING", "mode": "NULLABLE"}]
        errors = validate_custom_field_names(schema_fields, None, 'any', 'test_path')
        assert errors == []
        
        errors = validate_custom_field_names(schema_fields, '', 'any', 'test_path')
        assert errors == []
    
    def test_valid_any_position(self):
        """Test validation passes with required field names in any valid order."""
        schema_fields = [
            {"name": "data_field", "type": "STRING", "mode": "REQUIRED"},
            {"name": "insert_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "other_field", "type": "STRING", "mode": "NULLABLE"},
            {"name": "update_date", "type": "TIMESTAMP", "mode": "NULLABLE"}
        ]
        errors = validate_custom_field_names(schema_fields, 'insert_date,update_date', 'any', 'test_path')
        assert errors == []
    
    def test_valid_beginning_position(self):
        """Test validation passes with required field names at beginning."""
        schema_fields = [
            {"name": "insert_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "update_date", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "data_field", "type": "STRING", "mode": "REQUIRED"}
        ]
        errors = validate_custom_field_names(schema_fields, 'insert_date,update_date', 'beginning', 'test_path')
        assert errors == []
    
    def test_valid_end_position(self):
        """Test validation passes with required field names at end."""
        schema_fields = [
            {"name": "data_field", "type": "STRING", "mode": "REQUIRED"},
            {"name": "insert_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "update_date", "type": "TIMESTAMP", "mode": "NULLABLE"}
        ]
        errors = validate_custom_field_names(schema_fields, 'insert_date,update_date', 'end', 'test_path')
        assert errors == []
    
    def test_missing_required_field(self):
        """Test validation fails when required field name is missing."""
        schema_fields = [
            {"name": "data_field", "type": "STRING", "mode": "REQUIRED"},
            {"name": "other_field", "type": "STRING", "mode": "NULLABLE"}
        ]
        errors = validate_custom_field_names(schema_fields, 'insert_date,update_date', 'any', 'test_path')
        assert len(errors) == 1
        assert "Missing required field names: insert_date, update_date" in errors[0]
    
    def test_wrong_order(self):
        """Test validation fails when required field names are in wrong order."""
        schema_fields = [
            {"name": "update_date", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "insert_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "data_field", "type": "STRING", "mode": "REQUIRED"}
        ]
        errors = validate_custom_field_names(schema_fields, 'insert_date,update_date', 'any', 'test_path')
        assert len(errors) == 1
        assert "Required field names out of order" in errors[0]
        assert "[insert_date, update_date]" in errors[0]
    
    def test_wrong_beginning_position(self):
        """Test validation fails when required field names not at beginning."""
        schema_fields = [
            {"name": "data_field", "type": "STRING", "mode": "REQUIRED"},
            {"name": "insert_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "update_date", "type": "TIMESTAMP", "mode": "NULLABLE"}
        ]
        errors = validate_custom_field_names(schema_fields, 'insert_date,update_date', 'beginning', 'test_path')
        assert len(errors) == 1
        assert "Required field names must be at beginning" in errors[0]
    
    def test_wrong_end_position(self):
        """Test validation fails when required field names not at end."""
        schema_fields = [
            {"name": "insert_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "update_date", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "data_field", "type": "STRING", "mode": "REQUIRED"}
        ]
        errors = validate_custom_field_names(schema_fields, 'insert_date,update_date', 'end', 'test_path')
        assert len(errors) == 1
        assert "Required field names must be at end" in errors[0]
    
    def test_comma_separated_parsing(self):
        """Test that comma-separated field name parsing works correctly."""
        schema_fields = [
            {"name": "insert_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "update_date", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "data_field", "type": "STRING", "mode": "REQUIRED"}
        ]
        # Test with spaces around commas
        errors = validate_custom_field_names(schema_fields, ' insert_date , update_date ', 'any', 'test_path')
        assert errors == []


class TestRequiredFieldsIntegration:
    """Integration tests using actual test fixtures."""
    
    def get_fixture_path(self, filename):
        """Get path to test fixture file."""
        return os.path.join(
            os.path.dirname(__file__),
            'required_fields', 'bq', filename
        )
    
    def test_valid_end_position_file(self):
        """Test validation passes for valid end position fixture."""
        file_path = self.get_fixture_path('valid_end_position.json')
        errors, _, _ = validate_schema(
            file_path, 'bigquery', 'snake', 'lint',
            'insert_date,update_date', 'end'
        )
        assert errors == []
    
    def test_valid_begin_position_file(self):
        """Test validation passes for valid beginning position fixture."""
        file_path = self.get_fixture_path('valid_begin_position.json')
        errors, _, _ = validate_schema(
            file_path, 'bigquery', 'snake', 'lint',
            'insert_date,update_date', 'beginning'
        )
        assert errors == []
    
    def test_valid_any_position_file(self):
        """Test validation passes for valid any position fixture."""
        file_path = self.get_fixture_path('valid_any_position.json')
        errors, _, _ = validate_schema(
            file_path, 'bigquery', 'snake', 'lint',
            'insert_date,update_date', 'any'
        )
        assert errors == []
    
    def test_missing_field_file(self):
        """Test validation fails for missing field fixture."""
        file_path = self.get_fixture_path('missing_field.json')
        errors, _, _ = validate_schema(
            file_path, 'bigquery', 'snake', 'lint',
            'insert_date,update_date', 'any'
        )
        assert len(errors) > 0
        assert any("Missing required field names: insert_date, update_date" in error for error in errors)
    
    def test_wrong_order_file(self):
        """Test validation fails for wrong order fixture."""
        file_path = self.get_fixture_path('wrong_order.json')
        errors, _, _ = validate_schema(
            file_path, 'bigquery', 'snake', 'lint',
            'insert_date,update_date', 'any'
        )
        assert len(errors) > 0
        assert any("Required field names out of order" in error for error in errors)
    
    def test_wrong_position_end_file(self):
        """Test validation fails when end position required but fields at beginning."""
        file_path = self.get_fixture_path('wrong_position_end.json')
        errors, _, _ = validate_schema(
            file_path, 'bigquery', 'snake', 'lint',
            'insert_date,update_date', 'end'
        )
        assert len(errors) > 0
        assert any("Required field names must be at end" in error for error in errors)
    
    def test_wrong_position_begin_file(self):
        """Test validation fails when beginning position required but fields not at beginning."""
        file_path = self.get_fixture_path('wrong_position_begin.json')
        errors, _, _ = validate_schema(
            file_path, 'bigquery', 'snake', 'lint',
            'insert_date,update_date', 'beginning'
        )
        assert len(errors) > 0
        assert any("Required field names must be at beginning" in error for error in errors)
    
    def test_backward_compatibility(self):
        """Test that existing functionality works when no required fields specified."""
        file_path = self.get_fixture_path('valid_any_position.json')
        errors, _, _ = validate_schema(
            file_path, 'bigquery', 'snake', 'lint',
            None, 'any'
        )
        # Should pass basic validation without custom field requirements
        assert errors == []


if __name__ == '__main__':
    pytest.main([__file__])