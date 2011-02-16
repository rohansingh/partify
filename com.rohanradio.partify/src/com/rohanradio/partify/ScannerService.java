package com.rohanradio.partify;

import java.util.ArrayList;
import java.util.List;

import android.content.ContentResolver;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.location.Location;
import android.location.LocationManager;
import android.net.Uri;
import android.provider.MediaStore;

import com.commonsware.cwac.wakeful.WakefulIntentService;

public class ScannerService extends WakefulIntentService {

	public static final String TAG = "com.rohanradio.partify.ScannerService";
	
	public ScannerService(String name) {
		super(TAG);
	}
	
	@Override
	protected void doWakefulWork(Intent intent) {
		LocationManager locationManager = (LocationManager)this.getSystemService(Context.LOCATION_SERVICE);
		Location location = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
		
		if (location == null) {
			return;
		}

		List<Track> tracks = this.getTracks();
		
		ApiClient client = new ApiClient();
		client.setLocation(location);
	}
	
	private List<Track> getTracks() {
		
		Uri mediaUri = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI;
		ContentResolver resolver = this.getContentResolver();
		
		String artistColumn = MediaStore.Audio.ArtistColumns.ARTIST;
		String titleColumn = MediaStore.MediaColumns.TITLE;
		
		Cursor cursor = resolver.query(mediaUri, new String[] { artistColumn, titleColumn},
			null, null, null);
		
		List<Track> tracks = new ArrayList<Track>(cursor.getCount());
		
		if (cursor.moveToFirst()) {
			int artistIndex = cursor.getColumnIndex(artistColumn);
			int titleIndex = cursor.getColumnIndex(titleColumn);
			
			do {
				String artist = cursor.getString(artistIndex);
				String title = cursor.getString(titleIndex);
				
				tracks.add(new Track(artist, title));
			} while (cursor.moveToNext());
		}
		
		return tracks;
	}

}
