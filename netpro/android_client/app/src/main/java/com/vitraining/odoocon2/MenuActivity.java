package com.vitraining.odoocon2;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

public class MenuActivity extends AppCompatActivity {

    TextView txtStatus;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.layout_menu);

    }

    @Override
    public void onResume(){
        super.onResume();

        // put your code here...
        String username = SharedData.getKey(MenuActivity.this, "username");
        String database = SharedData.getKey(MenuActivity.this, "database");
        String serverAddress = SharedData.getKey(MenuActivity.this, "serverAddress");

        txtStatus = (TextView) findViewById(R.id.txtStatus);
        txtStatus.setText("Username: " + username + "\n" +
                        "Database : " + database + "\n" +
                        "Server Address : " + serverAddress
        );

    }

    public void onClickRegistration(View view){
        SharedData.setKey(MenuActivity.this, "operation", "registration");
        Intent myIntent = new Intent(MenuActivity.this, SearchActivity.class);
        MenuActivity.this.startActivity(myIntent);
    }

    public void onClickDischarge(View view){
        SharedData.setKey(MenuActivity.this, "operation", "discharge");
        Intent myIntent = new Intent(MenuActivity.this, SearchActivity.class);
        MenuActivity.this.startActivity(myIntent);
    }

    public void onClickVoid(View view){
        SharedData.setKey(MenuActivity.this, "operation", "void");
        Intent myIntent = new Intent(MenuActivity.this, SearchActivity.class);
        MenuActivity.this.startActivity(myIntent);
    }
}
