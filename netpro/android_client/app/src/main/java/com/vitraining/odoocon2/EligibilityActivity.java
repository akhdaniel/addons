package com.vitraining.odoocon2;

import android.content.DialogInterface;
import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import de.timroes.axmlrpc.XMLRPCCallback;
import de.timroes.axmlrpc.XMLRPCException;
import de.timroes.axmlrpc.XMLRPCServerException;

public class EligibilityActivity extends AppCompatActivity {
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

    Member member;
    Integer memberPlanId;
    long memberPlanDetailTaskId;
    private OdooUtility odoo;
    private String uid;
    private String password;
    private String serverAddress;
    private String database;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_eligibility);

        Intent intent = getIntent();
        member = (Member) intent.getParcelableExtra("member");

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


        //        Object[] coverages = member.getCoverages();
        //        ViewGroup linearLayout = (ViewGroup) findViewById(R.id.linearLayout);
        //        for (int i=0 ; i< coverages.length; i++)
        Object[] memberPlanIds = member.getMemberPlanIds();
        ViewGroup linearLayout = (ViewGroup) findViewById(R.id.linearLayout);
        for (int i=0 ; i< memberPlanIds.length; i++)
        {
            HashMap memberPlan = (HashMap)memberPlanIds[i];
            Button bt = new Button(this);
            bt.setText((String) memberPlan.get("planScheduleName"));
            bt.setTag( memberPlan.get("id"));
            bt.setLayoutParams(new ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT));
            bt.setOnClickListener(onClickListener);
            linearLayout.addView(bt);
        }


        uid = SharedData.getKey(EligibilityActivity.this, "uid");
        password = SharedData.getKey(EligibilityActivity.this, "password");
        serverAddress = SharedData.getKey(EligibilityActivity.this, "serverAddress");
        database = SharedData.getKey(EligibilityActivity.this, "database");
        odoo = new OdooUtility(serverAddress, "object");

    }

    View.OnClickListener onClickListener = new View.OnClickListener(){

        @Override
        public void onClick(View view) {
            memberPlanId =  (Integer) view.getTag();
            Button b = (Button)view;
            String memberPlan =  (String) b.getText().toString();

            Intent myIntent = new Intent(EligibilityActivity.this, RegistrationActivity.class);
            myIntent.putExtra("member", member);
            myIntent.putExtra("memberPlanId", memberPlanId);
            myIntent.putExtra("memberPlan", memberPlan);

            EligibilityActivity.this.startActivity(myIntent);

        }
    };



}
