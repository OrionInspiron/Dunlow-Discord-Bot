const nodes = [
  { name: 'MineCuta (NoSSL)', uri: 'http://lavav4.minecuta.com:2333', password: 'discord.gg/gKuXdHs' },
  { name: 'Kasawa (NoSSL)', uri: 'http://lava2.kasawa.pro:2334', password: 'youshallnotpass' },
  { name: 'Amane (SSL)', uri: 'https://lavalinkv4.serenetia.com:443', password: 'https://seretia.link/discord' },
  { name: 'Jirayu (SSL)', uri: 'https://lavalink.jirayu.net:443', password: 'youshallnotpass' },
  { name: 'AneFaiz (SSL)', uri: 'https://lava-v4.millohost.my.id:443', password: 'https://discord.gg/mjS5J2K3ep' },
  { name: 'Trinium 1 (SSL)', uri: 'https://lavalink-v4.triniumhost.com:443', password: 'free' },
  { name: 'Trinium 2 (SSL)', uri: 'https://nodelink.triniumhost.com:443', password: 'free' },
  { name: 'Trinium 3 (SSL)', uri: 'https://nodelink-02.triniumhost.com:443', password: 'trinium' }
];

async function checkNode(node) {
    const start = Date.now();
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
        
        const res = await fetch(`${node.uri}/v4/info`, { 
            headers: { 'Authorization': node.password },
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        const text = await res.text();
        const latency = Date.now() - start;
        
        if (res.ok && text.trim().length > 0) {
            return { ...node, status: 'Online', latency, version: text.trim() };
        } else {
            return { ...node, status: 'Error', error: `Status ${res.status}: ${text.substring(0, 50)}` };
        }
    } catch (e) {
        return { ...node, status: 'Offline', error: e.message };
    }
}

async function run() {
    console.log('Testing SSL and known working nodes...');
    const results = await Promise.all(nodes.map(checkNode));
    
    const online = results.filter(r => r.status === 'Online').sort((a, b) => a.latency - b.latency);
    const offline = results.filter(r => r.status !== 'Online');
    
    console.log('\n--- ONLINE NODES (Sorted by Latency) ---');
    online.forEach(n => console.log(`[${n.latency}ms] ${n.name} (${n.uri}) - v${n.version.substring(0,10)}...`));
    
    console.log('\n--- OFFLINE/ERROR NODES ---');
    offline.forEach(n => console.log(`${n.name} (${n.uri}) - ${n.error}`));
}

run();
