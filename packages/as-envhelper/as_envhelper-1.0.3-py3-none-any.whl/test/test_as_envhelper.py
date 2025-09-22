import unittest
import os
from as_envhelper import load_env, get_env, env_to_dict

class TestAsEnvHelper(unittest.TestCase):

    def setUp(self):
        # Create a temporary .env file for testing
        self.env_file = ".env.test"
        with open(self.env_file, "w") as f:
            f.write("TEST_KEY=123\n")
            f.write("BOOL_KEY=True\n")
            f.write("FLOAT_KEY=3.14\n")

    def tearDown(self):
        # Remove test .env file
        if os.path.exists(self.env_file):
            os.remove(self.env_file)

    def test_load_env(self):
        load_env(self.env_file)
        self.assertEqual(get_env("TEST_KEY"), "123")
        self.assertEqual(get_env("BOOL_KEY", type=bool), True)
        self.assertEqual(get_env("FLOAT_KEY", type=float), 3.14)

    def test_env_to_dict(self):
        load_env(self.env_file)
        d = env_to_dict()
        self.assertEqual(d["TEST_KEY"], "123")
        self.assertEqual(d["BOOL_KEY"], "True")
        self.assertEqual(d["FLOAT_KEY"], "3.14")

    def test_get_env_validation(self):
        load_env(self.env_file)
        # Regex validation
        with self.assertRaises(ValueError):
            get_env("TEST_KEY", regex=r"^\d{4}$")  # TEST_KEY is "123" → fails
        # Choices validation
        with self.assertRaises(ValueError):
            get_env("TEST_KEY", choices=["111", "222"])
        # Required validation
        with self.assertRaises(KeyError):
            get_env("MISSING_KEY", required=True)

if __name__ == "__main__":
    unittest.main()
