package com.vitraining.odoocon2;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * Created by akhmaddanielsembiring on 10/8/15.
 */
public class SharedData {
    private static final String MyPREFERENCES = "MyPrefs" ;
    private static SharedPreferences sharedpreferences;

    public static String getKey(Context c, String key){
        sharedpreferences = c.getSharedPreferences(MyPREFERENCES, Context.MODE_PRIVATE);
        return sharedpreferences.getString(key, "");
    }

    public static void setKey(Context c, String key, String value){
        sharedpreferences = c.getSharedPreferences(MyPREFERENCES, Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedpreferences.edit();
        editor.putString(key, value);
        editor.commit();
    }
}
