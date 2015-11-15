package com.vitraining.odoocon2;

import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.BatteryManager;
import android.os.Looper;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Toast;

import com.telpo.tps550.api.printer.ThermalPrinter;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import de.timroes.axmlrpc.XMLRPCCallback;
import de.timroes.axmlrpc.XMLRPCException;
import de.timroes.axmlrpc.XMLRPCServerException;

public class DischargeActivity extends AppCompatActivity {
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
    private TextView txtClaimNo;
    private TextView txtClaimDate;
    private TextView txtMemberPlan;
    private Button buttonPrint;

    Member member;
    String state ;
    Claim claim;
    long updateClaimTaskId;
    long confirmClaimTaskId;

    private OdooUtility odoo;
    private String uid;
    private String password;
    private String serverAddress;
    private String database;

    List billedAmounts;


    PrinterHandler handler;
    private ProgressDialog progressDialog;
    ProgressDialog dialog;
    private Boolean nopaper = false;
    private boolean LowBattery = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_discharge);

        uid = SharedData.getKey(DischargeActivity.this, "uid");
        password = SharedData.getKey(DischargeActivity.this, "password");
        serverAddress = SharedData.getKey(DischargeActivity.this, "serverAddress");
        database = SharedData.getKey(DischargeActivity.this, "database");
        odoo = new OdooUtility(serverAddress, "object");

        Intent intent = getIntent();
        member = (Member) intent.getParcelableExtra("member");
        claim = (Claim) intent.getParcelableExtra("claim");
        state = intent.getStringExtra("state");

        billedAmounts = new ArrayList();

        setValues();
        handler = new PrinterHandler(DischargeActivity.this);
        IntentFilter pIntentFilter = new IntentFilter();
        pIntentFilter.addAction(Intent.ACTION_BATTERY_CHANGED);
//        pIntentFilter.addAction(PRINT_VERSION_CHANGE);
        registerReceiver(printReceive, pIntentFilter);

    }

    private void setValues() {

        /**
         * ambil object text view dari layout
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
        txtClaimNo = (TextView) findViewById(R.id.txtClaimNo);
        txtClaimDate = (TextView) findViewById(R.id.txtClaimDate);
        txtMemberPlan = (TextView) findViewById(R.id.txtMemberPlan);
        buttonPrint = (Button) findViewById(R.id.buttonPrint);

        /**
         * isi text view values
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
        txtClaimNo.setText(claim.getClaimNo());
        txtClaimDate.setText(claim.getClaimDate());
        txtMemberPlan.setText(claim.getMemberPlanName());


        buttonPrint.setEnabled(false);
        if(state != null){
            if (state.equals("open")){
                buttonPrint.setEnabled(true);
            }
        }

        /**
         * show form isian benefit amount
         */
        showBenefitsForm();

        /**
         * show form isian pilihan diagnosis
         */
        showDiagnosisForm();

        /**
         * show tombol kirim utk update claim
         */

    }

    private void showBenefitsForm(){
        TableLayout tl = (TableLayout) findViewById(R.id.tableLayoutBenefit);
        tl.setColumnStretchable(2, true);

        TableRow th = new TableRow(this);
        th.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

        TextView col1 = new TextView(this);
        col1.setText("Benefit");
        col1.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

        TextView col2 = new TextView(this);
        col2.setText("Billed Amount");
        col2.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));


        th.addView(col1);
        th.addView(col2);


        tl.addView(th, new TableLayout.LayoutParams(TableLayout.LayoutParams.MATCH_PARENT, TableLayout.LayoutParams.WRAP_CONTENT));

        Object[] benefits = member.getBenefits();
        for (int i=0 ; i< benefits.length; i++)
        {
            HashMap benefit = (HashMap)benefits[i];

            if(benefit.get("memberPlanId") != claim.getMemberPlanId())
                continue;

            TableRow tr = new TableRow(this);
            tr.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));


            TextView tdcol1 = new TextView(this);
            tdcol1.setText((String)benefit.get("benefitName"));
            tdcol1.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));

            EditText billed = new EditText(this);
            billed.setInputType(InputType.TYPE_CLASS_NUMBER);
            billed.setLayoutParams(new TableRow.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));


            tr.addView(tdcol1);
            tr.addView(billed);

            HashMap detail = new HashMap();
            detail.put( "benefitId", benefit.get("benefitId"));
            detail.put( "billed", billed);

            billedAmounts.add(detail);

            tl.addView(tr, new TableLayout.LayoutParams(TableLayout.LayoutParams.MATCH_PARENT, TableLayout.LayoutParams.WRAP_CONTENT));

        }
    }

    private  void showDiagnosisForm(){

    }

    public void onClickConfirm(View view){
        confirmUpdateClaim();
    }

    /**
     * update claim, add benefit billed, diagnosis
     * if success, continue with executing action_open
     */
    private void confirmUpdateClaim(){

        List data = Arrays.asList(
                Arrays.asList(claim.getId()),
                new HashMap() {{
                    List details = new ArrayList();
                    for(int i=0; i< billedAmounts.size(); i++)
                    {
                        final HashMap  bm = (HashMap ) billedAmounts.get(i);
                        final Integer benefitId = (Integer)bm.get("benefitId");
                        final EditText billed = (EditText)bm.get("billed");

                        details.add(Arrays.asList(0, 0, new HashMap() {{
                            put("benefit_id", benefitId);
                            put("billed", billed.getText().toString());
                            put("quantity", "1");
                        }}));
                    }

                    put("claim_no_revision", 100);
                    put("reference_no", "android");
                    put("claim_detail_ids",details);
                }}
        );
        updateClaimTaskId = odoo.update(listener, database, uid, password, "netpro.claim", data);

    }

    XMLRPCCallback listener = new XMLRPCCallback() {
        public void onResponse(long id, Object result) {

            Looper.prepare();

            if (id==updateClaimTaskId)
            {
                final Boolean updateResult =(Boolean)result;

                if(updateResult)
                {
                    Log.v("CLAIM UPDATE", "successfully");
                    List data = Arrays.asList( claim.getId() );
                    confirmClaimTaskId = odoo.exec(listener, database, uid, password, "netpro.claim", "action_open", data);
                }
                else{
                    odoo.MessageDialog(DischargeActivity.this, "Update claim failed. Server return was false");
                }

            }
            else if (id==confirmClaimTaskId)
            {
                final Boolean confirmResult =(Boolean)result;

                if(confirmResult){

                    Log.v("CLAIM CONFIRMED", "successfully");

                    AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(DischargeActivity.this);
                    alertDialogBuilder.setMessage("Successfully discharged Claim" )
                            .setCancelable(false)
                            .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                                @Override
                                public void onClick(DialogInterface dialog, int which) {
                                    dialog.dismiss();

                                    // Do stuff if user accepts
                                    finish();
                                    Intent myIntent = new Intent(DischargeActivity.this, DischargeActivity.class);
                                    myIntent.addFlags(Intent.FLAG_ACTIVITY_NO_ANIMATION);
                                    myIntent.putExtra("state", "open");
                                    myIntent.putExtra("member", member);
                                    myIntent.putExtra("claim", claim);
                                    DischargeActivity.this.startActivity(myIntent);

                                }
                            }).create().show();

                }
                else
                {
                    odoo.MessageDialog(DischargeActivity.this, "Confirm Claim failed. Result from server is false");
                }
            }
            Looper.loop();

        }
        public void onError(long id, XMLRPCException error) {
            Log.e("SEARCH ****", error.getMessage());
            odoo.MessageDialog(DischargeActivity.this, error.getMessage());

        }
        public void onServerError(long id, XMLRPCServerException error) {
            Log.e("SEARCH ****",error.getMessage());
            odoo.MessageDialog(DischargeActivity.this, error.getMessage());
        }
    };

    public void onClickPrint(View view){

        String printContent = "";
        printContent += "DISCHARGE\n";
        printContent += "Claim No      : " + claim.getClaimNo() + "\n";
        printContent += "Name          : " + member.getName() + "\n";
        printContent += "Class         : " + member.getClassName() + "\n";
        printContent += "Membership    : " + member.getMembershipName() + "\n";
        printContent += "Card No       : " + member.getCardNo() + "\n";
        printContent += "Date of Birth : " + member.getDateOfBirth() + "\n";
        printContent += "Gender        : " + member.getGenderName() + "\n";
        printContent += "Policy No     : " + member.getPolicyName() + "\n";
        printContent += "Policy Group  : " + member.getPolicyCategoryId() + "\n";
        printContent += "Policy Start  : " + member.getInsurancePeriodStart() + " to " + member.getInsurancePeriodEnd() + "\n";
        printContent += "Company       : " + member.getPolicyHolderName() + "\n";
        printContent += " \n";


        String col1 = "%-20s";
        String col2 = "%-5s";
        String col3 = "%-10s";
        String col4 = "%-10s";
        printContent += String.format(col1, "Benefit");
        //printContent += String.format(col2, "Unit");
        //printContent += String.format(col3, "Usage");
        printContent += String.format(col4, "Billed");
        printContent += " \n";

        Double total = 0.0;
        Double limit = 0.0;
        Double excess = 0.0;

        Object[] benefits = member.getBenefits();
        //for(int i=0; i< billedAmounts.size(); i++)
        for (int i=0 ; i< benefits.length; i++)
        {
            HashMap benefit = (HashMap)benefits[i];
            String benefitName= (String)benefit.get("benefitName");
            Double remaining = (Double)benefit.get("remaining");

            //final HashMap  bm = (HashMap ) billedAmounts.get(i);
            //final Integer benefitId = (Integer)bm.get("benefitId");
            //final EditText billed = (EditText)bm.get("billed");

            printContent += String.format(col1, benefitName);
            printContent += String.format(col4, "" );
            printContent +=  " \n";

            //total += Double.parseDouble(billed.getText().toString());
            //limit += remaining;
        }
        printContent += "-----------------------------\n";
        printContent += String.format(col1, "TOTAL");
        printContent += String.format(col4, total );
        printContent +=  " \n";

        printContent += String.format(col1, "EXCESS");
        printContent += String.format(col4, limit - total );
        printContent +=  " \n";


        printContent += "Print Date:" + new SimpleDateFormat("dd-MM-yyyy").format(new Date());
        printContent += " \n";
        printContent += " \n";
        printContent += " \n";
        printContent += " \n";
        printContent += " \n";
        printContent += " \n";
        printContent += "(..........................)\n";
        printContent += "         Signature\n";
        printContent += " \n";
        printContent += " \n";
        printContent += " \n";
        printContent += " \n";
        printContent += " \n";

        handler.leftDistance = 0;
        handler.lineDistance = 0;
        handler.printContent = printContent;
        handler.wordFont = 2;
        handler.printGray = 20;

        if (LowBattery == true) {
            handler.sendMessage(handler.obtainMessage(handler.LOWBATTERY, 1, 0, null));
        } else {
            if(!nopaper) {
                //setTitle("print character");
                progressDialog = ProgressDialog.show(DischargeActivity.this, getString(R.string.bl_dy), getString(R.string.printing_wait));
                handler.progressDialog = progressDialog;
                handler.sendMessage(handler.obtainMessage(handler.PRINTCONTENT, 1, 0, null));
            }
            else {
                Toast.makeText(DischargeActivity.this, getString(R.string.ptintInit), Toast.LENGTH_LONG).show();
            }
        }

    }

    protected void onDestroy() {
        if(progressDialog != null && !DischargeActivity.this.isFinishing() ){
            progressDialog.dismiss();
            progressDialog = null;
        }
        //        stop = true;
        unregisterReceiver(printReceive);
        ThermalPrinter.stop();
        super.onDestroy();
    }

    private BroadcastReceiver printReceive = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent)
        {
            String action = intent.getAction();
            if (action.equals(Intent.ACTION_BATTERY_CHANGED)) {
                int status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, BatteryManager.BATTERY_STATUS_NOT_CHARGING);
                int level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, 0);
                int scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, 0);
                if (status != BatteryManager.BATTERY_STATUS_CHARGING) {
                    if (level * 5 <= scale) {
                        LowBattery = true;
                    } else {
                        LowBattery = false;
                    }
                } else {
                    LowBattery = false;
                }
            }
        }
    };


}
