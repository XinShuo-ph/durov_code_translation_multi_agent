#!/usr/bin/env python3
"""
Validate state files against JSON schemas.

Used as a pre-commit hook or manual validation tool.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# JSON Schema definitions
WORKER_STATE_SCHEMA = {
    "type": "object",
    "required": ["worker_id", "branch", "heartbeat", "status"],
    "properties": {
        "worker_id": {
            "type": "string",
            "pattern": "^[a-z0-9]{4}$",
            "description": "4-character worker ID"
        },
        "branch": {
            "type": "string",
            "description": "Git branch name"
        },
        "heartbeat": {
            "type": "integer",
            "description": "Unix timestamp"
        },
        "status": {
            "enum": ["online", "translating", "offline", "claiming"],
            "description": "Worker status"
        },
        "claimed_page": {
            "type": ["integer", "null"],
            "minimum": 1,
            "description": "Currently claimed page number"
        },
        "claim_time": {
            "type": "integer",
            "description": "Unix timestamp of claim"
        },
        "completed_pages": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["page", "completed_at"],
                "properties": {
                    "page": {"type": "integer", "minimum": 1},
                    "completed_at": {"type": "integer"},
                    "hash": {"type": "string"}
                }
            }
        },
        "stats": {
            "type": "object",
            "properties": {
                "pages_completed": {"type": "integer"},
                "pages_claimed": {"type": "integer"}
            }
        }
    }
}

GLOBAL_STATE_SCHEMA = {
    "type": "object",
    "required": ["project", "total_pages", "completed_pages", "claimed_pages", "available_pages"],
    "properties": {
        "project": {
            "type": "string",
            "description": "Project name"
        },
        "total_pages": {
            "type": "integer",
            "minimum": 1,
            "description": "Total number of pages"
        },
        "last_updated": {
            "type": "integer",
            "description": "Unix timestamp of last update"
        },
        "completed_pages": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "List of completed page numbers"
        },
        "claimed_pages": {
            "type": "object",
            "description": "Map of page number to claim info"
        },
        "available_pages": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "List of available page numbers"
        },
        "workers": {
            "type": "object",
            "description": "Map of worker_id to worker state"
        },
        "stats": {
            "type": "object",
            "properties": {
                "total_completions": {"type": "integer"},
                "total_claims": {"type": "integer"},
                "conflicts_detected": {"type": "integer"},
                "pages_reclaimed": {"type": "integer"}
            }
        }
    }
}


def validate_type(value: Any, expected_type: str) -> List[str]:
    """Validate value type"""
    errors = []
    
    if expected_type == "string" and not isinstance(value, str):
        errors.append(f"Expected string, got {type(value).__name__}")
    elif expected_type == "integer" and not isinstance(value, int):
        errors.append(f"Expected integer, got {type(value).__name__}")
    elif expected_type == "array" and not isinstance(value, list):
        errors.append(f"Expected array, got {type(value).__name__}")
    elif expected_type == "object" and not isinstance(value, dict):
        errors.append(f"Expected object, got {type(value).__name__}")
    
    return errors


def validate_enum(value: Any, allowed_values: List) -> List[str]:
    """Validate enum value"""
    if value not in allowed_values:
        return [f"Value '{value}' not in allowed values: {allowed_values}"]
    return []


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any], path: str = "") -> List[str]:
    """Recursively validate data against schema"""
    errors = []
    
    # Check required fields
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"{path}.{field}: Required field missing")
    
    # Check properties
    properties = schema.get("properties", {})
    for field, value in data.items():
        if field not in properties:
            # Unknown field - warning but not error
            continue
        
        field_schema = properties[field]
        field_path = f"{path}.{field}" if path else field
        
        # Check type
        field_type = field_schema.get("type")
        if isinstance(field_type, list):
            # Union type (e.g., ["integer", "null"])
            valid = False
            for t in field_type:
                if t == "null" and value is None:
                    valid = True
                    break
                elif t == "string" and isinstance(value, str):
                    valid = True
                    break
                elif t == "integer" and isinstance(value, int):
                    valid = True
                    break
            if not valid:
                errors.append(f"{field_path}: Expected one of {field_type}, got {type(value).__name__}")
        elif field_type:
            type_errors = validate_type(value, field_type)
            errors.extend([f"{field_path}: {e}" for e in type_errors])
        
        # Check enum
        if "enum" in field_schema:
            enum_errors = validate_enum(value, field_schema["enum"])
            errors.extend([f"{field_path}: {e}" for e in enum_errors])
        
        # Check minimum
        if "minimum" in field_schema and isinstance(value, int):
            if value < field_schema["minimum"]:
                errors.append(f"{field_path}: Value {value} below minimum {field_schema['minimum']}")
        
        # Check array items
        if field_type == "array" and "items" in field_schema and isinstance(value, list):
            for i, item in enumerate(value):
                # Only validate schema for object items, not primitives
                if field_schema["items"].get("type") == "object":
                    item_errors = validate_schema(item, field_schema["items"], f"{field_path}[{i}]")
                    errors.extend(item_errors)
                elif field_schema["items"].get("type") == "integer" and not isinstance(item, int):
                    errors.append(f"{field_path}[{i}]: Expected integer, got {type(item).__name__}")
                elif field_schema["items"].get("type") == "string" and not isinstance(item, str):
                    errors.append(f"{field_path}[{i}]: Expected string, got {type(item).__name__}")
    
    return errors


def validate_worker_state(filepath: Path) -> List[str]:
    """Validate a worker state file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"Error reading file: {e}"]
    
    return validate_schema(data, WORKER_STATE_SCHEMA)


def validate_global_state(filepath: Path) -> List[str]:
    """Validate the global STATE.json file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    except Exception as e:
        return [f"Error reading file: {e}"]
    
    errors = validate_schema(data, GLOBAL_STATE_SCHEMA)
    
    # Additional validation: check set consistency
    completed = set(data.get('completed_pages', []))
    claimed = set(data.get('claimed_pages', {}).keys())
    available = set(data.get('available_pages', []))
    
    # Check for overlaps
    if completed & claimed:
        errors.append(f"Pages in both completed and claimed: {completed & claimed}")
    if completed & available:
        errors.append(f"Pages in both completed and available: {completed & available}")
    if claimed & available:
        errors.append(f"Pages in both claimed and available: {claimed & available}")
    
    # Check coverage
    total_pages = data.get('total_pages', 0)
    all_pages = completed | set(claimed) | available
    expected_pages = set(range(1, total_pages + 1))
    
    missing = expected_pages - all_pages
    if missing:
        errors.append(f"Pages missing from all sets: {sorted(missing)}")
    
    extra = all_pages - expected_pages
    if extra:
        errors.append(f"Pages beyond total_pages range: {sorted(extra)}")
    
    return errors


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate state files")
    parser.add_argument("--worker-state", help="Path to worker state JSON file")
    parser.add_argument("--global-state", help="Path to global STATE.json file")
    parser.add_argument("--all", action="store_true", help="Validate all state files")
    
    args = parser.parse_args()
    
    all_valid = True
    
    if args.worker_state:
        filepath = Path(args.worker_state)
        print(f"Validating {filepath}...")
        errors = validate_worker_state(filepath)
        
        if errors:
            print("❌ INVALID:")
            for error in errors:
                print(f"  - {error}")
            all_valid = False
        else:
            print("✓ Valid")
    
    if args.global_state:
        filepath = Path(args.global_state)
        print(f"Validating {filepath}...")
        errors = validate_global_state(filepath)
        
        if errors:
            print("❌ INVALID:")
            for error in errors:
                print(f"  - {error}")
            all_valid = False
        else:
            print("✓ Valid")
    
    if args.all:
        # Validate STATE.json
        if Path("STATE.json").exists():
            print("Validating STATE.json...")
            errors = validate_global_state(Path("STATE.json"))
            if errors:
                print("❌ INVALID:")
                for error in errors:
                    print(f"  - {error}")
                all_valid = False
            else:
                print("✓ Valid")
        
        # Validate all worker states
        worker_states_dir = Path("worker-states")
        if worker_states_dir.exists():
            for filepath in worker_states_dir.glob("worker-*.json"):
                print(f"Validating {filepath}...")
                errors = validate_worker_state(filepath)
                if errors:
                    print("❌ INVALID:")
                    for error in errors:
                        print(f"  - {error}")
                    all_valid = False
                else:
                    print("✓ Valid")
    
    if not (args.worker_state or args.global_state or args.all):
        parser.print_help()
        sys.exit(1)
    
    if not all_valid:
        sys.exit(1)
    else:
        print("\n✓ All validations passed")

if __name__ == "__main__":
    main()
