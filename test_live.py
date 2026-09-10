import urllib.request
import json
import asyncio

BASE_URL = 'https://tony-ai-assistant.onrender.com'

print('========================================================')
print('        TONY AI FULL LIVE CLOUD TEST SUITE              ')
print('========================================================\n')

# 1. Test Static Frontend Assets
print('[TEST 1] Checking Frontend Assets...')
for endpoint in ['/', '/style.css', '/app.js']:
    url = f'{BASE_URL}{endpoint}'
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read()
            print(f'   [PASS] {endpoint:<12} Status {resp.status}, Size: {len(data)} bytes')
    except Exception as e:
        print(f'   [FAIL] {endpoint:<12} Failed: {e}')

# 2. Test Live Telemetry API
print('\n[TEST 2] Checking Live Telemetry API (/api/telemetry)...')
try:
    with urllib.request.urlopen(f'{BASE_URL}/api/telemetry', timeout=10) as resp:
        diag = json.loads(resp.read().decode())
        print('   [PASS] Telemetry received:')
        print(f'     - OS: {diag.get("os")}')
        print(f'     - CPU: {diag.get("cpu_usage_percent")}%')
        print(f'     - RAM: {diag.get("ram_percent")}% ({diag.get("ram_used_gb")} GB)')
        print(f'     - Battery: {diag.get("battery_percent")}')
except Exception as e:
    print('   [FAIL] Telemetry API Failed:', e)

# 3. Test Gemini Cognitive Reasoning & Persona
print('\n[TEST 3] Checking Cognitive Chat API (/api/chat)...')
queries = [
    'Tony, identify yourself and state your primary design.',
    'What is your active security posture?',
    'Give me a brief tactical assessment of current system resources.'
]

for q in queries:
    req_data = json.dumps({'prompt': q, 'persona': 'tony', 'reasoning_mode': 'balanced'}).encode('utf-8')
    req = urllib.request.Request(f'{BASE_URL}/api/chat', data=req_data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            res = json.loads(resp.read().decode())
            text = res.get('text', '')
            preview = text[:140].replace('\n', ' ')
            print(f'\n   Query: "{q}"')
            print(f'   Tony: {preview}...')
    except Exception as e:
        print(f'   [FAIL] Query "{q}" Failed:', e)

print('\n========================================================')
print('           ALL LIVE END-TO-END TESTS COMPLETED!         ')
print('========================================================')
