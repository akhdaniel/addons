package com.vitraining.odoocon2;

import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Looper;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.EditText;

import de.timroes.axmlrpc.XMLRPCCallback;
import de.timroes.axmlrpc.XMLRPCException;
import de.timroes.axmlrpc.XMLRPCServerException;

public class LoginActivity extends AppCompatActivity {

    private long loginTaskId;

    EditText txtUsername;
    EditText txtPassword;
    EditText txtDatabase;
    EditText txtServerAddress;
    EditText txtTID;


    AlertDialog.Builder alertDialogBuilder;
    AlertDialog alertDialog;

    /*********************************************************************************************
     *
     * @param savedInstanceState
     *********************************************************************************************/
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        String database = SharedData.getKey(LoginActivity.this, "database");
        String serverAddress = SharedData.getKey(LoginActivity.this, "serverAddress");
        String tid = SharedData.getKey(LoginActivity.this, "tid");

        txtDatabase = (EditText) findViewById(R.id.txtDatabase);
        txtServerAddress = (EditText) findViewById(R.id.txtServerAddress);
        txtTID = (EditText) findViewById(R.id.txtTID);

        txtDatabase.setText(database);
        txtServerAddress.setText(serverAddress);
        txtTID.setText(tid);

        alertDialogBuilder = new AlertDialog.Builder(this  );

    }

    /**********************************************************************************************
     *
     * @param view
     *********************************************************************************************/

    public void  onClick(View view){
        switch (view.getId()) {
            case R.id.btnLogin:
                txtUsername = (EditText) findViewById(R.id.txtUsername);
                txtPassword = (EditText) findViewById(R.id.txtPassword);
                txtDatabase = (EditText) findViewById(R.id.txtDatabase);
                txtServerAddress = (EditText) findViewById(R.id.txtServerAddress);
                txtTID = (EditText) findViewById(R.id.txtTID);

                String password = txtPassword.getText().toString();
                String username = txtUsername.getText().toString();
                String database = txtDatabase.getText().toString();
                String serverAddress = txtServerAddress.getText().toString();
                String tid = txtTID.getText().toString();

                OdooUtility odoo = new OdooUtility(serverAddress, "common");
                loginTaskId = odoo.login(listener, database, username, password);

                SharedData.setKey(LoginActivity.this, "password", password);
                SharedData.setKey(LoginActivity.this, "username", username);
                SharedData.setKey(LoginActivity.this, "database", database);
                SharedData.setKey(LoginActivity.this, "serverAddress", serverAddress);
                SharedData.setKey(LoginActivity.this, "tid", tid);

                break;
        }
    }

    /**********************************************************************************************
     * the callback listener
     *********************************************************************************************/
    XMLRPCCallback listener = new XMLRPCCallback() {
        public void onResponse(long id, Object result) {
            /*
            looper supaya bisa akses UI component dari thread ini
             */
            Looper.prepare();
            if (id == loginTaskId){
                if ( result instanceof Boolean && (Boolean)result == false){
                    alertDialogBuilder.setMessage("Login Error. Please try again");
                    alertDialog = alertDialogBuilder.create();
                    alertDialog.show();
                }
                else
                {
                    /*
                    open main menu activity
                    send the uid
                    */
                    String uid = result.toString();
                    SharedData.setKey(LoginActivity.this, "uid", uid);

//                    String username = SharedData.getKey(LoginActivity.this, "username");
//                    String database = SharedData.getKey(LoginActivity.this, "database");
//                    String serverAddress = SharedData.getKey(LoginActivity.this, "serverAddress");

                    // use this to start and trigger a service
                    Intent myIntent = new Intent(LoginActivity.this, MenuActivity.class);
//                    myIntent.putExtra("username", username);
//                    myIntent.putExtra("database", database);
//                    myIntent.putExtra("serverAddress", serverAddress);

                    LoginActivity.this.startActivity(myIntent);

                }
            }
            Looper.loop();
        }

        public void onError(long id, XMLRPCException error) {
            // Handling any error in the library
            Looper.prepare();
            Log.e("LOGIN****", error.getMessage());
            alertDialogBuilder.setMessage("Login Error. " + error.getMessage());
            alertDialog = alertDialogBuilder.create();
            alertDialog.show();
            Looper.loop();
        }

        public void onServerError(long id, XMLRPCServerException error) {
            // Handling an error response from the server
            Looper.prepare();
            Log.e("LOGIN****", error.getMessage());
            alertDialogBuilder.setMessage("Login Error. "+ error.getMessage());
            alertDialog = alertDialogBuilder.create();
            alertDialog.show();
            Looper.loop();
        }
    };


    public void onTestMagnetid(View view){
        Intent intent = new Intent(LoginActivity.this, PrinterActivity.class);
//        Intent intent = new Intent(LoginActivity.this, MegneticActivity.class);
        startActivity(intent);
    }

}
