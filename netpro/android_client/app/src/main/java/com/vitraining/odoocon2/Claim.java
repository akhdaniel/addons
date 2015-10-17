package com.vitraining.odoocon2;

import android.os.Parcel;
import android.os.Parcelable;

import java.util.List;
import java.util.Map;

/**
 * Created by akhmaddanielsembiring on 10/16/15.
 */
public class Claim implements Parcelable {

    Integer             id;
    String				claimNo = "";
    Integer				claimNoRevision =0;
    String				extClaimNo = "";
    String				claimDate = "";
    String				claimReceivedDate ="";
    String				claimLossDateStart ="";
    String				claimLossDateEnd ="";
    Integer				policyId =0;
    String				policyName ="";
    Integer				memberId =0;
    Integer				claimCategoryId =0;
    Integer				claimTypeId =0;
    Integer				memberPlanId =0;
    String 				memberPlanName ="";
    Integer				diagnosisId =0;
    String 				diagnosisName ="";
    Integer				diagnosis2Id =0;
    String 				diagnosis2Name ="";
    Integer				diagnosis3Id =0;
    String 				diagnosis3Name ="";
    Integer				claimId =0;
    Integer				branchId =0;
    Integer				currencyId =0;
    Double				claimRate =0.0;
    Double				policyRate =0.0;
    Double				reimbursement =0.0;
    Integer				claimRoomId =0;
    Boolean				exgratiaClaim=false;
    Boolean				nonJabodetabek=false;
    Boolean				disableProrate=false;
    Integer				countryId =0;
    String				remarks ="";
    Integer				reasonId =0;
    String				otherReason ="";
    String				sysRemarks ="";
    Double				discount =0.0;
    Double				asoCharge =0.0;
    String				referenceNo ="";
    String				refTpaPayment ="";
    String				refExcess ="";
    Integer				payTo =0;
    Integer				paymentId =0;
    String				accountNo ="";
    String				accountName ="";
    Integer				bankId =0;
    String				bankName ="";
    String				bankBranch ="";
    Integer				excessPayorId =0;
    Integer				excessId =0;
    Integer				excessTpaId =0;
    String				refundAccountNo ="";
    String				refundAccountName ="";
    String				refundBankName ="";
    String				edcTrcAuthorization ="";
    String				edcTrcClaimPayable ="";
    String				state ="";
    String				acceptationStatus ="";
    Integer				cno =0;
    Integer				pcno =0;
    Integer				batchId =0;
    Integer				glid =0;
    Double				prorate =0.0;
    String				paymentStatusRequestDate ="";
    String				paymentStatusPaymentDate ="";
    String				paymentStatusExcessPaymentDate ="";
    String				transactionHistoryCreatedById ="";
    String				transactionHistoryCreatedDate ="";
    String				transactionHistoryLastEditedById ="";
    String				transactionHistoryLastEditedDate ="";
    String				transactionHistoryAdjustedById ="";
    String				transactionHistoryAdjustedDate ="";
    String				transactionHistoryCheckedById ="";
    String				transactionHistoryCheckedDate ="";
    String				transactionHistoryReleasedById ="";
    String				transactionHistoryReleasedDate ="";
    String				doctor ="";
    String				symptoms ="";
    String				diseaseHistory ="";
    String				physExamination ="";
    String				consultation ="";
    Integer				treatmentId =0;
    String				treatmentRemarks ="";
    String				treatmentPlace ="";
    Integer				placeId =0;
    Double				summaryBilled =0.0;
    Double				sumaryUnpaid =0.0;
    Double				summaryDiscount =0.0;
    Double				summaryCashMember =0.0;
    Double				summaryTotalPaid =0.0;
    Double				summaryAccepted =0.0;
    Double				summaryClientAccepted =0.0;
    Double				sumaryTotalExcess =0.0;
    Double				summaryCashMemberAccepted =0.0;
    Double				summaryExcess =0.0;
    Double				summaryVerid =0.0;
    Double				summaryAdjustment =0.0;
    Double				summaryOverallLimit =0.0;
    Double				summaryUsage =0.0;
    Double				summaryBalance =0.0;
    Double				summaryFamilyLimit =0.0;
    Double				summaryFamilyUsage =0.0;
    Double				summaryFamilyBalance =0.0;
    Double				summaryClaimCount =0.0;
    Object[]			claimDetailIds;
    Object[]			diagnosisIds;
    Object[]			claimReasonIds;
    Integer				tpaId =0;
    Integer				providerId =0;

    /**
     * Standard basic constructor for non-parcel
     * object creation
     */
    public Claim() { ; };
    /**
     *
     * Constructor to use when re-constructing object
     * from a parcel
     *
     * @param in a parcel from which to read this object
     */
    public Claim(Parcel in) {
        readFromParcel(in);
    }

    // write your object's data to the passed-in Parcel
    @Override
    public void writeToParcel(Parcel dest, int flags) {

        // We just need to write each field into the
        // parcel. When we read from parcel, they
        // will come back in the same order

        dest.writeInt(id);
        dest.writeString(claimNo);
        dest.writeInt(claimNoRevision);
        dest.writeString(extClaimNo);
        dest.writeString(claimDate);
        dest.writeString(claimReceivedDate);
        dest.writeString(claimLossDateStart);
        dest.writeString(claimLossDateEnd);
        dest.writeInt(policyId);
        dest.writeString(policyName);
        dest.writeInt(memberId);
        dest.writeInt(claimCategoryId);
        dest.writeInt(claimTypeId);
        dest.writeInt(memberPlanId);
        dest.writeString(memberPlanName);
        dest.writeInt(diagnosisId);
        dest.writeString(diagnosisName);
        dest.writeInt(diagnosis2Id);
        dest.writeString(diagnosis2Name);
        dest.writeInt(diagnosis3Id);
        dest.writeString(diagnosis3Name);
        dest.writeInt(claimId);
        dest.writeInt(branchId);
        dest.writeInt(currencyId);
        dest.writeDouble(claimRate);
        dest.writeDouble(policyRate);
        dest.writeDouble(reimbursement);
        dest.writeInt(claimRoomId);
        dest.writeByte((byte)(exgratiaClaim?1:0));
        dest.writeByte((byte)(nonJabodetabek?1:0));
        dest.writeByte((byte)(disableProrate?1:0));
        dest.writeInt(countryId);
        dest.writeString(remarks);
        dest.writeInt(reasonId);
        dest.writeString(otherReason);
        dest.writeString(sysRemarks);
        dest.writeDouble(discount);
        dest.writeDouble(asoCharge);
        dest.writeString(referenceNo);
        dest.writeString(refTpaPayment);
        dest.writeString(refExcess);
        dest.writeInt(payTo);
        dest.writeInt(paymentId);
        dest.writeString(accountNo);
        dest.writeString(accountName);
        dest.writeInt(bankId);
        dest.writeString(bankName);
        dest.writeString(bankBranch);
        dest.writeInt(excessPayorId);
        dest.writeInt(excessId);
        dest.writeInt(excessTpaId);
        dest.writeString(refundAccountNo);
        dest.writeString(refundAccountName);
        dest.writeString(refundBankName);
        dest.writeString(edcTrcAuthorization);
        dest.writeString(edcTrcClaimPayable);
        dest.writeString(state);
        dest.writeString(acceptationStatus);
        dest.writeInt(cno);
        dest.writeInt(pcno);
        dest.writeInt(batchId);
        dest.writeInt(glid);
        dest.writeDouble(prorate);
        dest.writeString(paymentStatusRequestDate);
        dest.writeString(paymentStatusPaymentDate);
        dest.writeString(paymentStatusExcessPaymentDate);
        dest.writeString(transactionHistoryCreatedById);
        dest.writeString(transactionHistoryCreatedDate);
        dest.writeString(transactionHistoryLastEditedById);
        dest.writeString(transactionHistoryLastEditedDate);
        dest.writeString(transactionHistoryAdjustedById);
        dest.writeString(transactionHistoryAdjustedDate);
        dest.writeString(transactionHistoryCheckedById);
        dest.writeString(transactionHistoryCheckedDate);
        dest.writeString(transactionHistoryReleasedById);
        dest.writeString(transactionHistoryReleasedDate);
        dest.writeString(doctor);
        dest.writeString(symptoms);
        dest.writeString(diseaseHistory);
        dest.writeString(physExamination);
        dest.writeString(consultation);
        dest.writeInt(treatmentId);
        dest.writeString(treatmentRemarks);
        dest.writeString(treatmentPlace);
        dest.writeInt(placeId);
        dest.writeDouble(summaryBilled);
        dest.writeDouble(sumaryUnpaid);
        dest.writeDouble(summaryDiscount);
        dest.writeDouble(summaryCashMember);
        dest.writeDouble(summaryTotalPaid);
        dest.writeDouble(summaryAccepted);
        dest.writeDouble(summaryClientAccepted);
        dest.writeDouble(sumaryTotalExcess);
        dest.writeDouble(summaryCashMemberAccepted);
        dest.writeDouble(summaryExcess);
        dest.writeDouble(summaryVerid);
        dest.writeDouble(summaryAdjustment);
        dest.writeDouble(summaryOverallLimit);
        dest.writeDouble(summaryUsage);
        dest.writeDouble(summaryBalance);
        dest.writeDouble(summaryFamilyLimit);
        dest.writeDouble(summaryFamilyUsage);
        dest.writeDouble(summaryFamilyBalance);
        dest.writeDouble(summaryClaimCount);
        dest.writeArray(claimDetailIds);
        dest.writeArray(diagnosisIds);
        dest.writeArray(claimReasonIds);
        dest.writeInt(tpaId);
        dest.writeInt(providerId);
        
    }
    /**
     *
     * Called from the constructor to create this
     * object from a parcel.
     *
     * @param in parcel from which to re-create object
     */
    private void readFromParcel(Parcel in) {

        // We just need to read back each
        // field in the order that it was
        // written to the parcel
        id = in.readInt();
        claimNo = in.readString();
        claimNoRevision = in.readInt();
        extClaimNo = in.readString();
        claimDate = in.readString();
        claimReceivedDate = in.readString();
        claimLossDateStart = in.readString();
        claimLossDateEnd = in.readString();
        policyId = in.readInt();
        policyName = in.readString();
        memberId = in.readInt();
        claimCategoryId = in.readInt();
        claimTypeId = in.readInt();
        memberPlanId = in.readInt();
        memberPlanName = in.readString();
        diagnosisId = in.readInt();
        diagnosisName = in.readString();
        diagnosis2Id = in.readInt();
        diagnosis2Name = in.readString();
        diagnosis3Id = in.readInt();
        diagnosis3Name = in.readString();
        claimId = in.readInt();
        branchId = in.readInt();
        currencyId = in.readInt();
        claimRate = in.readDouble();
        policyRate = in.readDouble();
        reimbursement = in.readDouble();
        claimRoomId = in.readInt();
        exgratiaClaim = in.readByte()!= 0;
        nonJabodetabek = in.readByte()!= 0;
        disableProrate = in.readByte()!= 0;
        countryId = in.readInt();
        remarks = in.readString();
        reasonId = in.readInt();
        otherReason = in.readString();
        sysRemarks = in.readString();
        discount = in.readDouble();
        asoCharge = in.readDouble();
        referenceNo = in.readString();
        refTpaPayment = in.readString();
        refExcess = in.readString();
        payTo = in.readInt();
        paymentId = in.readInt();
        accountNo = in.readString();
        accountName = in.readString();
        bankId = in.readInt();
        bankName = in.readString();
        bankBranch = in.readString();
        excessPayorId = in.readInt();
        excessId = in.readInt();
        excessTpaId = in.readInt();
        refundAccountNo = in.readString();
        refundAccountName = in.readString();
        refundBankName = in.readString();
        edcTrcAuthorization = in.readString();
        edcTrcClaimPayable = in.readString();
        state = in.readString();
        acceptationStatus = in.readString();
        cno = in.readInt();
        pcno = in.readInt();
        batchId = in.readInt();
        glid = in.readInt();
        prorate = in.readDouble();
        paymentStatusRequestDate = in.readString();
        paymentStatusPaymentDate = in.readString();
        paymentStatusExcessPaymentDate = in.readString();
        transactionHistoryCreatedById = in.readString();
        transactionHistoryCreatedDate = in.readString();
        transactionHistoryLastEditedById = in.readString();
        transactionHistoryLastEditedDate = in.readString();
        transactionHistoryAdjustedById = in.readString();
        transactionHistoryAdjustedDate = in.readString();
        transactionHistoryCheckedById = in.readString();
        transactionHistoryCheckedDate = in.readString();
        transactionHistoryReleasedById = in.readString();
        transactionHistoryReleasedDate = in.readString();
        doctor = in.readString();
        symptoms = in.readString();
        diseaseHistory = in.readString();
        physExamination = in.readString();
        consultation = in.readString();
        treatmentId = in.readInt();
        treatmentRemarks = in.readString();
        treatmentPlace = in.readString();
        placeId = in.readInt();
        summaryBilled = in.readDouble();
        sumaryUnpaid = in.readDouble();
        summaryDiscount = in.readDouble();
        summaryCashMember = in.readDouble();
        summaryTotalPaid = in.readDouble();
        summaryAccepted = in.readDouble();
        summaryClientAccepted = in.readDouble();
        sumaryTotalExcess = in.readDouble();
        summaryCashMemberAccepted = in.readDouble();
        summaryExcess = in.readDouble();
        summaryVerid = in.readDouble();
        summaryAdjustment = in.readDouble();
        summaryOverallLimit = in.readDouble();
        summaryUsage = in.readDouble();
        summaryBalance = in.readDouble();
        summaryFamilyLimit = in.readDouble();
        summaryFamilyUsage = in.readDouble();
        summaryFamilyBalance = in.readDouble();
        summaryClaimCount = in.readDouble();
        claimDetailIds = in.readArray(Claim.class.getClassLoader() );
        diagnosisIds = in.readArray( Claim.class.getClassLoader() );
        claimReasonIds = in.readArray( Claim.class.getClassLoader() );
        tpaId = in.readInt();
        providerId = in.readInt();

    }

    public int describeContents() {
        return 0;
    }

    // this is used to regenerate your object. All Parcelables must have a CREATOR that implements these two methods
    public static final Parcelable.Creator<Claim> CREATOR = new Parcelable.Creator<Claim>() {
        public Claim createFromParcel(Parcel in) {
            return new Claim(in);
        }

        public Claim[] newArray(int size) {
            return new Claim[size];
        }
    };

    /**********************************************************************************************
     *
     * @return
     */
    public Integer getProviderId() {
        return providerId;
    }

    public void setProviderId(Integer providerId) {
        this.providerId = providerId;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getClaimNo() {
        return claimNo;
    }

    public void setClaimNo(String claimNo) {
        this.claimNo = claimNo;
    }

    public Integer getClaimNoRevision() {
        return claimNoRevision;
    }

    public void setClaimNoRevision(Integer claimNoRevision) {
        this.claimNoRevision = claimNoRevision;
    }

    public String getExtClaimNo() {
        return extClaimNo;
    }

    public void setExtClaimNo(String extClaimNo) {
        this.extClaimNo = extClaimNo;
    }

    public String getClaimDate() {
        return claimDate;
    }

    public void setClaimDate(String claimDate) {
        this.claimDate = claimDate;
    }

    public String getClaimReceivedDate() {
        return claimReceivedDate;
    }

    public void setClaimReceivedDate(String claimReceivedDate) {
        this.claimReceivedDate = claimReceivedDate;
    }

    public String getClaimLossDateStart() {
        return claimLossDateStart;
    }

    public void setClaimLossDateStart(String claimLossDateStart) {
        this.claimLossDateStart = claimLossDateStart;
    }

    public String getClaimLossDateEnd() {
        return claimLossDateEnd;
    }

    public void setClaimLossDateEnd(String claimLossDateEnd) {
        this.claimLossDateEnd = claimLossDateEnd;
    }

    public Integer getPolicyId() {
        return policyId;
    }

    public void setPolicyId(Integer policyId) {
        this.policyId = policyId;
    }

    public Integer getMemberId() {
        return memberId;
    }

    public void setMemberId(Integer memberId) {
        this.memberId = memberId;
    }

    public Integer getClaimCategoryId() {
        return claimCategoryId;
    }

    public void setClaimCategoryId(Integer claimCategoryId) {
        this.claimCategoryId = claimCategoryId;
    }

    public Integer getClaimTypeId() {
        return claimTypeId;
    }

    public void setClaimTypeId(Integer claimTypeId) {
        this.claimTypeId = claimTypeId;
    }

    public Integer getMemberPlanId() {
        return memberPlanId;
    }

    public void setMemberPlanId(Integer memberPlanId) {
        this.memberPlanId = memberPlanId;
    }

    public Integer getDiagnosisId() {
        return diagnosisId;
    }

    public void setDiagnosisId(Integer diagnosisId) {
        this.diagnosisId = diagnosisId;
    }

    public Integer getDiagnosis2Id() {
        return diagnosis2Id;
    }

    public void setDiagnosis2Id(Integer diagnosis2Id) {
        this.diagnosis2Id = diagnosis2Id;
    }

    public Integer getDiagnosis3Id() {
        return diagnosis3Id;
    }

    public void setDiagnosis3Id(Integer diagnosis3Id) {
        this.diagnosis3Id = diagnosis3Id;
    }

    public Integer getClaimId() {
        return claimId;
    }

    public void setClaimId(Integer claimId) {
        this.claimId = claimId;
    }

    public Integer getBranchId() {
        return branchId;
    }

    public void setBranchId(Integer branchId) {
        this.branchId = branchId;
    }

    public Integer getCurrencyId() {
        return currencyId;
    }

    public void setCurrencyId(Integer currencyId) {
        this.currencyId = currencyId;
    }

    public Double getClaimRate() {
        return claimRate;
    }

    public void setClaimRate(Double claimRate) {
        this.claimRate = claimRate;
    }

    public Double getPolicyRate() {
        return policyRate;
    }

    public void setPolicyRate(Double policyRate) {
        this.policyRate = policyRate;
    }

    public Double getReimbursement() {
        return reimbursement;
    }

    public void setReimbursement(Double reimbursement) {
        this.reimbursement = reimbursement;
    }

    public Integer getClaimRoomId() {
        return claimRoomId;
    }

    public void setClaimRoomId(Integer claimRoomId) {
        this.claimRoomId = claimRoomId;
    }

    public Boolean getExgratiaClaim() {
        return exgratiaClaim;
    }

    public void setExgratiaClaim(Boolean exgratiaClaim) {
        this.exgratiaClaim = exgratiaClaim;
    }

    public Boolean getNonJabodetabek() {
        return nonJabodetabek;
    }

    public void setNonJabodetabek(Boolean nonJabodetabek) {
        this.nonJabodetabek = nonJabodetabek;
    }

    public Boolean getDisableProrate() {
        return disableProrate;
    }

    public void setDisableProrate(Boolean disableProrate) {
        this.disableProrate = disableProrate;
    }

    public Integer getCountryId() {
        return countryId;
    }

    public void setCountryId(Integer countryId) {
        this.countryId = countryId;
    }

    public String getRemarks() {
        return remarks;
    }

    public void setRemarks(String remarks) {
        this.remarks = remarks;
    }

    public Integer getReasonId() {
        return reasonId;
    }

    public void setReasonId(Integer reasonId) {
        this.reasonId = reasonId;
    }

    public String getOtherReason() {
        return otherReason;
    }

    public void setOtherReason(String otherReason) {
        this.otherReason = otherReason;
    }

    public String getSysRemarks() {
        return sysRemarks;
    }

    public void setSysRemarks(String sysRemarks) {
        this.sysRemarks = sysRemarks;
    }

    public Double getDiscount() {
        return discount;
    }

    public void setDiscount(Double discount) {
        this.discount = discount;
    }

    public Double getAsoCharge() {
        return asoCharge;
    }

    public void setAsoCharge(Double asoCharge) {
        this.asoCharge = asoCharge;
    }

    public String getReferenceNo() {
        return referenceNo;
    }

    public void setReferenceNo(String referenceNo) {
        this.referenceNo = referenceNo;
    }

    public String getRefTpaPayment() {
        return refTpaPayment;
    }

    public void setRefTpaPayment(String refTpaPayment) {
        this.refTpaPayment = refTpaPayment;
    }

    public String getRefExcess() {
        return refExcess;
    }

    public void setRefExcess(String refExcess) {
        this.refExcess = refExcess;
    }

    public Integer getPayTo() {
        return payTo;
    }

    public void setPayTo(Integer payTo) {
        this.payTo = payTo;
    }

    public Integer getPaymentId() {
        return paymentId;
    }

    public void setPaymentId(Integer paymentId) {
        this.paymentId = paymentId;
    }

    public String getAccountNo() {
        return accountNo;
    }

    public void setAccountNo(String accountNo) {
        this.accountNo = accountNo;
    }

    public String getAccountName() {
        return accountName;
    }

    public void setAccountName(String accountName) {
        this.accountName = accountName;
    }

    public Integer getBankId() {
        return bankId;
    }

    public void setBankId(Integer bankId) {
        this.bankId = bankId;
    }

    public String getBankName() {
        return bankName;
    }

    public void setBankName(String bankName) {
        this.bankName = bankName;
    }

    public String getBankBranch() {
        return bankBranch;
    }

    public void setBankBranch(String bankBranch) {
        this.bankBranch = bankBranch;
    }

    public Integer getExcessPayorId() {
        return excessPayorId;
    }

    public void setExcessPayorId(Integer excessPayorId) {
        this.excessPayorId = excessPayorId;
    }

    public Integer getExcessId() {
        return excessId;
    }

    public void setExcessId(Integer excessId) {
        this.excessId = excessId;
    }

    public Integer getExcessTpaId() {
        return excessTpaId;
    }

    public void setExcessTpaId(Integer excessTpaId) {
        this.excessTpaId = excessTpaId;
    }

    public String getRefundAccountNo() {
        return refundAccountNo;
    }

    public void setRefundAccountNo(String refundAccountNo) {
        this.refundAccountNo = refundAccountNo;
    }

    public String getRefundAccountName() {
        return refundAccountName;
    }

    public void setRefundAccountName(String refundAccountName) {
        this.refundAccountName = refundAccountName;
    }

    public String getRefundBankName() {
        return refundBankName;
    }

    public void setRefundBankName(String refundBankName) {
        this.refundBankName = refundBankName;
    }

    public String getEdcTrcAuthorization() {
        return edcTrcAuthorization;
    }

    public void setEdcTrcAuthorization(String edcTrcAuthorization) {
        this.edcTrcAuthorization = edcTrcAuthorization;
    }

    public String getEdcTrcClaimPayable() {
        return edcTrcClaimPayable;
    }

    public void setEdcTrcClaimPayable(String edcTrcClaimPayable) {
        this.edcTrcClaimPayable = edcTrcClaimPayable;
    }

    public String getState() {
        return state;
    }

    public void setState(String state) {
        this.state = state;
    }

    public String getAcceptationStatus() {
        return acceptationStatus;
    }

    public void setAcceptationStatus(String acceptationStatus) {
        this.acceptationStatus = acceptationStatus;
    }

    public Integer getCno() {
        return cno;
    }

    public void setCno(Integer cno) {
        this.cno = cno;
    }

    public Integer getPcno() {
        return pcno;
    }

    public void setPcno(Integer pcno) {
        this.pcno = pcno;
    }

    public Integer getBatchId() {
        return batchId;
    }

    public void setBatchId(Integer batchId) {
        this.batchId = batchId;
    }

    public Integer getGlid() {
        return glid;
    }

    public void setGlid(Integer glid) {
        this.glid = glid;
    }

    public Double getProrate() {
        return prorate;
    }

    public void setProrate(Double prorate) {
        this.prorate = prorate;
    }

    public String getPaymentStatusRequestDate() {
        return paymentStatusRequestDate;
    }

    public void setPaymentStatusRequestDate(String paymentStatusRequestDate) {
        this.paymentStatusRequestDate = paymentStatusRequestDate;
    }

    public String getPaymentStatusPaymentDate() {
        return paymentStatusPaymentDate;
    }

    public void setPaymentStatusPaymentDate(String paymentStatusPaymentDate) {
        this.paymentStatusPaymentDate = paymentStatusPaymentDate;
    }

    public String getPaymentStatusExcessPaymentDate() {
        return paymentStatusExcessPaymentDate;
    }

    public void setPaymentStatusExcessPaymentDate(String paymentStatusExcessPaymentDate) {
        this.paymentStatusExcessPaymentDate = paymentStatusExcessPaymentDate;
    }

    public String getTransactionHistoryCreatedById() {
        return transactionHistoryCreatedById;
    }

    public void setTransactionHistoryCreatedById(String transactionHistoryCreatedById) {
        this.transactionHistoryCreatedById = transactionHistoryCreatedById;
    }

    public String getTransactionHistoryCreatedDate() {
        return transactionHistoryCreatedDate;
    }

    public void setTransactionHistoryCreatedDate(String transactionHistoryCreatedDate) {
        this.transactionHistoryCreatedDate = transactionHistoryCreatedDate;
    }

    public String getTransactionHistoryLastEditedById() {
        return transactionHistoryLastEditedById;
    }

    public void setTransactionHistoryLastEditedById(String transactionHistoryLastEditedById) {
        this.transactionHistoryLastEditedById = transactionHistoryLastEditedById;
    }

    public String getTransactionHistoryLastEditedDate() {
        return transactionHistoryLastEditedDate;
    }

    public void setTransactionHistoryLastEditedDate(String transactionHistoryLastEditedDate) {
        this.transactionHistoryLastEditedDate = transactionHistoryLastEditedDate;
    }

    public String getTransactionHistoryAdjustedById() {
        return transactionHistoryAdjustedById;
    }

    public void setTransactionHistoryAdjustedById(String transactionHistoryAdjustedById) {
        this.transactionHistoryAdjustedById = transactionHistoryAdjustedById;
    }

    public String getTransactionHistoryAdjustedDate() {
        return transactionHistoryAdjustedDate;
    }

    public void setTransactionHistoryAdjustedDate(String transactionHistoryAdjustedDate) {
        this.transactionHistoryAdjustedDate = transactionHistoryAdjustedDate;
    }

    public String getTransactionHistoryCheckedById() {
        return transactionHistoryCheckedById;
    }

    public void setTransactionHistoryCheckedById(String transactionHistoryCheckedById) {
        this.transactionHistoryCheckedById = transactionHistoryCheckedById;
    }

    public String getTransactionHistoryCheckedDate() {
        return transactionHistoryCheckedDate;
    }

    public void setTransactionHistoryCheckedDate(String transactionHistoryCheckedDate) {
        this.transactionHistoryCheckedDate = transactionHistoryCheckedDate;
    }

    public String getTransactionHistoryReleasedById() {
        return transactionHistoryReleasedById;
    }

    public void setTransactionHistoryReleasedById(String transactionHistoryReleasedById) {
        this.transactionHistoryReleasedById = transactionHistoryReleasedById;
    }

    public String getTransactionHistoryReleasedDate() {
        return transactionHistoryReleasedDate;
    }

    public void setTransactionHistoryReleasedDate(String transactionHistoryReleasedDate) {
        this.transactionHistoryReleasedDate = transactionHistoryReleasedDate;
    }

    public String getDoctor() {
        return doctor;
    }

    public void setDoctor(String doctor) {
        this.doctor = doctor;
    }

    public String getSymptoms() {
        return symptoms;
    }

    public void setSymptoms(String symptoms) {
        this.symptoms = symptoms;
    }

    public String getDiseaseHistory() {
        return diseaseHistory;
    }

    public void setDiseaseHistory(String diseaseHistory) {
        this.diseaseHistory = diseaseHistory;
    }

    public String getPhysExamination() {
        return physExamination;
    }

    public void setPhysExamination(String physExamination) {
        this.physExamination = physExamination;
    }

    public String getConsultation() {
        return consultation;
    }

    public void setConsultation(String consultation) {
        this.consultation = consultation;
    }

    public Integer getTreatmentId() {
        return treatmentId;
    }

    public void setTreatmentId(Integer treatmentId) {
        this.treatmentId = treatmentId;
    }

    public String getTreatmentRemarks() {
        return treatmentRemarks;
    }

    public void setTreatmentRemarks(String treatmentRemarks) {
        this.treatmentRemarks = treatmentRemarks;
    }

    public String getTreatmentPlace() {
        return treatmentPlace;
    }

    public void setTreatmentPlace(String treatmentPlace) {
        this.treatmentPlace = treatmentPlace;
    }

    public Integer getPlaceId() {
        return placeId;
    }

    public void setPlaceId(Integer placeId) {
        this.placeId = placeId;
    }

    public Double getSummaryBilled() {
        return summaryBilled;
    }

    public void setSummaryBilled(Double summaryBilled) {
        this.summaryBilled = summaryBilled;
    }

    public Double getSumaryUnpaid() {
        return sumaryUnpaid;
    }

    public void setSumaryUnpaid(Double sumaryUnpaid) {
        this.sumaryUnpaid = sumaryUnpaid;
    }

    public Double getSummaryDiscount() {
        return summaryDiscount;
    }

    public void setSummaryDiscount(Double summaryDiscount) {
        this.summaryDiscount = summaryDiscount;
    }

    public Double getSummaryCashMember() {
        return summaryCashMember;
    }

    public void setSummaryCashMember(Double summaryCashMember) {
        this.summaryCashMember = summaryCashMember;
    }

    public Double getSummaryTotalPaid() {
        return summaryTotalPaid;
    }

    public void setSummaryTotalPaid(Double summaryTotalPaid) {
        this.summaryTotalPaid = summaryTotalPaid;
    }

    public Double getSummaryAccepted() {
        return summaryAccepted;
    }

    public void setSummaryAccepted(Double summaryAccepted) {
        this.summaryAccepted = summaryAccepted;
    }

    public Double getSummaryClientAccepted() {
        return summaryClientAccepted;
    }

    public void setSummaryClientAccepted(Double summaryClientAccepted) {
        this.summaryClientAccepted = summaryClientAccepted;
    }

    public Double getSumaryTotalExcess() {
        return sumaryTotalExcess;
    }

    public void setSumaryTotalExcess(Double sumaryTotalExcess) {
        this.sumaryTotalExcess = sumaryTotalExcess;
    }

    public Double getSummaryCashMemberAccepted() {
        return summaryCashMemberAccepted;
    }

    public void setSummaryCashMemberAccepted(Double summaryCashMemberAccepted) {
        this.summaryCashMemberAccepted = summaryCashMemberAccepted;
    }

    public Double getSummaryExcess() {
        return summaryExcess;
    }

    public void setSummaryExcess(Double summaryExcess) {
        this.summaryExcess = summaryExcess;
    }

    public Double getSummaryVerid() {
        return summaryVerid;
    }

    public void setSummaryVerid(Double summaryVerid) {
        this.summaryVerid = summaryVerid;
    }

    public Double getSummaryAdjustment() {
        return summaryAdjustment;
    }

    public void setSummaryAdjustment(Double summaryAdjustment) {
        this.summaryAdjustment = summaryAdjustment;
    }

    public Double getSummaryOverallLimit() {
        return summaryOverallLimit;
    }

    public void setSummaryOverallLimit(Double summaryOverallLimit) {
        this.summaryOverallLimit = summaryOverallLimit;
    }

    public Double getSummaryUsage() {
        return summaryUsage;
    }

    public void setSummaryUsage(Double summaryUsage) {
        this.summaryUsage = summaryUsage;
    }

    public Double getSummaryBalance() {
        return summaryBalance;
    }

    public void setSummaryBalance(Double summaryBalance) {
        this.summaryBalance = summaryBalance;
    }

    public Double getSummaryFamilyLimit() {
        return summaryFamilyLimit;
    }

    public void setSummaryFamilyLimit(Double summaryFamilyLimit) {
        this.summaryFamilyLimit = summaryFamilyLimit;
    }

    public Double getSummaryFamilyUsage() {
        return summaryFamilyUsage;
    }

    public void setSummaryFamilyUsage(Double summaryFamilyUsage) {
        this.summaryFamilyUsage = summaryFamilyUsage;
    }

    public Double getSummaryFamilyBalance() {
        return summaryFamilyBalance;
    }

    public void setSummaryFamilyBalance(Double summaryFamilyBalance) {
        this.summaryFamilyBalance = summaryFamilyBalance;
    }

    public Double getSummaryClaimCount() {
        return summaryClaimCount;
    }

    public void setSummaryClaimCount(Double summaryClaimCount) {
        this.summaryClaimCount = summaryClaimCount;
    }

    public Object[] getClaimDetailIds() {
        return claimDetailIds;
    }

    public void setClaimDetailIds(Object[] claimDetailIds) {
        this.claimDetailIds = claimDetailIds;
    }

    public Object[] getDiagnosisIds() {
        return diagnosisIds;
    }

    public void setDiagnosisIds(Object[] diagnosisIds) {
        this.diagnosisIds = diagnosisIds;
    }

    public Object[] getClaimReasonIds() {
        return claimReasonIds;
    }

    public void setClaimReasonIds(Object[] claimReasonIds) {
        this.claimReasonIds = claimReasonIds;
    }

    public Integer getTpaId() {
        return tpaId;
    }

    public void setTpaId(Integer tpaId) {
        this.tpaId = tpaId;
    }

    public String getPolicyName() {
        return policyName;
    }

    public void setPolicyName(String policyName) {
        this.policyName = policyName;
    }

    public String getMemberPlanName() {
        return memberPlanName;
    }

    public void setMemberPlanName(String memberPlanName) {
        this.memberPlanName = memberPlanName;
    }

    public String getDiagnosisName() {
        return diagnosisName;
    }

    public void setDiagnosisName(String diagnosisName) {
        this.diagnosisName = diagnosisName;
    }

    public String getDiagnosis2Name() {
        return diagnosis2Name;
    }

    public void setDiagnosis2Name(String diagnosis2Name) {
        this.diagnosis2Name = diagnosis2Name;
    }

    public String getDiagnosis3Name() {
        return diagnosis3Name;
    }

    public void setDiagnosis3Name(String diagnosis3Name) {
        this.diagnosis3Name = diagnosis3Name;
    }
    
    public void fillData(Map<String, Object> classObj){
        setId( (Integer) classObj.get("id"));
        setClaimNo(OdooUtility.getString(classObj, "claim_no"));
        setClaimDate(OdooUtility.getString(classObj, "claim_date"));

        M2OField policy_id = OdooUtility.getMany2One(classObj, "policy_id");
        setPolicyId(policy_id.id);
        setPolicyName(policy_id.value);

        M2OField member_plan_id = OdooUtility.getMany2One(classObj, "member_plan_id");
        setMemberPlanId(member_plan_id.id);
        setMemberPlanName(member_plan_id.value);


        M2OField diagnosis_id = OdooUtility.getMany2One(classObj, "diagnosis_id");
        setDiagnosisId(diagnosis_id.id);
        setDiagnosisName(diagnosis_id.value);

        M2OField diagnosis2_id = OdooUtility.getMany2One(classObj, "2nd_diagnosis");
        setDiagnosis2Id( diagnosis2_id.id);
        setDiagnosis2Name(diagnosis2_id.value);

        M2OField diagnosis3_id = OdooUtility.getMany2One(classObj, "3rd_diagnosis");
        setDiagnosis3Id( diagnosis3_id.id);
        setDiagnosis3Name( diagnosis3_id.value);

        List diagnosis = OdooUtility.getOne2Many(classObj, "diagnosis_ids");
        setDiagnosisIds(diagnosis.toArray());
    }
}
