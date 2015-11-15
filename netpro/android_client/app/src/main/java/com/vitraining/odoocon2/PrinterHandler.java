package com.vitraining.odoocon2;

import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.DialogInterface;
import android.os.Message;
import android.widget.Toast;
import android.content.*;
import android.os.BatteryManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.util.Log;

import com.telpo.tps550.api.printer.ThermalPrinter;

/**
 * Created by akhmaddanielsembiring on 10/30/15.
 */
public class PrinterHandler extends  Handler{
    public final int ENABLE_BUTTON = 2;
    public final int NOPAPER = 3;
    public final int LOWBATTERY=4;
    public final int PRINTVERSION=5;
    public final int PRINTBARCODE = 6;
    public final int PRINTQRCODE = 7;
    public final int PRINTPAPERWALK = 8;
    public final int PRINTCONTENT = 9;
    public final int CANCELPROMPT=10;
    public final int PRINTERR = 11;
    public final int OVERHEAT = 12;
    public final int MAKER = 13;
    public final int PRINTPICTURE=14;
    public final int EXECUTECOMMAND=15;

    private boolean stop = false;
    private static final String TAG = "ConsoleTestActivity";

    private Context context;
    public static String barcodeStr;
    public static String qrcodeStr;
    public static int paperWalk;
    public static String printContent;
    public int leftDistance = 0;
    public int lineDistance;
    public int wordFont;
    public int printGray;

    private String Result;
    private Boolean nopaper = false;

    public ProgressDialog progressDialog;

    public PrinterHandler(Context context){
        this.context = context;
    }

    private void noPaperDlg() {
        AlertDialog.Builder dlg = new AlertDialog.Builder(context);
        dlg.setTitle(context.getString(R.string.noPaper));
        dlg.setMessage(context.getString(R.string.noPaperNotice));
        dlg.setPositiveButton(R.string.sure, new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialogInterface, int i) {

            }
        });
        dlg.show();
    }

    public void handleMessage(Message msg) {
        if (stop == true)
            return;
        switch (msg.what) {
            case NOPAPER:
                noPaperDlg();
                break;
            case LOWBATTERY:
                AlertDialog.Builder alertDialog = new AlertDialog.Builder(context);
                alertDialog.setTitle(R.string.operation_result);
                alertDialog.setMessage(context.getString(R.string.LowBattery));
                alertDialog.setPositiveButton(context.getString(R.string.dlg_ok), new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialogInterface, int i) {
                    }
                });
                alertDialog.show();
                break;
            case PRINTCONTENT:
                new contentPrintThread().start();
                break;

            case EXECUTECOMMAND:
                new executeCommand().start();
                break;
            case CANCELPROMPT:
                if(progressDialog != null  ){
                    progressDialog.dismiss();
                    progressDialog = null;
                }
                break;
            case OVERHEAT:
                AlertDialog.Builder overHeatDialog = new AlertDialog.Builder(context);
                overHeatDialog.setTitle(R.string.operation_result);
                overHeatDialog.setMessage(context.getString(R.string.overTemp));
                overHeatDialog.setPositiveButton(context.getString(R.string.dlg_ok), new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialogInterface, int i) {
                    }
                });
                overHeatDialog.show();
                break;
            default:
                Toast.makeText(context,"Print Error! " + msg.what ,Toast.LENGTH_LONG).show();
                break;
        }
    }


    private class contentPrintThread extends Thread{
        public void run(){
            super.run();
            setName("Content Print Thread");
            try {
                ThermalPrinter.start();
                ThermalPrinter.reset();
                ThermalPrinter.setAlgin(ThermalPrinter.ALGIN_LEFT);
                ThermalPrinter.setLeftIndent(leftDistance);
                ThermalPrinter.setLineSpace(lineDistance);
                if(wordFont == 3){
                    ThermalPrinter.setFontSize(2);
                    ThermalPrinter.enlargeFontSize(2,2);
                }else{
                    ThermalPrinter.setFontSize(wordFont);
                }
                ThermalPrinter.setGray(printGray);
                ThermalPrinter.addString(printContent);
                ThermalPrinter.printString();
                ThermalPrinter.clearString();
                ThermalPrinter.walkPaper(20);
            }catch (Exception e){
                e.printStackTrace();
                Result = e.toString();
                if (Result.equals("com.telpo.tps550.api.printer.NoPaperException")){
                    nopaper = true;
//                    return;
                }else if (Result.equals("com.telpo.tps550.api.printer.OverHeatException")) {
                    sendMessage( obtainMessage(OVERHEAT, 1, 0, null));
                }else {
                    sendMessage( obtainMessage(PRINTERR, 1, 0, null));
                }
            }finally {
                //lock.release();
                sendMessage(obtainMessage(CANCELPROMPT, 1, 0, null));
                if(nopaper)
                    sendMessage(obtainMessage(NOPAPER, 1, 0, null));
                ThermalPrinter.stop();
                nopaper=false;
//                PrinterActivity.this.sleep(1500);
//                if(progressDialog != null && !PrinterActivity.this.isFinishing() ){
//                    progressDialog.dismiss();
//                    progressDialog = null;
//                }
                Log.v(TAG,"The Print Progress End !!!");
//                if(isClose) {
////                    onDestroy();
//                    finish();
//                }
            }
//            handler.sendMessage(handler
//                    .obtainMessage(ENABLE_BUTTON, 1, 0, null));
        }
    }

    private class executeCommand extends Thread{

        @Override
        public void run() {
            super.run();
            setName("ExecuteCommand Thread");
            try{
                ThermalPrinter.start();
                ThermalPrinter.reset();
//                ThermalPrinter.sendCommand(edittext_input_command.getText().toString());
            }catch(Exception e){
                e.printStackTrace();
                Result = e.toString();
                if (Result.equals("com.telpo.tps550.api.printer.NoPaperException")){
                    nopaper = true;
//                    return;
                }else if (Result.equals("com.telpo.tps550.api.printer.OverHeatException"))
                {
                    sendMessage(obtainMessage(OVERHEAT, 1, 0, null));
                }else
                {
                    sendMessage(obtainMessage(PRINTERR, 1, 0, null));
                }
            }finally{
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                sendMessage(obtainMessage(CANCELPROMPT, 1, 0, null));
                if(nopaper)
                    sendMessage(obtainMessage(NOPAPER, 1, 0, null));
                ThermalPrinter.stop();
                nopaper=false;
//                PrinterActivity.this.sleep(1500);
//                if(progressDialog != null && !PrinterActivity.this.isFinishing() ){
//                    progressDialog.dismiss();
//                    progressDialog = null;
//                }
                Log.v(TAG,"The ExecuteCommand Progress End !!!");
//                if(isClose) {
//                    finish();
//                }
            }
        }

    }



}
