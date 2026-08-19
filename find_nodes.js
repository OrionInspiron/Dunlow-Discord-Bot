const fs = require('fs');
const https = require('https');
const http = require('http');

async function fetchUrl(url) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        client.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

async function testNode(uri, password) {
    return new Promise((resolve) => {
        const url = `${uri}/v4/info`;
        const client = url.startsWith('https') ? https : http;
        const req = client.get(url, {
            headers: { 'Authorization': password },
            timeout: 5000
        }, (res) => {
            if (res.statusCode === 200) {
                resolve(true);
            } else {
                resolve(false);
            }
        });
        
        req.on('error', () => resolve(false));
        req.on('timeout', () => { req.destroy(); resolve(false); });
    });
}

async function main() {
    console.log("Fetching node lists...");
    const urls = [
        "https://raw.githubusercontent.com/DarrenOfficial/lavalink-list/master/docs/NoSSL/Lavalink-NoSSL.md",
        "https://raw.githubusercontent.com/DarrenOfficial/lavalink-list/master/docs/SSL/Lavalink-SSL.md"
    ];
    
    let nodes = [];
    
    for (const url of urls) {
        try {
            const data = await fetchUrl(url);
            const isSSL = url.includes("SSL.md") && !url.includes("NoSSL.md");
            
            // Markdown tables have format | host | port | password | ...
            const lines = data.split('\n');
            for (const line of lines) {
                if (line.includes('|') && !line.includes('---') && !line.includes('Host')) {
                    const parts = line.split('|').map(p => p.trim()).filter(p => p);
                    if (parts.length >= 3) {
                        const host = parts[0].replace(/`/g, '');
                        const port = parts[1].replace(/`/g, '');
                        const password = parts[2].replace(/`/g, '');
                        
                        if (host && port && password && !host.includes('Host') && !host.includes('[')) {
                            const uri = `http${isSSL ? 's' : ''}://${host}:${port}`;
                            nodes.push({ uri, password, isSSL });
                        }
                    }
                }
            }
        } catch (e) {
            console.error("Failed to fetch list:", e.message);
        }
    }
    
    // Also add some statically known v4 nodes to test
    nodes.push({ uri: "http://lava-v4.ajp.pw:2333", password: "youshallnotpass", isSSL: false });
    nodes.push({ uri: "http://188.245.207.225:2333", password: "youshallnotpass", isSSL: false }); // Stackryze
    nodes.push({ uri: "http://lavalink.jirayu.net:13592", password: "youshallnotpass", isSSL: false });

    // Deduplicate
    const unique = [];
    const seen = new Set();
    for (const n of nodes) {
        if (!seen.has(n.uri)) {
            seen.add(n.uri);
            unique.push(n);
        }
    }
    
    console.log(`Found ${unique.length} unique nodes to test. Testing now...`);
    
    const working = [];
    for (const node of unique) {
        const ok = await testNode(node.uri, node.password);
        if (ok) {
            console.log(`✅ WORKING: ${node.uri} (Password: ${node.password})`);
            working.push(node);
        } else {
            // console.log(`❌ FAILED: ${node.uri}`);
        }
    }
    
    console.log(`\nFound ${working.length} working nodes!`);
}

main();
