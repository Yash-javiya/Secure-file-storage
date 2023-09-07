import { AES, enc, SHA256 } from "crypto-js";
import axios from "axios";

// Function to fetch the data encryption key from the server
async function fetchDataEncryptionKey(username) {
  try {
    const response = await axios.get(`/getkey?username=${username}`);
    return response.data.DataEncryptionKey;
  } catch (error) {
    console.error("Error fetching encryption key:", error);
    throw new Error("Failed to fetch encryption key.");
  }
}

async function deriveKeyFromPassword(password, salt) {
  try {
    // Concatenate the password and salt
    const dataToHash = password + salt;

    // Generate the SHA256 hash of the concatenated data
    const derivedKey = SHA256(dataToHash).toString(); // Convert the hash to a string

    return derivedKey;
  } catch (error) {
    console.error("Error deriving encryption key:", error);
    throw new Error("Failed to derive encryption key.");
  }
}

// Function to encrypt file content using the encryption key
async function encryptFileContent(content, encryptionKey, username) {
  try {
    const derivedKey = await deriveKeyFromPassword(encryptionKey, username);

    const encryptedContent = AES.encrypt(content, derivedKey);

    const encryptedData = encryptedContent.toString(); // Convert encrypted content to a string

    return encryptedData;
  } catch (error) {
    console.error("Error encrypting file content:", error);
    throw new Error("Failed to encrypt file content.");
  }
}

// Function to decrypt file content using the decryption key
async function decryptFileContent(encryptedData, decryptionKey, username) {
  try {

    const derivedKey = await deriveKeyFromPassword(decryptionKey, username);

    const decryptedContent = AES.decrypt(encryptedData, derivedKey);

    const decryptedData = decryptedContent.toString(enc.Utf8);

    return decryptedData;
  } catch (error) {
    console.error("Error decrypting file content:", error);
    throw new Error("Failed to decrypt file content.");
  }
}

async function encryptHandler(fileContent, username) {
  try {
    // Convert the file content to a string if it is not already
    const contentString = typeof fileContent === "string" ? fileContent : fileContent.toString();

    const encryptionKey = await fetchDataEncryptionKey(username);

    // Encrypt the content as a string
    const encryptedData = await encryptFileContent(contentString, encryptionKey, username);

    return encryptedData;
  } catch (error) {
    console.error("Encryption error:", error);
    throw new Error("Failed to encrypt content.");
  }
}

async function decryptHandler(encryptedData, username) {
  try {
    // Fetch the decryption key from the server using the username
    const decryptionKey = await fetchDataEncryptionKey(username);

    // Decrypt the content using the decryption key
    const decryptedData = await decryptFileContent(encryptedData, decryptionKey, username);

    return decryptedData; // Return the decrypted content
  } catch (error) {
    console.error("Decryption error:", error);
    throw new Error("Failed to decrypt content.");
  }
}

export { encryptHandler, decryptHandler };
