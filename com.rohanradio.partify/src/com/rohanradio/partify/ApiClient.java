package com.rohanradio.partify;

import java.io.IOException;
import java.io.UnsupportedEncodingException;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONException;
import org.json.JSONObject;

import android.location.Location;

public class ApiClient {
	public static final String API_URL = "http://localhost:8855/api/";
	
	public ApiClient() {
	}
	
	public void setLocation(Location location) {
		JSONObject locationJson = new JSONObject();
		
		try {
			locationJson.put("lat", location.getLatitude());
			locationJson.put("long", location.getLongitude());
			locationJson.put("accuracy", location.getAccuracy());
		} catch (JSONException e) {
			e.printStackTrace();
		}
		
		
		HttpClient client = new DefaultHttpClient();
		
		HttpPost post = new HttpPost(API_URL + "setLocation");
		post.setHeader("Content-Type", "application/json");

		StringEntity entity = null;
		try {
			entity = new StringEntity(locationJson.toString());
			entity.setContentType(post.getFirstHeader("Content-Type"));
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
		}
		
		post.setEntity(entity);
		
		try {
			HttpResponse response = client.execute(post);
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
