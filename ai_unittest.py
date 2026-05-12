import unittest
from benchmark import ai_benchmark
from generated_code.gpt_5_4.test import factorial

class TestAICodeGeneration(unittest.TestCase):
    def test_factorial_code_generation(self):
        self.assertEqual(factorial(5), 120)

if __name__ == "__main__":
    unittest.main()
