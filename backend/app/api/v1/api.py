from fastapi import APIRouter
from app.api.v1.endpoints import auth,users,erp,employees,client_master,site_master,control_center,roster_master,attendance_master,erp_controls,accounts_master,mobile_sync

api_router=APIRouter()
api_router.include_router(auth.router,prefix="/auth",tags=["Authentication"])
api_router.include_router(users.router,prefix="/users",tags=["Users"])
api_router.include_router(erp.router,prefix="/erp",tags=["Enterprise ERP"])
api_router.include_router(employees.router,prefix="/erp/employees",tags=["Employee Master"])
api_router.include_router(client_master.router,prefix="/erp/clients",tags=["Client Master"])
api_router.include_router(site_master.router,prefix="/erp/sites",tags=["Site Master"])
api_router.include_router(control_center.router,prefix="/erp",tags=["ERP Controls"])
api_router.include_router(roster_master.router,prefix="/erp/rosters",tags=["Roster Master"])
api_router.include_router(attendance_master.router,prefix="/erp/attendance",tags=["Attendance Master"])
api_router.include_router(erp_controls.router,prefix="/erp",tags=["ERP Compliance & Controls"])
api_router.include_router(accounts_master.router,prefix="/erp",tags=["ERP Accounts Workflows"])
api_router.include_router(mobile_sync.router,prefix="/erp",tags=["Mobile ERP Sync"])
