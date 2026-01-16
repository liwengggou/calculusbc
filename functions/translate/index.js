// CloudBase Cloud Function for Tencent Translation API
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

// CloudBase cloud function entry point
exports.main = async (event, context) => {
    // Handle CORS preflight
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            body: '',
        };
    }

    // Only allow POST requests
    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers: { 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ error: 'Method not allowed' }),
        };
    }

    try {
        // Parse request body
        let body;
        if (typeof event.body === 'string') {
            body = JSON.parse(event.body);
        } else {
            body = event.body || {};
        }

        const { text, source = 'auto', target = 'zh' } = body;

        // Validate input
        if (!text || text.length === 0) {
            return {
                statusCode: 400,
                headers: { 'Access-Control-Allow-Origin': '*' },
                body: JSON.stringify({ error: 'Text is required' }),
            };
        }

        if (text.length > 2000) {
            return {
                statusCode: 400,
                headers: { 'Access-Control-Allow-Origin': '*' },
                body: JSON.stringify({ error: 'Text exceeds 2000 character limit' }),
            };
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
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            body: JSON.stringify({
                translation: response.TargetText,
                source: response.Source,
                target: response.Target,
            }),
        };
    } catch (error) {
        console.error('Translation error:', error);
        return {
            statusCode: 500,
            headers: { 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({
                error: 'Translation failed',
                message: error.message,
            }),
        };
    }
};
