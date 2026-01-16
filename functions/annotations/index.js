const mysql = require('mysql2/promise');

// MySQL connection config
const dbConfig = {
  host: process.env.MYSQL_HOST || '10.34.109.106',
  port: parseInt(process.env.MYSQL_PORT || '3306'),
  user: process.env.MYSQL_USER || 'root',
  password: process.env.MYSQL_PASSWORD,
  database: process.env.MYSQL_DATABASE || 'test-3gop834c099077bf'
};

// Create connection pool
let pool = null;
function getPool() {
  if (!pool) {
    pool = mysql.createPool({
      ...dbConfig,
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0
    });
  }
  return pool;
}

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json'
};

exports.main = async (event, context) => {
  const { httpMethod, queryStringParameters, body } = event;

  // Handle CORS preflight
  if (httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers: corsHeaders, body: '' };
  }

  try {
    const pool = getPool();

    // GET - Load annotations for a URI
    if (httpMethod === 'GET') {
      const uri = queryStringParameters?.uri;
      if (!uri) {
        return {
          statusCode: 400,
          headers: corsHeaders,
          body: JSON.stringify({ error: 'Missing uri parameter' })
        };
      }

      const [rows] = await pool.execute(
        'SELECT id, quote, comment, uri, createdAt FROM annotations WHERE uri = ? ORDER BY createdAt DESC LIMIT 100',
        [uri]
      );

      return {
        statusCode: 200,
        headers: corsHeaders,
        body: JSON.stringify({ data: rows })
      };
    }

    // POST - Save new annotation
    if (httpMethod === 'POST') {
      const data = typeof body === 'string' ? JSON.parse(body) : body;
      const { quote, comment, uri } = data;

      console.log('POST annotation:', { quote: quote?.substring(0, 50), comment: comment?.substring(0, 50), uri });

      if (!quote || !comment || !uri) {
        return {
          statusCode: 400,
          headers: corsHeaders,
          body: JSON.stringify({ error: 'Missing required fields: quote, comment, uri' })
        };
      }

      const [result] = await pool.execute(
        'INSERT INTO annotations (quote, comment, uri, createdAt) VALUES (?, ?, ?, NOW())',
        [quote, comment, uri]
      );

      console.log('Insert result:', { insertId: result.insertId, affectedRows: result.affectedRows });

      return {
        statusCode: 200,
        headers: corsHeaders,
        body: JSON.stringify({
          success: true,
          id: result.insertId
        })
      };
    }

    // DELETE - Remove annotation
    if (httpMethod === 'DELETE') {
      const id = queryStringParameters?.id;
      if (!id) {
        return {
          statusCode: 400,
          headers: corsHeaders,
          body: JSON.stringify({ error: 'Missing id parameter' })
        };
      }

      await pool.execute('DELETE FROM annotations WHERE id = ?', [id]);

      return {
        statusCode: 200,
        headers: corsHeaders,
        body: JSON.stringify({ success: true })
      };
    }

    return {
      statusCode: 405,
      headers: corsHeaders,
      body: JSON.stringify({ error: 'Method not allowed' })
    };

  } catch (error) {
    console.error('Database error:', error.message);
    console.error('Full error:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({
        error: error.message,
        code: error.code || 'UNKNOWN'
      })
    };
  }
};
