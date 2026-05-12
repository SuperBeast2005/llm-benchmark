import unittest
from benchmark import ai_benchmark
from generated_code.gpt_5_4.test import factorial
from passatk import calculate_pass_at_k

class TestAICodeGeneration(unittest.TestCase):
    # This test assumes that the generated code for the factorial function is correct and can be imported.
    def test_factorial_code_generation(self):
        self.assertEqual(factorial(5), 120)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAICodeGeneration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n--- Zusammenfassung ---")
    print(f"Anzahl der Tests: {result.testsRun}")
    print(f"Erfolgreich: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fehlgeschlagen: {len(result.failures)}")
    print(f"Fehler (Code-Errors): {len(result.errors)}")
    print(calculate_pass_at_k(result.testsRun, result.testsRun - len(result.failures) - len(result.errors), 1))
    print(calculate_pass_at_k(10, 3, 5))

    # Details zu Fehlern ausgeben
    for check, error in result.failures:
        print(f"Defekt: {check} -> {error}")