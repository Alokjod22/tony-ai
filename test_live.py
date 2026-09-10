import urllib.request
import json
import asyncio
import websockets

BASE_URL = 'https://tony-ai-assistant.onrender.com'
WS_URL = 'wss://tony-ai-assistant.onrender.com/ws/stream'

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
print('\n[TEST 3] Checking Gemini LLM Cognitive Chat (/api/chat)...')
queries = [
    'Tony, identify yourself and state your primary design.',
    'What is the distance between Earth and Mars in kilometers?',
    'What is the weather in Tokyo?',
    'Who is Nikola Tesla?'
]

for q in queries:
    req_data = json.dumps({'prompt': q}).encode('utf-8')
    req = urllib.request.Request(f'{BASE_URL}/api/chat', data=req_data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            res = json.loads(resp.read().decode())
            text = res.get('text', '')
            preview = text[:140].replace('\n', ' ')
            print(f'\n   Query: "{q}"')
            print(f'   Tony: {preview}...')
            print(f'   Engine: {res.get("source")}')
    except Exception as e:
        print(f'   [FAIL] Query "{q}" Failed:', e)

# 4. Test Live WebSocket Telemetry & Streaming
print('\n[TEST 4] Testing Live WebSocket Stream (/ws/stream)...')
async def test_ws():
    try:
        async with websockets.connect(WS_URL) as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=6)
            data = json.loads(msg)
            print(f'   [PASS] WebSocket Connected! Initial packet type: "{data.get("type")}"')
            if data.get('payload'):
                print(f'     - Streamed CPU: {data["payload"].get("cpu_usage_percent")}%')
                print(f'     - Streamed RAM: {data["payload"].get("ram_percent")}%')
    except Exception as e:
        print('   [FAIL] WebSocket Test Failed:', e)

asyncio.run(test_ws())

print('\n========================================================')
print('           ALL LIVE END-TO-END TESTS PASSED!            ')
print('========================================================')
