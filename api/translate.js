// api/translate.js - Serverless function for Tencent Cloud Machine Translation
// Works with Vercel, Netlify, or any Node.js serverless platform

const tencentcloud = require('tencentcloud-sdk-nodejs');

const TmtClient = tencentcloud.tmt.v20180321.Client;

// Initialize Tencent Cloud client
const client = new TmtClient({
    credential: {
        secretId: process.env.TENCENT_SECRET_ID,
        secretKey: process.env.TENCENT_SECRET_KEY,
    },
    region: 'ap-guangzhou',  // Options: ap-guangzhou, ap-shanghai, ap-beijing
    profile: {
        signMethod: 'TC3-HMAC-SHA256',
        httpProfile: {
            endpoint: 'tmt.tencentcloudapi.com',
        },
    },
});

module.exports = async (req, res) => {
    // CORS headers for cross-origin requests
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // Handle preflight request
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    // Only allow POST requests
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { text, source = 'auto', target = 'zh' } = req.body;

        // Validate input
        if (!text || text.length === 0) {
            return res.status(400).json({ error: 'Text is required' });
        }

        if (text.length > 2000) {
            return res.status(400).json({ error: 'Text exceeds 2000 character limit' });
        }

        // Call Tencent Translation API
        const params = {
            SourceText: text,
            Source: source,
            Target: target,
            ProjectId: 0,
        };

        const response = await client.TextTranslate(params);

        // Return successful translation
        res.status(200).json({
            translation: response.TargetText,
            source: response.Source,
            target: response.Target,
        });
    } catch (error) {
        console.error('Translation error:', error);
        res.status(500).json({
            error: 'Translation failed',
            message: error.message
        });
    }
};
