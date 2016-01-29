import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

from spyne import Application, ServiceBase, rpc
from spyne import String, Integer, Integer16, Integer64, Double, Boolean, DateTime, ByteArray, AnyXml, Unicode

from spyne import Mandatory as M
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model import complex

from openerp.service import db
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID
from lxml import etree

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

class Resp_CekDataCheckINResult(complex.ComplexModel):
    CekDataCheckINResult = Boolean
    EDCDataOut
    errMsg = String

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
    EDCDataOut()

class Resp_CheckOutPatientByEDCResult(complex.ComplexModel):
    CheckOutPatientByEDCResult = Boolean
    EDCDataOut()

class Resp_SaveClaimByEDC(complex.ComplexModel):
    SaveClaimByEDCResult = Boolean
    cno = Integer
    errMessage = String

class DataSet(complex.ComplexModel):
    schema = AnyXml

class Resp_GetDataSet(complex.ComplexModel):
    GetDataSetResult = Boolean
    DataSet()
    ErrMsg = String

class Resp_reversalvoidCekDataCheckIN(complex.ComplexModel):
    reversalvoidCekDataCheckINResult = Boolean
    EDCDataOut()
    errMsg = String

class Resp_reversalvoidCheckOutPatientByEDC(complex.ComplexModel):
    reversalvoidCheckOutPatientByEDCResult = Boolean
    EDCDataOut()
    errmsg = String

class Resp_UpdateSQL(complex.ComplexModel):
    UpdateSQLResult = Boolean
    ErrMsg = String

class Resp_CancelCekIN(complex.ComplexModel):
    CancelCekINResult = Boolean
    s()
    errMessage = String

class Resp_CancelCekOut(complex.ComplexModel):
    CancelCekOutResult = Boolean
    s()
    errMessage = String

class ws_netpro(ServiceBase):

    # CANCEL REVERSAL CEK IN
    @rpc(String, String, s, String, _returns=Boolean)
    def CancelReversalCekIN(self, dbUser, dbPassword, s, errMessage):
        path=self.transport.get_path() # get path sepertinya dari URL
        # import pdb; pdb.set_trace()
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        # res = Resp_CancelReversalCekIN()
        # res.CancelReversalCekINResult = True
        # res.errMessage = ''
        # return res
        print 'KAPANGGIL DA'
        yield True

    @rpc(String, String, s, String, _returns=Boolean)
    def CancelReversalCekOut(self, dbUser, dbPassword, s, errMessage):
        path=self.transport.get_path() # get path sepertinya dari URL
        # import pdb; pdb.set_trace()
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        # res = Resp_CancelReversalCekIN()
        # res.CancelReversalCekINResult = True
        # res.errMessage = ''
        # return res
        yield True

    # CEK DATA CHECK IN
    @rpc(String, String, String, M(String), DateTime, String, String, String, _returns=Resp_CekMemberInClaim)
    def CekMemberInClaim(self, dbUser, dbPassword, ClaimType, CardNo, sDate, PayTo, errMessage, ResponseCode):
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

    @rpc(String, String, EDCData, EDCDataOut, String, _returns=Resp_CekDataCheckINResult)
    def CekDataCheckIN(self, dbUser, dbPassword, EDCData, EDCDataOut, errMsg):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        # create XML 
        # res_bool = etree.Element('CekDataCheckINResult')
        # res_bool.text = True

        # res_edc_data_out = etree.Element('EDCDataOut')
        # BenefitTotalAmount = etree.Element('BenefitTotalAmount')
        # BenefitTotalAmount.text = ''
        # res_edc_data_out.append(BenefitTotalAmount)

        # res_err_msg = etree.Element('errMsg')
        # res_err_msg.text = ''

        # # pretty string
        # a = etree.tostring(res_bool, pretty_print=True)
        # b = etree.tostring(res_edc_data_out, pretty_print=True)
        # c = etree.tostring(res_err_msg, pretty_print=True)

        # yield a, b, c

        # CekDataCheckINResponse
        # CekDataCheckINResult
        # EDCDataOut
        # errMsg

        res = Resp_CekDataCheckINResult()
        res.CekDataCheckINResult = True
        res.EDCDataOut = EDCDataOut
        res.errMsg = ''
        return res

    # CHECK OUT PATIENT BY EDC
    @rpc(String, String, EDCData, EDCDataOut, String, _returns=Resp_CheckOutPatientByEDCResult)
    def CheckOutPatientByEDC(self, dbUser, dbPassword, EDCData, EDCDataOut, errMessage):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_CheckOutPatientByEDCResult()
        return res

    # SAVE CLAIM BY EDC
    @rpc(String, String, EDCData, Integer, String, _returns=Resp_SaveClaimByEDC)
    def SaveClaimByEDC(self, dbUser, dbPassword, EDCData, cno, errMessage):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_SaveClaimByEDC()
        return res

    # GET DATA SET
    @rpc(String, String, DataSet, String, String, _returns=Resp_GetDataSet)
    def GetDataSet(self, dbUser, dbPassword, DataSet, SQL, ErrMsg):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_GetDataSet()
        return res

    # REVERSAL VOID CEK DATA CHECK IN
    @rpc(String, String, EDCData, EDCDataOut, String, _returns=Resp_reversalvoidCekDataCheckIN)
    def reversalvoidCekDataCheckIN(self, dbUser, dbPassword, EDCData, EDCDataOut, errMsg):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_reversalvoidCekDataCheckIN()
        return res

    # REVERSAL VOID CHECK OUT PATIENT BY EDC
    @rpc(String, String, EDCData, EDCDataOut, String, _returns=Resp_reversalvoidCheckOutPatientByEDC)
    def reversalvoidCheckOutPatientByEDC(self, dbUser, dbPassword, EDCData, EDCDataOut, errmsg):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_reversalvoidCheckOutPatientByEDC()
        return res

    # UPDATE SQL
    @rpc(String, String, String, String, _returns=Resp_UpdateSQL)
    def UpdateSQL(self, dbUser, dbPassword, SQL, ErrMsg):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_UpdateSQL()
        return res

    # CANCEL CEK IN
    @rpc(String, String, s, String, String, _returns=Resp_CancelCekIN)
    def UpdateSQL(self, dbUser, dbPassword, s, Tracenumber, errMessage):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_CancelCekIN()
        return res

    # CANCEL CEK OUT
    @rpc(String, String, s, String, String, _returns=Resp_CancelCekOut)
    def UpdateSQL(self, dbUser, dbPassword, s, Tracenumber, errMessage):
        path=self.transport.get_path() # get path sepertinya dari URL
        db_name = path.split('/')[2] # pisahkan berdasarkan / dan ambil array ke 3
        registry, cr, uid, context = get_registry_cr_uid_context(db_name) # pengambilan registry odoo berdasarkan db name

        res = Resp_CancelCekOut()
        return res


class SOAPWsgiApplication(WsgiApplication):

    def __call__(self, req_env, start_response, wsgi_url=None):
        """Only match URL requests starting with '/soap/'."""
        # print req_env
        # if 'HTTP_SOAPACTION' in req_env.keys():
        #     splited = req_env['HTTP_SOAPACTION'].split('/')
        #     print 'ANUNYA ' + splited
        #     #req_env['HTTP_SOAPACTION'] = splited[3]
        if req_env['PATH_INFO'].startswith('/soap/'):
            return super(SOAPWsgiApplication, self).__call__(
                req_env, start_response, wsgi_url)

# Spyne application
application = Application(
    [ws_netpro],
    'http://tempuri.org/',
    in_protocol=Soap11(),
    out_protocol=Soap11())

application.interface.nsmap[None] = application.interface.nsmap['tns']
application.interface.prefmap[application.interface.nsmap['tns']] = None
del application.interface.nsmap['tns']

# WSGI application
wsgi_application = SOAPWsgiApplication(application)
