package com.vitraining.odoocon2;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.DatabaseUtils;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class Benefit extends SQLiteOpenHelper {

    public static final String DATABASE_NAME = "MyDBName.db";
    public static final String BENFITS_TABLE_NAME = "benefit";
    public static final String BENFITS_COLUMN_ID = "id";
    public static final String BENFITS_COLUMN_NAME = "name";


    Integer id;
    Integer memberPlanId;
    String memberPlanName;
    Integer benefitId;
    String benefitName;
    Double reim;
    Double providerLimit;
    Double nonProviderLimit ;
    String unit;
    Double usage;
    Double remaining;

    public Benefit(Context context)
    {
        super(context, DATABASE_NAME , null, 2);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        // TODO Auto-generated method stub
        db.execSQL(
                "create table benefit " +
                        "(id integer primary key, " +
                        "    memberPlanId integer,\n" +
                        "    memberPlanName text,\n" +
                        "    benefitId integer,\n" +
                        "    benefitName text,\n" +
                        "    reim fload,\n" +
                        "    providerLimit float,\n" +
                        "    nonProviderLimit float,\n" +
                        "    unit string,\n" +
                        "    usage float,\n" +
                        "    remaining float)"
        );
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS benefit");
        onCreate(db);
    }

    public boolean insert( Integer memberPlanId,
            String memberPlanName,
            Integer benefitId,
            String benefitName,
            Double reim,
            Double providerLimit,
            Double nonProviderLimit,
            String unit,
            Double usage,
            Double remaining)
    {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues contentValues = new ContentValues();
        contentValues.put("memberPlanId", memberPlanId);
        contentValues.put("memberPlanName", memberPlanName);
        contentValues.put("benefitId", benefitId);
        contentValues.put("benefitName", benefitName);
        contentValues.put("reim", reim);
        contentValues.put("providerLimit", providerLimit);
        contentValues.put("nonProviderLimit", nonProviderLimit) ;
        contentValues.put("unit", unit);
        contentValues.put("usage", usage);
        contentValues.put("remaining", remaining);

        db.insert("benefit", null, contentValues);
        return true;
    }

    public  void addToDb(){
        insert(memberPlanId,
                memberPlanName,
                benefitId,
                benefitName,
                reim,
                providerLimit,
                nonProviderLimit,
                unit,
                usage,
                remaining);
    }

    public Cursor find(int id){
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor res =  db.rawQuery( "select * from benefit where id="+id+"", null );
        return res;
    }

    public int numberOfRows(){
        SQLiteDatabase db = this.getReadableDatabase();
        int numRows = (int) DatabaseUtils.queryNumEntries(db, BENFITS_TABLE_NAME);
        return numRows;
    }

    public boolean update (Integer id, String field, String value)
    {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues contentValues = new ContentValues();
        contentValues.put(field, value);
        db.update("benefit", contentValues, "id = ? ", new String[]{Integer.toString(id)});
        return true;
    }

    public Integer delete (Integer id)
    {
        SQLiteDatabase db = this.getWritableDatabase();
        return db.delete("benefit",
                "id = ? ",
                new String[] { Integer.toString(id) });
    }

    public ArrayList<String> findAll()
    {
        ArrayList<String> array_list = new ArrayList<String>();

        //hp = new HashMap();
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor res =  db.rawQuery( "select * from benefit", null );
        res.moveToFirst();

        while(res.isAfterLast() == false){
            array_list.add(res.getString(res.getColumnIndex(BENFITS_COLUMN_NAME)));
            res.moveToNext();
        }
        return array_list;
    }


    public void deleteAll(){
        SQLiteDatabase db = this.getReadableDatabase();
        db.execSQL("delete from benefit");
    }

    public void setData(Map<String,Object> classObj){

        Integer member_plan_detail_id =OdooUtility.getInteger(classObj, "id");

        M2OField member_plan_id = OdooUtility.getMany2One(classObj, "member_plan_id");
        Integer memberPlanId = member_plan_id.id;
        String  memberPlanName = (String)member_plan_id.value;

        Double   reim= OdooUtility.getDouble(classObj, "reim");
        Double   provider_limit = OdooUtility.getDouble(classObj,"provider_limit");
        Double   non_provider_limit =  OdooUtility.getDouble(classObj,"non_provider_limit");

        String   unit= OdooUtility.getString(classObj,"unit");
        Double   usage =  OdooUtility.getDouble(classObj,"usage");
        Double   remaining =  OdooUtility.getDouble(classObj,"remaining");

        M2OField benefit_id = OdooUtility.getMany2One(classObj, "benefit_id");
        Integer benefitId = benefit_id.id;
        String benefitName = benefit_id.value;

        setId(member_plan_detail_id);
        setMemberPlanId(memberPlanId);
        setMemberPlanName(memberPlanName);
        setReim(reim);
        setProviderLimit(provider_limit);
        setNonProviderLimit(non_provider_limit);
        setUnit(unit);
        setUsage(usage);
        setRemaining(remaining);
        setBenefitId(benefitId);
        setBenefitName(benefitName);
    }

    public void setById(int id){
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor res =  db.rawQuery("select * from benefit where id=" + id + "", null);
        res.moveToFirst();

        if(res.getCount()>0){
            setId(res.getInt(res.getColumnIndex("id")));
            setMemberPlanId(res.getInt(res.getColumnIndex("memberPlanId")));
            setMemberPlanName(res.getString(res.getColumnIndex("memberPlanName")));
            setBenefitId(res.getInt(res.getColumnIndex("benefitId")));
            setBenefitName(res.getString(res.getColumnIndex("benefitName")));
            setReim(res.getDouble(res.getColumnIndex("reim")));
            setProviderLimit(res.getDouble(res.getColumnIndex("providerLimit")));
            setNonProviderLimit(res.getDouble(res.getColumnIndex("nonProviderLimit")));
            setUnit(res.getString(res.getColumnIndex("unit")));
            setUsage(res.getDouble(res.getColumnIndex("usage")));
            setRemaining(res.getDouble( res.getColumnIndex("remaining")));
        }
    }


    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getMemberPlanId() {
        return memberPlanId;
    }

    public void setMemberPlanId(Integer memberPlanId) {
        this.memberPlanId = memberPlanId;
    }

    public String getMemberPlanName() {
        return memberPlanName;
    }

    public void setMemberPlanName(String memberPlanName) {
        this.memberPlanName = memberPlanName;
    }

    public Integer getBenefitId() {
        return benefitId;
    }

    public void setBenefitId(Integer benefitId) {
        this.benefitId = benefitId;
    }

    public String getBenefitName() {
        return benefitName;
    }

    public void setBenefitName(String benefitName) {
        this.benefitName = benefitName;
    }

    public Double getReim() {
        return reim;
    }

    public void setReim(Double reim) {
        this.reim = reim;
    }

    public Double getProviderLimit() {
        return providerLimit;
    }

    public void setProviderLimit(Double providerLimit) {
        this.providerLimit = providerLimit;
    }

    public Double getNonProviderLimit() {
        return nonProviderLimit;
    }

    public void setNonProviderLimit(Double nonProviderLimit) {
        this.nonProviderLimit = nonProviderLimit;
    }

    public String getUnit() {
        return unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }

    public Double getUsage() {
        return usage;
    }

    public void setUsage(Double usage) {
        this.usage = usage;
    }

    public Double getRemaining() {
        return remaining;
    }

    public void setRemaining(Double remaining) {
        this.remaining = remaining;
    }
}