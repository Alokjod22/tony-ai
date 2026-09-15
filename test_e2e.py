import asyncio
import sys
import io

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from server.app import brain

prompts = [
    ("Rooting", "can you root my phone"),
    ("Bootloader", "how to unlock bootloader"),
    ("Firmware", "find firmware for my device"),
    ("Custom ROM", "custom rom directory"),
    ("General AI", "explain quantum computing in simple terms")
]

async def run_tests():
    all_passed = True
    for category, p in prompts:
        print(f"\n==================== [TESTING: {category}] ====================")
        print(f"Prompt: {p}")
        try:
            res = await brain.process_user_input(p, persona="tony")
            resp_text = res.get("response", "")
            print(f"Persona: {res.get('persona')}")
            print(f"Emotion: {res.get('emotion')}")
            print(f"Confidence: {res.get('confidence')}")
            print(f"Response Preview:\n{resp_text[:300]}...\n")
            
            if "Instruction processed by TONY cognitive matrix. Telemetry is active and nominal." in resp_text:
                print("[FAIL] Received generic fallback string!")
                all_passed = False
            elif len(resp_text) < 50:
                print("[FAIL] Response too short!")
                all_passed = False
            else:
                print("[PASS] Rich intelligent response received.")
        except Exception as e:
            print(f"[ERROR]: {e}")
            all_passed = False

    if all_passed:
        print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")
    else:
        print("\n>>> SOME TESTS FAILED! <<<")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_tests())
