package com.vitraining.odoocon2;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Looper;
import android.os.Parcelable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import de.timroes.axmlrpc.XMLRPCCallback;
import de.timroes.axmlrpc.XMLRPCException;
import de.timroes.axmlrpc.XMLRPCServerException;
import java.util.Arrays;
import java.util.List;
import com.telpo.tps550.api.TelpoException;
import com.telpo.tps550.api.TimeoutException;
import com.telpo.tps550.api.magnetic.MagneticCard;

public class SearchActivity extends AppCompatActivity {
    private TextView txtOperation;

    private long memberTaskId;
    private long policyTaskId;
    private long coverageTaskId;
    private long memberPlanIdsTaskId;
    private long claimTaskId;
    private long memberPlanDetailTaskId;


    private String uid;
    private String password;
    private String serverAddress;
    private String database;

    private String operation;

    Member member;
    Claim claim;
    EditText txtCardNo;

    Button buttonSwipeCard;

    private  OdooUtility odoo;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search);

        uid = SharedData.getKey(SearchActivity.this, "uid");
        password = SharedData.getKey(SearchActivity.this, "password");
        serverAddress = SharedData.getKey(SearchActivity.this, "serverAddress");
        database = SharedData.getKey(SearchActivity.this, "database");
        odoo = new OdooUtility(serverAddress, "object");
        member = new Member(SearchActivity.this);
        operation = SharedData.getKey( SearchActivity.this, "operation");

        buttonSwipeCard = (Button) findViewById(R.id.buttonSwipeCard);
        txtCardNo = (EditText) findViewById(R.id.txtCardNo);

        try {
            MagneticCard.open();
            new ReadTask().execute();

        } catch (Exception e) {
            buttonSwipeCard.setEnabled(false);
            AlertDialog.Builder alertDialog = new AlertDialog.Builder(this);
            alertDialog.setTitle(R.string.error);
            alertDialog.setMessage(R.string.error_open_magnetic_card);
            alertDialog.setPositiveButton(R.string.dialog_comfirm,new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    SearchActivity.this.finish();
                }
            });
            alertDialog.show();
        }


        buttonSwipeCard.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                setTitle(getText(R.string.please));
                new ReadTask().execute();
            }
        });
    }

    private class ReadTask extends AsyncTask<Void, Integer, String[]>
    {
        AlertDialog.Builder builder = new AlertDialog.Builder(SearchActivity.this);
        AlertDialog dialog;
        int exit = 0;
        String[] TracData = null;

        @Override
        protected String[] doInBackground(Void... params)
        {
            long strat = System.currentTimeMillis();
            while ((exit != 1) &&
                    (System.currentTimeMillis() - strat < 60000))
            {
                try
                {
                    TracData = MagneticCard.check(200);
                    return TracData;
                } catch (TimeoutException e)
                {
                    e.printStackTrace();
                } catch (TelpoException e)
                {
                    e.printStackTrace();
                    break;
                }
            }
            return null;
        }

        @Override
        protected void onPreExecute()
        {
            builder.setTitle(getString(R.string.magnetic_card_test));
            builder.setMessage("Swipe card now...");
            builder.setNegativeButton("Enter Manually", new DialogInterface.OnClickListener()
            {

                @Override
                public void onClick(DialogInterface dialog, int which)
                {
                    exit = 1;
                }
            });
            dialog = builder.create();
            dialog.show();
        }

        @Override
        protected void onPostExecute(String[] result)
        {
            dialog.dismiss();
            if (result != null)
            {
                for(int i=0; i<3; i++){
                    if(result[i] != null){
                        switch (i)
                        {
                            case 0:
                                String tmp = result[i];
                                txtCardNo.setText(tmp.substring(2,18));
                                break;
//                            case 1:
//                                txtCardNo.setText(result[i]);
//                                break;
//                            case 2:
//                                txtCardNo.setText(result[i]);
//                                break;
                        }

                    }
                }
            }
            else
            {
                Toast.makeText(SearchActivity.this, "Read Card Failed", Toast.LENGTH_SHORT).show();
            }
        }

    }

    @Override
    public void onResume(){
        super.onResume();

        // put your code here...

        txtOperation = (TextView) findViewById(R.id.txtOperation);
        txtOperation.setText(operation);
    }

    @Override
    public void onPause(){
        super.onPause();
        MagneticCard.close();
    }

    public void onClick(View view){
        /*
        cari member ke odoo berdasarkan cardNo
        jika ditemukan, tampilkan eligibiiyt/
         */
        txtCardNo = (EditText) findViewById(R.id.txtCardNo);
        String cardNo = txtCardNo.getText().toString();
        searchMemberByCardNo(cardNo);
    }

    private void searchMemberByCardNo(String cardNo){
        List conditions = Arrays.asList(Arrays.asList(
                Arrays.asList("card_no", "ilike", cardNo)));

        Map fields = new HashMap() {{
            put("fields", Arrays.asList(
                    "id",
                    "class_id",
                    "name",
                    "membership",
                    "card_no",
                    "date_of_birth",
                    "gender_id",
                    "policy_id",
                    "policy_category",
                    "policy_holder",
                    "insurance_period_start",
                    "insurance_period_end",
                    "member_plan_ids"));
            put("limit", 1);
        }};
        memberTaskId = odoo.search_read(listener, database, uid, password, "netpro.member", conditions, fields);
    }

    private void searchMemberPlanIds(List member_plan_ids){
        List conditions = Arrays.asList(Arrays.asList(
                Arrays.asList("id", "in", member_plan_ids)));

        Map fields = new HashMap() {{
            put("fields", Arrays.asList(
                    "id",
                    "plan_schedule_id",
                    "bamount",
                    "plan_limit",
                    "remaining_limit"));
        }};

        memberPlanIdsTaskId = odoo.search_read(listener,  database, uid, password,
                "netpro.member_plan", conditions, fields);
    }

    private void searchBenefits(Object[] memberPlanIds){

        //search current selected coverage's benefits, and wait for response
        //when done, set benefits variable, and call setValues to set the activity values

        ArrayList ids = new ArrayList();
        for (int i=0; i< memberPlanIds.length; i++){
            @SuppressWarnings("unchecked") Map<String,Object> mp=(Map<String,Object>)memberPlanIds[i];
            ids.add((Integer) mp.get("id") );
        }

        List conditions = Arrays.asList(Arrays.asList(Arrays.asList("member_plan_id", "in", ids)));
        Map fields = new HashMap() {{
            put("fields", Arrays.asList("id",
                    "member_plan_id",
                    "benefit_id",
                    "reim",
                    "provider_limit",
                    "non_provider_limit",
                    "unit",
                    "usage",
                    "remaining"));
        }};
        memberPlanDetailTaskId = odoo.search_read(listener,  database, uid, password,
                "netpro.member_plan_detail", conditions, fields);
    }

    private void searchClaim() {

        //search current selected coverage's benefits, and wait for response
        //when done, set benefits variable, and call setValues to set the activity values
        List conditions = Arrays.asList(Arrays.asList(
                        Arrays.asList("member_id", "=", member.getId()),
                        Arrays.asList("state", "=", "open")
                )
        );
        Map fields = new HashMap() {{
            put("fields", Arrays.asList("id",
                    "claim_no",
                    "claim_date",
                    "policy_id",
                    "member_plan_id",
                    "diagnosis_id",
                    "2nd_diagnosis",
                    "3rd_diagnosis",
                    "diagnosis_ids"));
        }};
        claimTaskId = odoo.search_read(listener, database, uid, password, "netpro.claim", conditions, fields);
    }

    private void searchPolicyById(){
        List conditions = Arrays.asList(Arrays.asList(
                Arrays.asList("id", "=", member.getPolicyId() )));

        Map fields = new HashMap() {{
            put("fields", Arrays.asList("policy_no", "coverage_ids"));
        }};

        policyTaskId = odoo.search_read(listener, database, uid, password, "netpro.policy", conditions, fields);
    }

    private void searchCoverages(List converage_ids){
        List conditions = Arrays.asList(Arrays.asList(
                Arrays.asList("id", "in", converage_ids)));

        Map fields = new HashMap() {{
            put("fields", Arrays.asList("id", "product_id"));
        }};

        coverageTaskId = odoo.search_read(listener,  database, uid, password, "netpro.coverage", conditions, fields);
    }

    XMLRPCCallback listener = new XMLRPCCallback() {
        public void onResponse(long id, Object result) {

            Looper.prepare();
            Object[] classObjs=(Object[])result;
            int length=classObjs.length;

            /**
             * step 1 search member
             */
            if (id == memberTaskId) {

                if(length>0){
                    for (int i=0; i < length; i++) {
                        @SuppressWarnings("unchecked") Map<String,Object> classObj=(Map<String,Object>)classObjs[i];

                        member.fillData(classObj);

                        List member_plan_ids = OdooUtility.getOne2Many(classObj, "member_plan_ids");
                        searchMemberPlanIds(member_plan_ids);

                    }

                }
                else {
                    odoo.MessageDialog(SearchActivity.this, "Member not found");
                }
            }

            /**
             * step 2: search member plan: Rawat Inap Class1, Rawat Jalan Class 1, dll
             */
            else if (id==memberPlanIdsTaskId)
            {

                member.fillMemberPlans(classObjs);

                Object[] memberPlanIds = member.getMemberPlanIds();
                searchBenefits( memberPlanIds );

            }
            /**
             * step 3: search member plan details (benefits) utk setiap member plan
             * bisa datang lebih dari 1x
             */
            else if (id==memberPlanDetailTaskId)
            {
                String operation =  SharedData.getKey(SearchActivity.this, "operation");
                member.fillBenefits(classObjs);


                if (operation.equals("registration")){
                    openEligibility();
                }
                else if (operation.equals("discharge")){
                    searchClaim();
                }
                else if (operation.equals("void")){
                    searchClaim();
                }
            }
            else if (id==claimTaskId){
                claim = new Claim();
                String operation =  SharedData.getKey(SearchActivity.this, "operation");

                if(length>0){
                    /**
                     * fill selected member's currently open claim
                     */
                    for (int i=0; i < length; i++) {
                        @SuppressWarnings("unchecked") Map<String, Object> classObj = (Map<String, Object>) classObjs[i];
                        claim.fillData(classObj);
                    }

                    if (operation.equals("discharge")){
                        openDischarge();
                    }
                    else if (operation.equals("void")){
                        openVoid();
                    }

                }
                else
                {
                    odoo.MessageDialog(SearchActivity.this, "Claim data not found");

                }

            }
            else if (id==policyTaskId)
            {
                for (int i=0; i < length; i++) {
                    @SuppressWarnings("unchecked") Map<String, Object> classObj = (Map<String, Object>) classObjs[i];
                    List coverage_ids = OdooUtility.getOne2Many(classObj, "coverage_ids");

                    searchCoverages(coverage_ids);
                }

            }
            else if (id==coverageTaskId)
            {
                ArrayList coverages = new ArrayList();

                for (int i=0; i < length; i++) {
                    @SuppressWarnings("unchecked") Map<String, Object> classObj = (Map<String, Object>) classObjs[i];

                    Integer coverage_id = (Integer)classObj.get("id");

                    M2OField product_id = OdooUtility.getMany2One(classObj, "product_id");
                    Integer productId = product_id.id;
                    String productName = product_id.value;

                    HashMap m = new HashMap();
                    m.put("coverageId", coverage_id);
                    m.put("productName", productName);
                    coverages.add( i, m);
                }
                member.setCoverages(coverages.toArray());

            }
            Looper.loop();
        }

        public void onError(long id, XMLRPCException error) {
            Looper.prepare();
            Log.e("SEARCH ****", error.getMessage());
            odoo.MessageDialog(SearchActivity.this, error.getMessage());
            Looper.loop();
        }

        public void onServerError(long id, XMLRPCServerException error) {
            Looper.prepare();
            Log.e("SEARCH ****", error.getMessage());
            odoo.MessageDialog(SearchActivity.this, error.getMessage());
            Looper.loop();
        }
    };

    private void openEligibility(){
        Intent myIntent = new Intent(SearchActivity.this, EligibilityActivity.class);
        myIntent.putExtra("member",member);
        SearchActivity.this.startActivity(myIntent);
    }

    private void openDischarge(){
        Intent myIntent = new Intent(SearchActivity.this, DischargeActivity.class);
        myIntent.putExtra("member",member);
        myIntent.putExtra("claim",claim);
        SearchActivity.this.startActivity(myIntent);
    }

    private void openVoid(){
        Intent myIntent = new Intent(SearchActivity.this, VoidActivity.class);
        myIntent.putExtra("member",member);
        myIntent.putExtra("claim",claim);
        SearchActivity.this.startActivity(myIntent);
    }


}
