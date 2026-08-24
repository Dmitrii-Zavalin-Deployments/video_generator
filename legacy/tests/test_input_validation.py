import json
import unittest
from jsonschema import validate

class TestInputValidation(unittest.TestCase):
    def setUp(self):
        """Load input JSON"""
        with open("data/testing-input-output/fluid_simulation.json") as f:
            self.input_data = json.load(f)

    def test_json_schema(self):
        """Ensure input file follows JSON schema"""
        schema = {
            "type": "object",
            "properties": {
                "simulation_info": {"type": "object"},
                "global_parameters": {"type": "object"},
                "data_points": {"type": "array"}
            },
            "required": ["simulation_info", "global_parameters", "data_points"]
        }
        validate(instance=self.input_data, schema=schema)

    def test_numerical_validity(self):
        """Ensure fluid simulation parameters are physically correct"""
        assert 101000 <= self.input_data["global_parameters"]["pressure"]["value"] <= 102000, "Pressure out of bounds!"
        assert self.input_data["simulation_info"]["frame_rate"] == 30, "Incorrect frame rate!"

if __name__ == "__main__":
    unittest.main()



