import json
from jsonschema import Draft7Validator
from config import SCHEMA_PATH

class SchemaValidator:
    def __init__(self, schema_path=SCHEMA_PATH):
        """Load and pre-compile the JSON schema validator."""
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        # Pre-compile Draft7Validator for maximum efficiency
        self.validator = Draft7Validator(self.schema)

    def validate(self, candidate: dict) -> bool:
        """
        Validate a single candidate record.
        Returns True if valid, False otherwise.
        """
        return self.validator.is_valid(candidate)

    def get_validation_errors(self, candidate: dict) -> list:
        """Return a list of validation errors if the candidate violates the schema."""
        return [error.message for error in self.validator.iter_errors(candidate)]
