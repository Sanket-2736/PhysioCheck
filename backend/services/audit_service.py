from database.models import AuditLog

class AuditService:
    @staticmethod
    async def log(db, admin_id, action, target_type, target_id, description):
        log = AuditLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description
        )
        db.add(log)
        await db.commit()
