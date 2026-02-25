const fs = require('fs');
const { Keypair } = require('@solana/web3.js');
const nacl = require('tweetnacl');
const bs58 = require('bs58');

// Install bs58 if needed
try {
  require('bs58');
} catch (e) {
  console.log('Installing bs58...');
  require('child_process').execSync('npm install bs58', {stdio: 'inherit'});
}

// Load keypair
const keypairData = JSON.parse(fs.readFileSync('moltwars-wallet.json'));
const keypair = Keypair.fromSecretKey(new Uint8Array(keypairData));

// Create auth message
const timestamp = Date.now();
const message = `molt-of-empires:${timestamp}`;
const messageBytes = new TextEncoder().encode(message);

// Sign message
const signature = nacl.sign.detached(messageBytes, keypair.secretKey);
const base58Signature = bs58.encode(signature);

// Create auth header value  
const authHeader = `${keypair.publicKey.toBase58()}:${base58Signature}:${timestamp}`;

console.log('Public Key:', keypair.publicKey.toBase58());
console.log('Message:', message);  
console.log('Auth Header:', authHeader);
console.log('Timestamp:', timestamp);