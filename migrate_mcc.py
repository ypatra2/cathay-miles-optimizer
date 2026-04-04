from db_manager import init_db, save_mcc_mapping
from vendor_overrides import VENDOR_OVERRIDES

def migrate():
    print("Initializing SQLite fallback / DB...")
    init_db()
    
    print(f"Migrating {len(VENDOR_OVERRIDES)} vendors to the unified MCC Registry...")
    for vendor, category in VENDOR_OVERRIDES.items():
        # Extrapolate platform type and generic MCC just for seeding the DB
        platform_type = "online" if "Online" in category or "OTA" in category else "offline"
        save_mcc_mapping(vendor, "SEED_UNKNOWN", platform_type, category)
        
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
