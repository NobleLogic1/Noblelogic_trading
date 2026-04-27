const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

class SecureKeyManager {
    constructor() {
        this.algorithm = 'aes-256-gcm';
        this.keyPath = path.join(__dirname, '../.secure');
        this.envPath = path.join(__dirname, '../.env');
        this.encryptedKeysPath = path.join(this.keyPath, 'keys.enc');
        
        // Ensure secure directory exists
        if (!fs.existsSync(this.keyPath)) {
            fs.mkdirSync(this.keyPath, { mode: 0o700 });
        }
        
        this.initializeEncryption();
    }

    initializeEncryption() {
        if (!process.env.ENCRYPTION_KEY) {
            const newKey = crypto.randomBytes(32);
            this.updateEnvFile('ENCRYPTION_KEY', newKey.toString('hex'));
        }
    }

    updateEnvFile(key, value) {
        let envContent = '';
        if (fs.existsSync(this.envPath)) {
            envContent = fs.readFileSync(this.envPath, 'utf8');
        }

        const envLines = envContent.split('\n');
        const keyIndex = envLines.findIndex(line => line.startsWith(`${key}=`));

        if (keyIndex >= 0) {
            envLines[keyIndex] = `${key}=${value}`;
        } else {
            envLines.push(`${key}=${value}`);
        }

        fs.writeFileSync(this.envPath, envLines.join('\n'), { mode: 0o600 });
        dotenv.config(); // Reload environment variables
    }

    encryptApiKeys(apiKey, secretKey) {
        try {
            const iv = crypto.randomBytes(16);
            const salt = crypto.randomBytes(64);
            const key = crypto.pbkdf2Sync(
                process.env.ENCRYPTION_KEY,
                salt,
                100000,
                32,
                'sha512'
            );

            const cipher = crypto.createCipheriv(this.algorithm, key, iv);
            
            // Encrypt API credentials
            const encryptedData = {
                apiKey: this.encryptValue(cipher, apiKey),
                secretKey: this.encryptValue(cipher, secretKey),
                iv: iv.toString('hex'),
                salt: salt.toString('hex'),
                tag: cipher.getAuthTag().toString('hex')
            };

            // Save encrypted data
            fs.writeFileSync(
                this.encryptedKeysPath,
                JSON.stringify(encryptedData),
                { mode: 0o600 }
            );

            return true;
        } catch (error) {
            console.error('Error encrypting API keys:', error);
            return false;
        }
    }

    decryptApiKeys() {
        try {
            const encryptedData = JSON.parse(
                fs.readFileSync(this.encryptedKeysPath, 'utf8')
            );

            const key = crypto.pbkdf2Sync(
                process.env.ENCRYPTION_KEY,
                Buffer.from(encryptedData.salt, 'hex'),
                100000,
                32,
                'sha512'
            );

            const decipher = crypto.createDecipheriv(
                this.algorithm,
                key,
                Buffer.from(encryptedData.iv, 'hex')
            );

            decipher.setAuthTag(Buffer.from(encryptedData.tag, 'hex'));

            return {
                apiKey: this.decryptValue(decipher, encryptedData.apiKey),
                secretKey: this.decryptValue(decipher, encryptedData.secretKey)
            };
        } catch (error) {
            console.error('Error decrypting API keys:', error);
            return null;
        }
    }

    encryptValue(cipher, value) {
        const encrypted = cipher.update(value, 'utf8', 'hex');
        return encrypted + cipher.final('hex');
    }

    decryptValue(decipher, value) {
        const decrypted = decipher.update(value, 'hex', 'utf8');
        return decrypted + decipher.final('utf8');
    }

    validateApiKeys(apiKey, secretKey) {
        // Validate key format
        const apiKeyRegex = /^[A-Za-z0-9]{64}$/;
        const secretKeyRegex = /^[A-Za-z0-9]{64}$/;

        if (!apiKeyRegex.test(apiKey) || !secretKeyRegex.test(secretKey)) {
            throw new Error('Invalid API key format');
        }

        return true;
    }

    rotateEncryptionKey() {
        const newKey = crypto.randomBytes(32);
        const oldKeys = this.decryptApiKeys();
        
        if (oldKeys) {
            this.updateEnvFile('ENCRYPTION_KEY', newKey.toString('hex'));
            return this.encryptApiKeys(oldKeys.apiKey, oldKeys.secretKey);
        }
        
        return false;
    }
}

module.exports = new SecureKeyManager();