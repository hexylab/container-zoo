#!/usr/bin/env node

/**
 * Express.js環境テスト用スクリプト
 * サーバーとデータベース環境が正しく構築されているかをテストします
 */

const http = require('http');
const { MongoClient } = require('mongodb');
const redis = require('redis');

// テスト設定
const TEST_CONFIG = {
  server: {
    host: 'localhost',
    port: 3000,
    endpoints: ['/health', '/api/info', '/api/users']
  },
  mongodb: {
    url: 'mongodb://admin:password@mongo:27017/express_app?authSource=admin',
    dbName: 'express_app'
  },
  redis: {
    url: 'redis://redis:6379'
  }
};

// カラー出力用
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
};

function log(message, color = 'green') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function error(message) {
  console.log(`${colors.red}✗ ${message}${colors.reset}`);
}

function success(message) {
  console.log(`${colors.green}✓ ${message}${colors.reset}`);
}

function warning(message) {
  console.log(`${colors.yellow}⚠ ${message}${colors.reset}`);
}

// HTTPリクエスト用ユーティリティ
function makeRequest(options) {
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data
        });
      });
    });
    
    req.on('error', reject);
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    if (options.data) {
      req.write(options.data);
    }
    req.end();
  });
}

// Express サーバーテスト
async function testExpressServer() {
  log('\n=== Express サーバーテスト ===', 'blue');
  
  for (const endpoint of TEST_CONFIG.server.endpoints) {
    try {
      const response = await makeRequest({
        hostname: TEST_CONFIG.server.host,
        port: TEST_CONFIG.server.port,
        path: endpoint,
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.statusCode === 200) {
        success(`${endpoint}: ステータス ${response.statusCode}`);
        
        if (endpoint === '/health') {
          const healthData = JSON.parse(response.body);
          success(`  サーバー稼働時間: ${Math.floor(healthData.uptime)}秒`);
        }
      } else {
        error(`${endpoint}: ステータス ${response.statusCode}`);
      }
    } catch (err) {
      error(`${endpoint}: ${err.message}`);
    }
  }
}

// POST リクエストテスト
async function testPostRequests() {
  log('\n=== POST リクエストテスト ===', 'blue');
  
  try {
    const testUser = {
      name: 'Test User',
      email: 'test@example.com'
    };
    
    const response = await makeRequest({
      hostname: TEST_CONFIG.server.host,
      port: TEST_CONFIG.server.port,
      path: '/api/users',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify(testUser)
    });
    
    if (response.statusCode === 201) {
      success('POST /api/users: ユーザー作成成功');
      const userData = JSON.parse(response.body);
      success(`  作成されたユーザー: ${userData.user.name}`);
    } else {
      error(`POST /api/users: ステータス ${response.statusCode}`);
    }
  } catch (err) {
    error(`POST /api/users: ${err.message}`);
  }
}

// MongoDB接続テスト
async function testMongoDB() {
  log('\n=== MongoDB 接続テスト ===', 'blue');
  
  let client;
  try {
    client = new MongoClient(TEST_CONFIG.mongodb.url);
    await client.connect();
    success('MongoDB接続成功');
    
    const db = client.db(TEST_CONFIG.mongodb.dbName);
    const collections = await db.listCollections().toArray();
    success(`データベース: ${TEST_CONFIG.mongodb.dbName}`);
    success(`コレクション数: ${collections.length}`);
    
    // サンプルデータの挿入テスト
    const testCollection = db.collection('test_users');
    const testDoc = {
      name: 'Test User',
      email: 'test@example.com',
      createdAt: new Date()
    };
    
    const result = await testCollection.insertOne(testDoc);
    success(`ドキュメント挿入成功: ID ${result.insertedId}`);
    
    // 挿入したデータの削除
    await testCollection.deleteOne({ _id: result.insertedId });
    success('テストデータクリーンアップ完了');
    
  } catch (err) {
    error(`MongoDB接続エラー: ${err.message}`);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

// Redis接続テスト
async function testRedis() {
  log('\n=== Redis 接続テスト ===', 'blue');
  
  let client;
  try {
    client = redis.createClient({
      url: TEST_CONFIG.redis.url
    });
    
    await client.connect();
    success('Redis接続成功');
    
    // SET/GET テスト
    const testKey = 'test:key';
    const testValue = 'test-value';
    
    await client.set(testKey, testValue);
    const retrievedValue = await client.get(testKey);
    
    if (retrievedValue === testValue) {
      success('Redis SET/GET テスト成功');
    } else {
      error('Redis SET/GET テスト失敗');
    }
    
    // テストキーの削除
    await client.del(testKey);
    success('テストデータクリーンアップ完了');
    
    // Redis情報の取得
    const info = await client.info('server');
    const redisVersion = info.match(/redis_version:([^\r\n]+)/)?.[1];
    if (redisVersion) {
      success(`Redisバージョン: ${redisVersion}`);
    }
    
  } catch (err) {
    error(`Redis接続エラー: ${err.message}`);
  } finally {
    if (client) {
      await client.quit();
    }
  }
}

// Node.js環境情報
function displayEnvironmentInfo() {
  log('\n=== 環境情報 ===', 'blue');
  success(`Node.js バージョン: ${process.version}`);
  success(`プラットフォーム: ${process.platform}`);
  success(`アーキテクチャ: ${process.arch}`);
  success(`プロセスID: ${process.pid}`);
  success(`メモリ使用量: ${Math.round(process.memoryUsage().rss / 1024 / 1024)}MB`);
}

// メイン実行関数
async function main() {
  log('Express.js 環境テスト開始', 'blue');
  log('=' * 50, 'blue');
  
  displayEnvironmentInfo();
  
  // 順次テスト実行
  await testExpressServer();
  await testPostRequests();
  await testMongoDB();
  await testRedis();
  
  log('\n' + '=' * 50, 'blue');
  log('環境テスト完了', 'blue');
}

// エラーハンドリング
process.on('unhandledRejection', (reason, promise) => {
  error(`未処理のPromise拒否: ${reason}`);
  process.exit(1);
});

process.on('uncaughtException', (err) => {
  error(`未処理の例外: ${err.message}`);
  process.exit(1);
});

// スクリプト実行
if (require.main === module) {
  main().catch((err) => {
    error(`テスト実行エラー: ${err.message}`);
    process.exit(1);
  });
}

module.exports = {
  testExpressServer,
  testMongoDB,
  testRedis,
  makeRequest
};