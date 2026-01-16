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

// Cloud function entry point for callFunction
// Event format: { method: 'GET'|'POST'|'DELETE', uri, quote, comment, id }
exports.main = async (event, context) => {
  const { method, uri, quote, comment, id } = event;

  console.log('Annotations function called:', { method, uri });

  try {
    const pool = getPool();

    // GET - Load annotations for a URI
    if (method === 'GET') {
      if (!uri) {
        return { success: false, error: 'Missing uri parameter' };
      }

      const [rows] = await pool.execute(
        'SELECT id, quote, comment, uri, createdAt FROM annotations WHERE uri = ? ORDER BY createdAt DESC LIMIT 100',
        [uri]
      );

      console.log('Loaded', rows.length, 'annotations for', uri);
      return { success: true, data: rows };
    }

    // POST - Save new annotation
    if (method === 'POST') {
      console.log('Saving annotation:', { quote: quote?.substring(0, 50), comment: comment?.substring(0, 50), uri });

      if (!quote || !comment || !uri) {
        return { success: false, error: 'Missing required fields: quote, comment, uri' };
      }

      const [result] = await pool.execute(
        'INSERT INTO annotations (quote, comment, uri, createdAt) VALUES (?, ?, ?, NOW())',
        [quote, comment, uri]
      );

      console.log('Insert result:', { insertId: result.insertId, affectedRows: result.affectedRows });
      return { success: true, id: result.insertId };
    }

    // DELETE - Remove annotation
    if (method === 'DELETE') {
      if (!id) {
        return { success: false, error: 'Missing id parameter' };
      }

      await pool.execute('DELETE FROM annotations WHERE id = ?', [id]);
      console.log('Deleted annotation:', id);
      return { success: true };
    }

    return { success: false, error: 'Invalid method. Use GET, POST, or DELETE.' };

  } catch (error) {
    console.error('Database error:', error.message);
    console.error('Full error:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
    return {
      success: false,
      error: error.message,
      code: error.code || 'UNKNOWN'
    };
  }
};
