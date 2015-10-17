package com.vitraining.odoocon2;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Looper;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import de.timroes.axmlrpc.XMLRPCCallback;
import de.timroes.axmlrpc.XMLRPCException;
import de.timroes.axmlrpc.XMLRPCServerException;

public class RegistrationActivity extends AppCompatActivity {
    private TextView txtName;
    private TextView txtClassName;
    private TextView txtMembershipName;
    private TextView txtCardNo;
    private TextView txtDateOfBirth;
    private TextView txtGenderName;
    private TextView txtPolicyName;
    private TextView txtPolicyCategoryName;
    private TextView txtPolicyHolderName;
    private TextView txtInsurancePeriodStart;
    private TextView txtInsurancePeriodEnd;

    Member member ;
    Integer memberPlanId;
    long createClaimTaskId;
    long confirmClaimTaskId;

    long planScheduleTaskId;
    private OdooUtility odoo;
    private String uid;
    private String password;
    private String serverAddress;
    private String database;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_registration);

        uid = SharedData.getKey(RegistrationActivity.this, "uid");
        password = SharedData.getKey(RegistrationActivity.this, "password");
        serverAddress = SharedData.getKey(RegistrationActivity.this, "serverAddress");
        database = SharedData.getKey(RegistrationActivity.this, "database");
        odoo = new OdooUtility(serverAddress, "object");

        Intent intent = getIntent();
        member = intent.getParcelableExtra("member");
        memberPlanId = intent.getIntExtra("memberPlanId", 0);
        setValues();

    }

    private void  setValues(){

        /**
         * ambil text view dari layout
         */
        txtName = (TextView) findViewById(R.id.txtName);
        txtClassName = (TextView) findViewById(R.id.txtClassName);
        txtMembershipName = (TextView) findViewById(R.id.txtMembershipName);
        txtCardNo = (TextView) findViewById(R.id.txtCardNo);
        txtDateOfBirth = (TextView) findViewById(R.id.txtDateOfBirth);
        txtGenderName = (TextView) findViewById(R.id.txtGenderName);
        txtPolicyName = (TextView) findViewById(R.id.txtPolicyName);
        txtPolicyCategoryName = (TextView) findViewById(R.id.txtPolicyCategoryName);
        txtPolicyHolderName = (TextView) findViewById(R.id.txtPolicyHolderName);
        txtInsurancePeriodStart = (TextView) findViewById(R.id.txtInsurancePeriodStart);
        txtInsurancePeriodEnd = (TextView) findViewById(R.id.txtInsurancePeriodEnd);


        /**
         * set text values
         */
        txtName.setText(member.getName());
        txtClassName.setText(member.getClassName());
        txtMembershipName.setText(member.getMembershipName());
        txtCardNo.setText(member.getCardNo());
        txtDateOfBirth.setText(member.getDateOfBirth());
        txtGenderName.setText(member.getGenderName());
        txtPolicyName.setText(member.getPolicyName());
        txtPolicyCategoryName.setText(member.getPolicyCategoryName());
        txtPolicyHolderName.setText(member.getPolicyHolderName());
        txtInsurancePeriodStart.setText(member.getInsurancePeriodStart());
        txtInsurancePeriodEnd.setText(member.getInsurancePeriodEnd());


        /**
         * tampilan benefits table
         */
        showBenefits();

    }

    private void showBenefits(){
        TableLayout tl = (TableLayout) findViewById(R.id.tblLayoutBenefit);

        TableRow th = new TableRow(this);
        th.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

        TextView col1 = new TextView(this);
        col1.setText("Benefit");
        col1.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

        TextView col2 = new TextView(this);
        col2.setText("Unit");
        col2.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

        TextView col3 = new TextView(this);
        col3.setText( "Usage");
        col3.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

        TextView col4 = new TextView(this);
        col4.setText( "Remaining");
        col4.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

        th.addView(col1);
        th.addView(col2);
        th.addView(col3);
        th.addView(col4);

        tl.addView(th, new TableLayout.LayoutParams(TableLayout.LayoutParams.MATCH_PARENT, TableLayout.LayoutParams.WRAP_CONTENT));

        Object[] benefits = member.getBenefits();
        for (int i=0 ; i< benefits.length; i++)
        {
            HashMap benefit = (HashMap)benefits[i];

            if(benefit.get("memberPlanId") != memberPlanId)
                continue;

            TableRow tr = new TableRow(this);
            tr.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));


            TextView tdcol1 = new TextView(this);
            tdcol1.setText((String)benefit.get("benefitName"));
            tdcol1.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

            TextView tdcol2 = new TextView(this);
            tdcol2.setText((String)benefit.get("unit"));
            tdcol2.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

            TextView tdcol3 = new TextView(this);
            tdcol3.setText( benefit.get("usage").toString());
            tdcol3.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

            TextView tdcol4 = new TextView(this);
            tdcol4.setText( benefit.get("remaining").toString());
            tdcol4.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

            tr.addView(tdcol1);
            tr.addView(tdcol2);
            tr.addView(tdcol3);
            tr.addView(tdcol4);

            tl.addView(tr, new TableLayout.LayoutParams(TableLayout.LayoutParams.MATCH_PARENT, TableLayout.LayoutParams.WRAP_CONTENT));

        }
    }

    public void onClick(View view){
        confirmClaim();
    }

    private void confirmClaim(){
        uid = SharedData.getKey(RegistrationActivity.this, "uid");
        password = SharedData.getKey(RegistrationActivity.this, "password");
        serverAddress = SharedData.getKey(RegistrationActivity.this, "serverAddress");
        database = SharedData.getKey(RegistrationActivity.this, "database");
        odoo = new OdooUtility(serverAddress, "object");

        List data = Arrays.asList(new HashMap() {{
            put("policy_id", member.getPolicyId());
            put("member_id",member.getId());
            put("member_plan_id",memberPlanId);
        }});
        createClaimTaskId = odoo.create(listener, database, uid, password, "netpro.claim", data);

    }

    XMLRPCCallback listener = new XMLRPCCallback() {
        public void onResponse(long id, Object result) {

            Looper.prepare();

            if (id==createClaimTaskId)
            {
                final Integer claimId =(Integer)result;
                Log.v("CLAIM CREATED", "successfully created with id=" + claimId);
                Log.v("CLAIM CONFIRMED", "successfully");

                AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(RegistrationActivity.this);
                alertDialogBuilder.setMessage("Successfully created new Claim" )
                        .setCancelable(false)
                        .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                dialog.dismiss();
                                // Do stuff if user accepts
                                Intent myIntent = new Intent(RegistrationActivity.this, MenuActivity.class);
                                myIntent.putExtra("member", member);
                                RegistrationActivity.this.startActivity(myIntent);
                            }
                        }).create().show();

//                List data = Arrays.asList( claimId );
//                confirmClaimTaskId = odoo.exec(listener, database, uid, password, "netpro.claim", "action_open", data);
            }
            else if (id==confirmClaimTaskId)
            {
                final Boolean confirmResult =(Boolean)result;

                if(confirmResult){

                    Log.v("CLAIM CONFIRMED", "successfully");

                    AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(RegistrationActivity.this);
                    alertDialogBuilder.setMessage("Successfully created and confirmed new Claim" )
                            .setCancelable(false)
                            .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                                @Override
                                public void onClick(DialogInterface dialog, int which) {
                                    dialog.dismiss();
                                    // Do stuff if user accepts
                                    Intent myIntent = new Intent(RegistrationActivity.this, MenuActivity.class);
                                    myIntent.putExtra("member", member);
                                    RegistrationActivity.this.startActivity(myIntent);
                                }
                            }).create().show();

                }
                else
                {
                    odoo.MessageDialog(RegistrationActivity.this, "Create of confirm Claim failed. Result from server is false");
                }
            }
            Looper.loop();

        }
        public void onError(long id, XMLRPCException error) {
            Log.e("SEARCH ****", error.getMessage());
            OdooUtility.MessageDialog(RegistrationActivity.this, error.getMessage());
        }
        public void onServerError(long id, XMLRPCServerException error) {
            Log.e("SEARCH ****",error.getMessage());
            OdooUtility.MessageDialog(RegistrationActivity.this, error.getMessage());
        }
    };

}

