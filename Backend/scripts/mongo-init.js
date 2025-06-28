// Real Estate Platform MongoDB Initialization
// MongoDB 7+ required

// Switch to realestate_documents database
db = db.getSiblingDB('realestate_documents');

// Create collections with validation
db.createCollection("property_documents", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["property_id", "document_type", "file_url", "created_at"],
            properties: {
                property_id: { bsonType: "string" },
                document_type: { enum: ["PLAN", "CERTIFICATE", "CONTRACT", "OTHER"] },
                file_url: { bsonType: "string" },
                created_at: { bsonType: "date" }
            }
        }
    }
});

db.createCollection("application_logs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["level", "message", "timestamp"],
            properties: {
                level: { enum: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] },
                message: { bsonType: "string" },
                timestamp: { bsonType: "date" }
            }
        }
    }
});

db.createCollection("user_sessions", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["user_id", "session_data", "created_at"],
            properties: {
                user_id: { bsonType: "string" },
                session_data: { bsonType: "object" },
                created_at: { bsonType: "date" }
            }
        }
    }
});

// Create indexes
db.property_documents.createIndex({ "property_id": 1 });
db.property_documents.createIndex({ "document_type": 1 });
db.property_documents.createIndex({ "created_at": -1 });

db.application_logs.createIndex({ "timestamp": -1 });
db.application_logs.createIndex({ "level": 1 });

db.user_sessions.createIndex({ "user_id": 1 });
db.user_sessions.createIndex({ "created_at": 1 }, { expireAfterSeconds: 604800 }); // 7 days

print("MongoDB initialized successfully");
