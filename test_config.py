import json

def test_config():
    with open('cogs/music.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Checking node configs...")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'node_configs = [' in line:
            for j in range(i, i+15):
                print(lines[j])
            break

test_config()
