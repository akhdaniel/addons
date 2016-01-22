from spyne import Application, ServiceBase, rpc
from spyne import String, Integer, Integer16, Integer64, Double, Boolean, DateTime, ByteArray

from spyne import Mandatory as M
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model import complex

from openerp.service import db
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


def get_registry_cr_uid_context(db_name):
    if db.exp_list():
        registry = RegistryManager.get(db_name)
        cr = registry.cursor()
        context = registry['res.users'].context_get(cr, SUPERUSER_ID)
        return registry, cr, SUPERUSER_ID, context

class ResponseDataMember(complex.ComplexModel):
    member_no = String
    employee_name = String    
    policy_no = String

class Resp_CancelReversalCekIN(complex.ComplexModel):
    CancelReversalCekINResult = Boolean
    errMessage = String

class s(complex.ComplexModel):
    BenefitTotalAmount = String
    Quantity01 = Double
    Quantity02 = Double
    Quantity03 = Double
    Quantity04 = Double
    Quantity05 = Double
    Quantity06 = Double
    Quantity07 = Double
    Quantity08 = Double
    Quantity09 = Double
    Quantity10 = Double
    Quantity11 = Double
    Quantity12 = Double
    Quantity13 = Double
    Quantity14 = Double
    Quantity15 = Double
    Benefit = String
    ClaimNo = String
    TPDU = ByteArray
    ExpiryDate = String
    PAN = String
    MTI = String
    ProcessingCode = String
    TransmisionDate = DateTime
    STAN = String
    ProcessingDate = DateTime
    ProcessingTime = String
    POSEntry = String
    NII = String
    POSCond = String
    Track2 = String
    RetrievalReferenceNumber = String
    ApprovalCode = String
    ResponseCode = String
    TID = String
    MID = String
    TraceNumber = String
    DiagnosticNo = String
    InsuranceName = String
    ErrorMessage = String
    ClaimType = String
    BenefitID1 = String
    BenefitAmount1 = Double
    BenefitID2 = String
    BenefitAmount2 = Double
    BenefitID3 = String
    BenefitAmount3 = Double
    BenefitID4 = String
    BenefitAmount4 = Double
    BenefitID5 = String
    BenefitID6 = String
    BenefitID7 = String
    BenefitID8 = String
    BenefitID9 = String
    BenefitID10 = String
    BenefitID11 = String
    BenefitID12 = String
    BenefitID13 = String
    BenefitID14 = String
    BenefitID15 = String
    BenefitAmount5 = Double
    BenefitAmount6 = Double
    BenefitAmount7 = Double
    BenefitAmount8 = Double
    BenefitAmount9 = Double
    BenefitAmount10 = Double
    BenefitAmount11 = Double
    BenefitAmount12 = Double
    BenefitAmount13 = Double
    BenefitAmount14 = Double
    BenefitAmount15 = Double
    BenefitID00 = String
    BenefitAmount00 = Double
    ApprovedAmount1 = Double
    ExcessAmount1 = Double
    ApprovedAmount2 = Double
    ExcessAmount2 = Double
    ApprovedAmount3 = Double
    ExcessAmount3 = Double
    ApprovedAmount4 = Double
    ExcessAmount4 = Double
    ApprovedAmount5 = Double
    ExcessAmount5 = Double
    ApprovedAmount6 = Double
    ExcessAmount6 = Double
    ApprovedAmount7 = Double
    ExcessAmount7 = Double
    ApprovedAmount8 = Double
    ExcessAmount8 = Double
    ApprovedAmount9 = Double
    ExcessAmount9 = Double
    ApprovedAmount10 = Double
    ExcessAmount10 = Double
    ApprovedAmount11 = Double
    ExcessAmount11 = Double
    ApprovedAmount12 = Double
    ExcessAmount12 = Double
    ApprovedAmount13 = Double
    ExcessAmount13 = Double
    ApprovedAmount14 = Double
    ExcessAmount14 = Double
    ApprovedAmount15 = Double
    ExcessAmount15 = Double
    RemainingLimit = Double
    BatchNumber = String
    CardNo = String
    ReconcileNumOfCheckInTrx = Integer16
    ReconcileTotalCheckInAmount = Integer64
    ReconcileNumOfCheckOutTrx = Integer16
    ReconcileTotalCheckOutAmount = Integer64

class EDCData(complex.ComplexModel):
    BenefitTotalAmount = String
    Quantity01 = Double
    Quantity02 = Double
    Quantity03 = Double
    Quantity04 = Double
    Quantity05 = Double
    Quantity06 = Double
    Quantity07 = Double
    Quantity08 = Double
    Quantity09 = Double
    Quantity10 = Double
    Quantity11 = Double
    Quantity12 = Double
    Quantity13 = Double
    Quantity14 = Double
    Quantity15 = Double
    Benefit = String
    ClaimNo = String
    TPDU = ByteArray
    ExpiryDate = String
    PAN = String
    MTI = String
    ProcessingCode = String
    TransmisionDate = DateTime
    STAN = String
    ProcessingDate = DateTime
    ProcessingTime = String
    POSEntry = String
    NII = String
    POSCond = String
    Track2 = String
    RetrievalReferenceNumber = String
    ApprovalCode = String
    ResponseCode = String
    TID = String
    MID = String
    TraceNumber = String
    DiagnosticNo = String
    InsuranceName = String
    ErrorMessage = String
    ClaimType = String
    BenefitID1 = String
    BenefitAmount1 = Double
    BenefitID2 = String
    BenefitAmount2 = Double
    BenefitID3 = String
    BenefitAmount3 = Double
    BenefitID4 = String
    BenefitAmount4 = Double
    BenefitID5 = String
    BenefitID6 = String
    BenefitID7 = String
    BenefitID8 = String
    BenefitID9 = String
    BenefitID10 = String
    BenefitID11 = String
    BenefitID12 = String
    BenefitID13 = String
    BenefitID14 = String
    BenefitID15 = String
    BenefitAmount5 = Double
    BenefitAmount6 = Double
    BenefitAmount7 = Double
    BenefitAmount8 = Double
    BenefitAmount9 = Double
    BenefitAmount10 = Double
    BenefitAmount11 = Double
    BenefitAmount12 = Double
    BenefitAmount13 = Double
    BenefitAmount14 = Double
    BenefitAmount15 = Double
    BenefitID00 = String
    BenefitAmount00 = Double
    ApprovedAmount1 = Double
    ExcessAmount1 = Double
    ApprovedAmount2 = Double
    ExcessAmount2 = Double
    ApprovedAmount3 = Double
    ExcessAmount3 = Double
    ApprovedAmount4 = Double
    ExcessAmount4 = Double
    ApprovedAmount5 = Double
    ExcessAmount5 = Double
    ApprovedAmount6 = Double
    ExcessAmount6 = Double
    ApprovedAmount7 = Double
    ExcessAmount7 = Double
    ApprovedAmount8 = Double
    ExcessAmount8 = Double
    ApprovedAmount9 = Double
    ExcessAmount9 = Double
    ApprovedAmount10 = Double
    ExcessAmount10 = Double
    ApprovedAmount11 = Double
    ExcessAmount11 = Double
    ApprovedAmount12 = Double
    ExcessAmount12 = Double
    ApprovedAmount13 = Double
    ExcessAmount13 = Double
    ApprovedAmount14 = Double
    ExcessAmount14 = Double
    ApprovedAmount15 = Double
    ExcessAmount15 = Double
    RemainingLimit = Double
    BatchNumber = String
    CardNo = String
    ReconcileNumOfCheckInTrx = Integer16
    ReconcileTotalCheckInAmount = Integer64
    ReconcileNumOfCheckOutTrx = Integer16
    ReconcileTotalCheckOutAmount = Integer64

class Resp_CancelReversalCekOut(complex.ComplexModel):
    CancelReversalCekOutResult = Boolean
    errMessage = String

class Resp_CekDataCheckINResult(complex.ComplexModel):
    CekDataCheckINResult = Boolean

class EDCDataOut(complex.ComplexModel):
    BenefitTotalAmount = String
    Quantity01 = Double
    Quantity02 = Double
    Quantity03 = Double
    Quantity04 = Double
    Quantity05 = Double
    Quantity06 = Double
    Quantity07 = Double
    Quantity08 = Double
    Quantity09 = Double
    Quantity10 = Double
    Quantity11 = Double
    Quantity12 = Double
    Quantity13 = Double
    Quantity14 = Double
    Quantity15 = Double
    Benefit = String
    ClaimNo = String
    TPDU = ByteArray
    ExpiryDate = String
    PAN = String
    MTI = String
    ProcessingCode = String
    TransmisionDate = DateTime
    STAN = String
    ProcessingDate = DateTime
    ProcessingTime = String
    POSEntry = String
    NII = String
    POSCond = String
    Track2 = String
    RetrievalReferenceNumber = String
    ApprovalCode = String
    ResponseCode = String
    TID = String
    MID = String
    TraceNumber = String
    DiagnosticNo = String
    InsuranceName = String
    ErrorMessage = String
    ClaimType = String
    BenefitID1 = String
    BenefitAmount1 = Double
    BenefitID2 = String
    BenefitAmount2 = Double
    BenefitID3 = String
    BenefitAmount3 = Double
    BenefitID4 = String
    BenefitAmount4 = Double
    BenefitID5 = String
    BenefitID6 = String
    BenefitID7 = String
    BenefitID8 = String
    BenefitID9 = String
    BenefitID10 = String
    BenefitID11 = String
    BenefitID12 = String
    BenefitID13 = String
    BenefitID14 = String
    BenefitID15 = String
    BenefitAmount5 = Double
    BenefitAmount6 = Double
    BenefitAmount7 = Double
    BenefitAmount8 = Double
    BenefitAmount9 = Double
    BenefitAmount10 = Double
    BenefitAmount11 = Double
    BenefitAmount12 = Double
    BenefitAmount13 = Double
    BenefitAmount14 = Double
    BenefitAmount15 = Double
    BenefitID00 = String
    BenefitAmount00 = Double
    ApprovedAmount1 = Double
    ExcessAmount1 = Double
    ApprovedAmount2 = Double
    ExcessAmount2 = Double
    ApprovedAmount3 = Double
    ExcessAmount3 = Double
    ApprovedAmount4 = Double
    ExcessAmount4 = Double
    ApprovedAmount5 = Double
    ExcessAmount5 = Double
    ApprovedAmount6 = Double
    ExcessAmount6 = Double
    ApprovedAmount7 = Double
    ExcessAmount7 = Double
    ApprovedAmount8 = Double
    ExcessAmount8 = Double
    ApprovedAmount9 = Double
    ExcessAmount9 = Double
    ApprovedAmount10 = Double
    ExcessAmount10 = Double
    ApprovedAmount11 = Double
    ExcessAmount11 = Double
    ApprovedAmount12 = Double
    ExcessAmount12 = Double
    ApprovedAmount13 = Double
    ExcessAmount13 = Double
    ApprovedAmount14 = Double
    ExcessAmount14 = Double
    ApprovedAmount15 = Double
    ExcessAmount15 = Double
    RemainingLimit = Double
    BatchNumber = String
    CardNo = String
    ReconcileNumOfCheckInTrx = Integer16
    ReconcileTotalCheckInAmount = Integer64
    ReconcileNumOfCheckOutTrx = Integer16
    ReconcileTotalCheckOutAmount = Integer64

class Params_CekMemberInClaim(complex.ComplexModel):
    dbUser = String
    dbPassword = String
    ClaimType = String
    CardNo = String
    sDate = DateTime
    PayTo = String
    errMessage = String
    ResponseCode = String

class Resp_CekMemberInClaim(complex.ComplexModel):
    CekMemberInClaimResult = Boolean
    errMessage = String
    ResponseCode = String
    EDCDataOut

class Resp_CheckOutPatientByEDCResult(complex.ComplexModel):
    CheckOutPatientByEDCResult = Boolean
    EDCDataOut()

class Resp_SaveClaimByEDC(complex.ComplexModel):
    SaveClaimByEDCResult = Boolean
    cno = Integer
    errMessage = String

class ws_netpro(ServiceBase):
	# @rpc(M(String), _returns=M(ResponseDataMember))
	# def get_member(self, member_no):
	# 	path=self.transport.get_path()
	# 	db_name = path.split('/')[2]
	# 	registry, cr, uid, context = get_registry_cr_uid_context(db_name)
	# 	member_model = registry['netpro.member']
	# 	member_id = member_model.search(cr, uid, [('member_no', '=', member_no)], context=context)

	# 	if member_id:
	# 		member = member_model.browse(cr, uid, member_id, context=context)
	# 		response= ResponseDataMember()
	# 		response.member_no = member.member_no
	# 		if member.employee_id.name:
	# 			response.employee_name = member.employee_id.name
	# 		response.policy_no = member.policy_id.policy_no
	# 		return response

    # CANCEL REVERSAL CEK IN
    @rpc(String, String, s, String, _returns=Resp_CancelReversalCekIN)
    def CancelReversalCekIN(self, dbUser, dbPassword, s, errMessage):
        path=self.transport.get_path() # get path sepertinya dari URL
        # import pdb; pdb.set_trace()
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_CancelReversalCekIN()
        res.CancelReversalCekINResult = True
        res.errMessage = ''
        return res

    # CEK DATA CHECK IN
    @rpc(String, String, String, M(String), DateTime, String, String, String, _returns=Resp_CekMemberInClaim)
    def cek_member_in_claim(self, dbUser, dbPassword, ClaimType, CardNo, sDate, PayTo, errMessage, ResponseCode):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        member_model = registry['netpro.member']
        member_id = member_model.search(cr, uid, [('card_no', '=', CardNo)], context=context)

        res = Resp_CekMemberInClaim()
        res.CekMemberInClaimResult = True
        res.errMessage = ''
        res.ResponseCode = ''
        return res

    # CHECK OUT PATIENT BY EDC
    @rpc(String, String, EDCData, EDCDataOut, String, _returns=Resp_CheckOutPatientByEDCResult)
    def check_out_patient_by_edc(self, dbUser, dbPassword, EDCData, EDCDataOut, errMessage):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_CheckOutPatientByEDCResult()
        return res

    # SAVE CLAIM BY EDC
    @rpc(String, String, EDCData, Integer, String, _returns=Resp_SaveClaimByEDC)
    def save_claim_by_edc(self, dbUser, dbPassword, EDCData, cno, errMessage):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_SaveClaimByEDC()
        return res


class SOAPWsgiApplication(WsgiApplication):

    def __call__(self, req_env, start_response, wsgi_url=None):
        """Only match URL requests starting with '/soap/'."""
        if 'HTTP_SOAPACTION' in req_env.keys():
            print 'ANUNYA '+ req_env['HTTP_SOAPACTION']
        if req_env['PATH_INFO'].startswith('/soap/'):
            return super(SOAPWsgiApplication, self).__call__(
                req_env, start_response, wsgi_url)

# Spyne application
application = Application(
    [ws_netpro],
    'http://tempuri.org/',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11())

# WSGI application
wsgi_application = SOAPWsgiApplication(application)