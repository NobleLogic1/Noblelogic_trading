import requests

BASE_URL = 'http://localhost:3001'

def test_endpoints():
    _test_endpoint('Trades', '/api/trades')
    _test_endpoint('Strategy', '/api/strategy')
    _test_endpoint('Health', '/api/health')

def _test_endpoint(name, path):
    try:
        res = requests.get(f'{BASE_URL}{path}')
        res.raise_for_status()
        print(f'\n✅ {name} ({path})')
        print(res.json())
    except Exception as e:
        print(f'\n❌ {name} ({path}) failed: {e}')

if __name__ == '__main__':
    test_endpoints()