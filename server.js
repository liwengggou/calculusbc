// Local development server for testing translation feature
const http = require('http');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const tencentcloud = require('tencentcloud-sdk-nodejs');
const TmtClient = tencentcloud.tmt.v20180321.Client;

// Initialize Tencent Cloud client
const client = new TmtClient({
    credential: {
        secretId: process.env.TENCENT_SECRET_ID,
        secretKey: process.env.TENCENT_SECRET_KEY,
    },
    region: 'ap-guangzhou',
    profile: {
        signMethod: 'TC3-HMAC-SHA256',
        httpProfile: {
            endpoint: 'tmt.tencentcloudapi.com',
        },
    },
});

const PORT = 5000;

const server = http.createServer(async (req, res) => {
    // Handle translation API
    if (req.url === '/api/translate' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk; });
        req.on('end', async () => {
            try {
                const { text, source = 'auto', target = 'zh' } = JSON.parse(body);

                if (!text || text.length === 0) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    return res.end(JSON.stringify({ error: 'Text is required' }));
                }

                const params = {
                    SourceText: text,
                    Source: source,
                    Target: target,
                    ProjectId: 0,
                };

                const response = await client.TextTranslate(params);

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    translation: response.TargetText,
                    source: response.Source,
                    target: response.Target,
                }));
            } catch (error) {
                console.error('Translation error:', error.message);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Translation failed', message: error.message }));
            }
        });
        return;
    }

    // Serve static files
    let filePath = req.url === '/' ? '/U1.1-Existence-of-Limit.html' : req.url;
    filePath = path.join(__dirname, filePath);

    const extname = path.extname(filePath);
    const contentTypes = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'text/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml',
    };

    fs.readFile(filePath, (err, content) => {
        if (err) {
            res.writeHead(404);
            res.end('File not found');
        } else {
            res.writeHead(200, { 'Content-Type': contentTypes[extname] || 'text/plain' });
            res.end(content);
        }
    });
});

server.listen(PORT, () => {
    console.log(`\n🚀 Server running at http://localhost:${PORT}`);
    console.log(`\n📖 Open http://localhost:${PORT} in your browser`);
    console.log(`\n✅ Translation API ready at http://localhost:${PORT}/api/translate`);
    console.log(`\nPress Ctrl+C to stop the server\n`);
});
