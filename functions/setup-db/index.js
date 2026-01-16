const mysql = require('mysql2/promise');

exports.main = async (event, context) => {
  const dbConfig = {
    host: process.env.MYSQL_HOST || '10.34.109.106',
    port: parseInt(process.env.MYSQL_PORT || '3306'),
    user: process.env.MYSQL_USER || 'root',
    password: process.env.MYSQL_PASSWORD,
    database: process.env.MYSQL_DATABASE || 'test-3gop834c099077bf'
  };

  try {
    const connection = await mysql.createConnection(dbConfig);

    // Check current table structure
    const [columns] = await connection.execute(
      "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = ? AND TABLE_NAME = 'annotations'",
      [dbConfig.database]
    );

    const existingColumns = columns.map(c => c.COLUMN_NAME);
    console.log('Existing columns:', existingColumns);

    const results = [];

    // Add missing columns
    if (!existingColumns.includes('quote')) {
      await connection.execute('ALTER TABLE annotations ADD COLUMN quote TEXT');
      results.push('Added column: quote');
    }

    if (!existingColumns.includes('comment')) {
      await connection.execute('ALTER TABLE annotations ADD COLUMN comment TEXT');
      results.push('Added column: comment');
    }

    if (!existingColumns.includes('uri')) {
      await connection.execute('ALTER TABLE annotations ADD COLUMN uri VARCHAR(500)');
      results.push('Added column: uri');

      // Add index for uri
      await connection.execute('ALTER TABLE annotations ADD INDEX idx_uri (uri)');
      results.push('Added index: idx_uri');
    }

    await connection.end();

    return {
      statusCode: 200,
      body: JSON.stringify({
        success: true,
        message: results.length > 0 ? 'Schema updated' : 'Schema already up to date',
        changes: results,
        existingColumns: existingColumns
      })
    };

  } catch (error) {
    console.error('Setup error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        success: false,
        error: error.message
      })
    };
  }
};
