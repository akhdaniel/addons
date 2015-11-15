package com.vitraining.odoocon2;

import android.content.Context;
import android.os.Parcel;
import android.os.Parcelable;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * Created by akhmaddanielsembiring on 10/13/15.
 */
public class Member implements Parcelable {


    private Integer id;
    private Integer classId;
    private String className;
    private String name;
    private Integer membershipId;
    private String membershipName;
    private String cardNo;
    private String dateOfBirth;
    private Integer genderId;
    private String genderName;
    private Integer policyId;
    private String policyName;
    private Integer policyCategoryId;
    private String policyCategoryName;
    private Integer policyHolderId;
    private String policyHolderName;
    private String insurancePeriodStart;
    private String insurancePeriodEnd;
    private Object[] coverages;
    private Object[] memberPlanIds;
    private Object[] benefits;

    private Context context;

    /**
     * Standard basic constructor for non-parcel
     * object creation
     */
    public Member(Context context) {
        this.context= context;
    };
    /**
     *
     * Constructor to use when re-constructing object
     * from a parcel
     *
     * @param in a parcel from which to read this object
     */
    public Member(Parcel in) {
        readFromParcel(in);
    }

    // write your object's data to the passed-in Parcel
    @Override
    public void writeToParcel(Parcel dest, int flags) {

        // We just need to write each field into the
        // parcel. When we read from parcel, they
        // will come back in the same order

        dest.writeInt(id);
        dest.writeInt(classId);
        dest.writeString(className);
        dest.writeString(name);
        dest.writeInt(membershipId);
        dest.writeString(membershipName);
        dest.writeString(cardNo);
        dest.writeString(dateOfBirth);
        dest.writeInt(genderId);
        dest.writeString(genderName);
        dest.writeInt(policyId);
        dest.writeString(policyName);
        dest.writeInt(policyCategoryId);
        dest.writeString(policyCategoryName);
        dest.writeInt(policyHolderId);
        dest.writeString(policyHolderName);
        dest.writeString(insurancePeriodStart);
        dest.writeString(insurancePeriodEnd);
        dest.writeArray(coverages);
        dest.writeArray(memberPlanIds);
        dest.writeArray(benefits);
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
        classId = in.readInt();
        className = in.readString();
        name= in.readString();
        membershipId = in.readInt();
        membershipName= in.readString();
        cardNo= in.readString();
        dateOfBirth= in.readString();
        genderId = in.readInt();
        genderName= in.readString();
        policyId = in.readInt();
        policyName= in.readString();
        policyCategoryId = in.readInt();
        policyCategoryName= in.readString();
        policyHolderId = in.readInt();
        policyHolderName= in.readString();
        insurancePeriodStart= in.readString();
        insurancePeriodEnd= in.readString();
        coverages = in.readArray(Member.class.getClassLoader());
        memberPlanIds = in.readArray(Member.class.getClassLoader());
        benefits = in.readArray( Member.class.getClassLoader() );
    }

    public int describeContents() {
        return 0;
    }

    // this is used to regenerate your object. All Parcelables must have a CREATOR that implements these two methods
    public static final Parcelable.Creator<Member> CREATOR = new Parcelable.Creator<Member>() {
        public Member createFromParcel(Parcel in) {
            return new Member(in);
        }

        public Member[] newArray(int size) {
            return new Member[size];
        }
    };



    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getClassName() {
        return className;
    }

    public void setClassName(String className) {
        this.className = className;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getMembershipId() {
        return membershipId;
    }

    public void setMembershipId(Integer membershipId) {
        this.membershipId = membershipId;
    }

    public String getMembershipName() {
        return membershipName;
    }

    public void setMembershipName(String membershipName) {
        this.membershipName = membershipName;
    }

    public String getCardNo() {
        return cardNo;
    }

    public void setCardNo(String cardNo) {
        this.cardNo = cardNo;
    }

    public String getDateOfBirth() {
        return dateOfBirth;
    }

    public void setDateOfBirth(String dateOfBirth) {
        this.dateOfBirth = dateOfBirth;
    }

    public Integer getGenderId() {
        return genderId;
    }

    public void setGenderId(Integer genderId) {
        this.genderId = genderId;
    }

    public String getGenderName() {
        return genderName;
    }

    public void setGenderName(String genderName) {
        this.genderName = genderName;
    }

    public Integer getPolicyId() {
        return policyId;
    }

    public void setPolicyId(Integer policyId) {
        this.policyId = policyId;
    }

    public String getPolicyName() {
        return policyName;
    }

    public void setPolicyName(String policyName) {
        this.policyName = policyName;
    }

    public Integer getPolicyCategoryId() {
        return policyCategoryId;
    }

    public void setPolicyCategoryId(Integer policyCategoryId) {
        this.policyCategoryId = policyCategoryId;
    }

    public String getPolicyCategoryName() {
        return policyCategoryName;
    }

    public void setPolicyCategoryName(String policyCategoryName) {
        this.policyCategoryName = policyCategoryName;
    }

    public Integer getPolicyHolderId() {
        return policyHolderId;
    }

    public void setPolicyHolderId(Integer policyHolderId) {
        this.policyHolderId = policyHolderId;
    }

    public String getPolicyHolderName() {
        return policyHolderName;
    }

    public void setPolicyHolderName(String policyHolderName) {
        this.policyHolderName = policyHolderName;
    }

    public String getInsurancePeriodStart() {
        return insurancePeriodStart;
    }

    public void setInsurancePeriodStart(String insurancePeriodStart) {
        this.insurancePeriodStart = insurancePeriodStart;
    }

    public String getInsurancePeriodEnd() {
        return insurancePeriodEnd;
    }

    public void setInsurancePeriodEnd(String insurancePeriodEnd) {
        this.insurancePeriodEnd = insurancePeriodEnd;
    }

    public Object[] getCoverages() {
        return coverages;
    }

    public void setCoverages(Object[] coverages) {
        this.coverages = coverages;
    }

    public Object[] getMemberPlanIds() {
        return memberPlanIds;
    }

    public void setMemberPlanIds(Object[] memberPlanIds) {
        this.memberPlanIds = memberPlanIds;
    }

    public Object[] getBenefits() {
        return benefits;
    }

    public void setBenefits(Object[] benefits) {
        this.benefits = benefits;
    }

    public Integer getClassId() {
        return classId;
    }

    public void setClassId(Integer classId) {
        this.classId = classId;
    }

    public void fillData(Map<String,Object> classObj){
        M2OField class_id = OdooUtility.getMany2One(classObj, "class_id");
        setClassId(class_id.id);
        setClassName(class_id.value);

        setId((Integer) classObj.get("id"));

        setName((String) classObj.get("name"));

        M2OField membership = OdooUtility.getMany2One(classObj, "membership");
        setMembershipId(membership.id);
        setMembershipName(membership.value);

        setCardNo( OdooUtility.getString(classObj, "card_no"));
        setDateOfBirth(OdooUtility.getString(classObj,"date_of_birth"));

        M2OField gender_id = OdooUtility.getMany2One(classObj, "gender_id");
        setGenderId(gender_id.id);
        setGenderName(gender_id.value);

        M2OField policy_id = OdooUtility.getMany2One(classObj, "policy_id");
        setPolicyId(policy_id.id);
        setPolicyName(policy_id.value);

        M2OField policy_category = OdooUtility.getMany2One(classObj, "policy_category");
        setPolicyCategoryId( policy_category.id);
        setPolicyCategoryName(policy_category.value);

        M2OField policy_holder = OdooUtility.getMany2One(classObj, "policy_holder");
        setPolicyHolderId(policy_holder.id);
        setPolicyHolderName(policy_holder.value);

        setInsurancePeriodStart((String) classObj.get("insurance_period_start"));
        setInsurancePeriodEnd((String) classObj.get("insurance_period_end"));
    }

    public void fillMemberPlans(Object[] classObjs){
        ArrayList memberPlanIds = new ArrayList();
        int length=classObjs.length;

        for (int i=0; i < length; i++)
        {
            @SuppressWarnings("unchecked") Map<String, Object> classObj = (Map<String, Object>) classObjs[i];

            Integer memberPlanId = (Integer)classObj.get("id");
            M2OField plan_schedule_id = OdooUtility.getMany2One(classObj, "plan_schedule_id");
            Integer planScheduleId = plan_schedule_id.id;
            String planScheduleName = plan_schedule_id.value;

            HashMap m = new HashMap();
            m.put("id", memberPlanId);
            m.put("planScheduleId", planScheduleId);
            m.put("planScheduleName", planScheduleName);
            memberPlanIds.add( i, m);
        }
        setMemberPlanIds(memberPlanIds.toArray());
    }

    public void fillBenefits(Object[] classObjs ){
        ArrayList benefits = new ArrayList();
        int length=classObjs.length;
        Benefit benefit = new Benefit(context);
        benefit.deleteAll();

        /*
        add the new benefits
         */
        for (int i=0; i < length; i++) {
            @SuppressWarnings("unchecked") Map<String, Object> classObj = (Map<String, Object>) classObjs[i];

            Integer member_plan_detail_id = (Integer)classObj.get("id");

            M2OField member_plan_id = OdooUtility.getMany2One(classObj, "member_plan_id");
            Integer memberPlanId = member_plan_id.id;
            String  memberPlanName = (String)member_plan_id.value;

            Double   reim= (Double)classObj.get("reim");
            Double   provider_limit = (Double)classObj.get("provider_limit");
            Double   non_provider_limit = (Double)classObj.get("non_provider_limit");

            String   unit="";
            if (classObj.get("unit") instanceof String){
                unit = (String)classObj.get("unit");
            }
            Double   usage = (Double)classObj.get("usage");
            Double   remaining = (Double)classObj.get("remaining");

            M2OField benefit_id = OdooUtility.getMany2One(classObj, "benefit_id");
            Integer benefitId = benefit_id.id;
            String benefitName = benefit_id.value;

            HashMap m = new HashMap();
            m.put("memberPlanDetailId", member_plan_detail_id);
            m.put("memberPlanId", memberPlanId);
            m.put("memberPlanName", memberPlanName);
            m.put("benefitId", benefitId);
            m.put("benefitName", benefitName);
            m.put("reim", reim);
            m.put("providerLimit", provider_limit);
            m.put("nonProviderLimit", non_provider_limit);
            m.put("unit", unit);
            m.put("usage", usage);
            m.put("remaining", remaining);

            benefits.add(i, m);

            benefit.setData(classObj);
            benefit.addToDb();

        }

        setBenefits(benefits.toArray());
    }

}
