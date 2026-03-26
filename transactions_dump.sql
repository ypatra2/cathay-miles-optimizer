BEGIN TRANSACTION;
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('transactions',2);
CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            vendor TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            recommended_card TEXT NOT NULL,
            miles_earned INTEGER NOT NULL
        );
INSERT INTO "transactions" VALUES(1,'2026-03-27T00:12:50.820376','Cathay Pacific','Cathay Pacific Flights',3852.0,'Standard Chartered Cathay Mastercard',1926);
INSERT INTO "transactions" VALUES(2,'2026-03-27T00:14:02.726034','Keeta','Food Delivery',88.9,'HSBC Red Mastercard',35);
COMMIT;
